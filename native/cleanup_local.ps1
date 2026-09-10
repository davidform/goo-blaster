param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$privateRoot = Join-Path $repo '_private'
$mobile = Join-Path $privateRoot 'mobile-test'
$latest = Get-Content -LiteralPath (Join-Path $mobile 'latest.json') -Raw | ConvertFrom-Json
$published = Get-Content -LiteralPath (Join-Path $mobile 'published.json') -Raw | ConvertFrom-Json
if (!$published.public_download_verified -or $latest.build -ne $published.build -or $latest.apk_sha256 -ne $published.apk_sha256) { throw 'Current release must be verified first' }
if ((Get-FileHash -LiteralPath (Join-Path $repo 'index.html') -Algorithm SHA256).Hash.ToLower() -ne $latest.game_sha256) { throw 'Working game has unpublished changes' }
if ((Get-FileHash -LiteralPath $latest.apk_path -Algorithm SHA256).Hash.ToLower() -ne $latest.apk_sha256) { throw 'APK hash mismatch' }
# Fail closed while browser tests or Android builds may still use temporary files.
$busy = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -and $_.Name -match '^(python|node|java).*' -and $_.CommandLine -match '(run_tests\.py|tests[/\\]py_|tests[/\\]test\d|GradleDaemon)' }
if ($busy) { throw 'Tests/builds are still running; finish them before cleanup' }
$apks = @(Get-ChildItem -LiteralPath $mobile -File | Where-Object { $_.Name -match '^goo-blaster-v\d+\.\d+\.\d+-(\d+)\.apk$' } | Sort-Object { [int64]([regex]::Match($_.Name,'-(\d+)\.apk$').Groups[1].Value) } -Descending)
if (!$apks.Count -or $apks[0].FullName -ne [IO.Path]::GetFullPath($latest.apk_path)) { throw 'Unexpected newest APK' }
$targets = @($apks | Select-Object -Skip 2)
$targets += @(Get-ChildItem -LiteralPath (Join-Path $privateRoot 'test-artifacts') -Directory | Where-Object { $_.Name -match '^(release-profile-|range-profile-)' })
# Validate ALL absolute paths and reject junctions before deleting anything.
$skipped = @()
$validated = @()
foreach ($target in $targets) {
    $resolved = [IO.Path]::GetFullPath($target.FullName)
    if (!$resolved.StartsWith($privateRoot + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Path outside project private directory' }
    $chain = $target
    while ($chain -and $chain.FullName -ne $repo) {
        if ($chain.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse point rejected' }
        $chain = if ($chain.PSIsContainer) { $chain.Parent } else { $chain.Directory }
    }
    try {
        if ($target.PSIsContainer -and (Get-ChildItem -LiteralPath $resolved -Recurse -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })) { throw 'Nested reparse point rejected' }
        $validated += $target
    } catch {
        if ($_.CategoryInfo.Category -ne 'PermissionDenied') { throw }
        $skipped += [pscustomobject]@{path=$resolved;reason='Access denied; left unchanged'}
    }
}
$targets = $validated
$items = @($targets | ForEach-Object {
    $size = if ($_.PSIsContainer) { (Get-ChildItem -LiteralPath $_.FullName -File -Recurse -Force | Measure-Object Length -Sum).Sum } else { $_.Length }
    [pscustomobject]@{path=$_.FullName;bytes=[int64]$size}
})
$report = [ordered]@{applied=[bool]$Apply;build=$latest.build;kept_apks=@($apks|Select-Object -First 2 -ExpandProperty Name);items=$items;bytes=($items|Measure-Object bytes -Sum).Sum;skipped=$skipped}
$receipt = Join-Path $mobile ('cleanup-local-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
$report['removed'] = @()
$report['failed'] = @()
$report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt -Encoding utf8
if ($Apply) {
    foreach ($target in $targets) {
        try {
            Remove-Item -LiteralPath $target.FullName -Recurse -Force
            $report['removed'] += $target.FullName
        } catch { $report['failed'] += [pscustomobject]@{path=$target.FullName;reason=$_.Exception.Message} }
        $report | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $receipt -Encoding utf8
    }
}
$report | ConvertTo-Json -Depth 5
if ($report['failed'].Count) { exit 1 }
