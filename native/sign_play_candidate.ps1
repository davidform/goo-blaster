param([switch]$CreateUploadKey)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$out = Join-Path $repo '_private/play-preparation'
$candidate = Get-Content -LiteralPath (Join-Path $out 'candidate.json') -Raw | ConvertFrom-Json
$unsigned = [IO.Path]::GetFullPath($candidate.aab_path)
if (!$unsigned.StartsWith($out + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Candidate must be inside private preparation directory' }
if ((Get-FileHash -LiteralPath $unsigned -Algorithm SHA256).Hash.ToLower() -ne $candidate.aab_sha256) { throw 'Candidate hash changed' }
if ((Get-FileHash -LiteralPath (Join-Path $repo 'index.html') -Algorithm SHA256).Hash.ToLower() -ne $candidate.game_sha256) { throw 'Game source changed' }
$signed = Join-Path $out ($candidate.build + '-' + $candidate.version_code + '-play-signed.aab')
if (Test-Path -LiteralPath $signed) { throw 'Signed artifact exists; audit instead of overwriting' }
$keyDir = Join-Path $env:USERPROFILE '.goo-blaster-signing'
$keystore = Join-Path $keyDir 'upload.p12'
$passwordFile = Join-Path $keyDir 'upload-password.dpapi'
$cert = Join-Path $keyDir 'upload-certificate.pem'
$jdk = Join-Path $env:USERPROFILE '.jdks/jbr-21.0.11/bin'
$alias = 'goo-upload'
if (!(Test-Path -LiteralPath $keystore)) {
    if (!$CreateUploadKey) { throw 'Explicit -CreateUploadKey authorization required for first use' }
    if (Test-Path -LiteralPath $keyDir) { throw 'Existing key directory; inspect without overwriting' }
    New-Item -ItemType Directory -Path $keyDir | Out-Null
    $sid = [Security.Principal.WindowsIdentity]::GetCurrent().User
    $acl = [Security.AccessControl.DirectorySecurity]::new()
    $acl.SetOwner($sid)
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($principal in @($sid, [Security.Principal.SecurityIdentifier]::new('S-1-5-18'))) {
        $acl.AddAccessRule([Security.AccessControl.FileSystemAccessRule]::new($principal, 'FullControl', 'ContainerInherit,ObjectInherit', 'None', 'Allow'))
    }
    Set-Acl -LiteralPath $keyDir -AclObject $acl
    $random = [byte[]]::new(32)
    [Security.Cryptography.RandomNumberGenerator]::Fill($random)
    $secret = ConvertTo-SecureString ([Convert]::ToBase64String($random)) -AsPlainText -Force
    ConvertFrom-SecureString $secret | Set-Content -LiteralPath $passwordFile -Encoding ascii
    [Array]::Clear($random,0,$random.Length)
} else {
    if ($CreateUploadKey) { throw 'Upload key already exists; never replace it' }
    $secret = (Get-Content -LiteralPath $passwordFile -Raw).Trim() | ConvertTo-SecureString
}
# The password is never printed, stored in the repository, or placed in process arguments.
# DPAPI protects the stored password for this Windows user. Off-device recovery backup is still required.
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secret)
try {
    $env:GOO_UPLOAD_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr)
    if (!(Test-Path -LiteralPath $keystore)) {
        & "$jdk/keytool.exe" -genkeypair -keystore $keystore -storetype PKCS12 -alias $alias -keyalg RSA -keysize 3072 -sigalg SHA256withRSA -validity 10000 -dname 'CN=DemjaStudio Upload, O=DemjaStudio' -storepass:env GOO_UPLOAD_PASSWORD -keypass:env GOO_UPLOAD_PASSWORD 2>&1 | Set-Content (Join-Path $out 'upload-key-generation.log')
        if ($LASTEXITCODE -ne 0) { throw 'keytool generation failed; inspect log, do not regenerate blindly' }
    }
    & "$jdk/keytool.exe" -exportcert -rfc -keystore $keystore -storetype PKCS12 -alias $alias -storepass:env GOO_UPLOAD_PASSWORD -file $cert 2>&1 | Set-Content (Join-Path $out 'upload-certificate-export.log')
    if ($LASTEXITCODE -ne 0) { throw 'Certificate export failed' }
    & "$jdk/jarsigner.exe" -keystore $keystore -storetype PKCS12 -storepass:env GOO_UPLOAD_PASSWORD -keypass:env GOO_UPLOAD_PASSWORD -sigalg SHA256withRSA -digestalg SHA-256 -signedjar $signed $unsigned $alias 2>&1 | Set-Content (Join-Path $out 'aab-signing.log')
    if ($LASTEXITCODE -ne 0) { throw 'Signing failed' }
    & "$jdk/jarsigner.exe" -verify -strict -verbose -certs -keystore $keystore -storetype PKCS12 -storepass:env GOO_UPLOAD_PASSWORD $signed $alias 2>&1 | Set-Content (Join-Path $out 'aab-signature-verification.log')
    if ($LASTEXITCODE -ne 0) { throw 'Strict signature verification failed' }
    & "$jdk/keytool.exe" '-J-Duser.language=en' '-J-Duser.country=US' -printcert -jarfile $signed 2>&1 | Set-Content (Join-Path $out 'aab-signer-certificate.log')
    if ($LASTEXITCODE -ne 0) { throw 'Signer certificate inspection failed' }
    Write-Output "Signed and strictly verified: $signed"
    Write-Output "Key directory (not backed up externally): $keyDir"
} finally {
    Remove-Item Env:GOO_UPLOAD_PASSWORD -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr)
    $secret.Dispose()
}
