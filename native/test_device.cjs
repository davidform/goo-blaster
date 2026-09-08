// Test only the newly installed debug package, preserving its actual saved progress.
// NODE_PATH must point to the development Playwright installation.
// Usage: node native/test_device.cjs <adb-device-serial>
const { _android } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const app = 'com.demjastudio.gooblaster';
const out = path.resolve(__dirname, '../_private/test-artifacts');
fs.mkdirSync(out, {recursive:true});
(async()=>{
  const devices = await _android.devices();
  const device = devices.find(d=>d.serial() === process.argv[2]);
  assert(device, 'Requested test device must be connected');
  try {
    const airplane = (await device.shell('settings get global airplane_mode_on')).toString().trim();
    const wifi = (await device.shell('cmd wifi status')).toString().split('\n')[0].trim();
    assert.equal(airplane, '1', 'Enable airplane mode for the offline test');
    assert.equal(wifi, 'Wifi is disabled', 'Turn Wi-Fi off for the offline test');
    const connect = async()=>{
      await device.shell('am start -W -n ' + app + '/.MainActivity');
      const view = await device.webView({pkg:app}, {timeout:60000});
      const page = await view.page();
      await page.waitForFunction('typeof NATIVE_READY !== "undefined" && NATIVE_READY');
      return page;
    };
    const read = page=>page.evaluate(()=>({build:BUILD,progress:PROGRESS,coins:COINS,meta:META,lang:LANG,selection:SEL_IDX}));
    let page = await connect();
    const before = await read(page);
    await page.evaluate(()=>saveGame());
    await page.waitForFunction(async()=>{
      const r=await Capacitor.Plugins.Preferences.get({key:PROG_KEY});
      if(!r.value) return false;
      const data=JSON.parse(r.value);
      return data.progress===PROGRESS && data.coins===COINS && JSON.stringify(data.meta)===JSON.stringify(META);
    });
    const nativeSaved = await page.evaluate(async()=>JSON.parse((await Capacitor.Plugins.Preferences.get({key:PROG_KEY})).value));
    // No uninstall, no data clearing, no fabricated coins/progress.
    await device.shell('am force-stop ' + app);
    page = await connect();
    const after = await read(page);
    assert.deepEqual(after, before, 'Actual save must survive a cold offline restart');
    const errors=[], external=[];
    page.on('pageerror', e=>errors.push(String(e)));
    page.on('request', r=>{
      if(/^https?:/.test(r.url()) && new URL(r.url()).hostname!=='localhost') external.push(r.url());
    });
    await page.screenshot({path:path.join(out,'android-offline-restored.png')});
    await page.click('#btnPlay');
    await page.waitForFunction('G.running');
    await page.screenshot({path:path.join(out,'android-offline-play.png')});
    assert.deepEqual(errors, []);
    assert.deepEqual(external, []);
    const report={airplane,wifi,before,nativeSaved,after,errors,external_requests_during_observed_play:external};
    fs.writeFileSync(path.join(out,'android-device.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report,null,2));
    console.log('PASS actual Preferences save, cold restart and launch while offline. Debug APK only.');
  } finally { await device.close(); }
})().catch(e=>{console.error(e);process.exitCode=1});
