"""Render actual SFX instruments offline for listening and signal diagnostics.

Injects a scheduling hook into a disposable copy; never edits the game file.
"""
import argparse
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import wave
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--label',default='audio-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
parser.add_argument('--source',default=str(root/'index.html'))
args=parser.parse_args()
out=root/'_private/test-artifacts'/args.label
out.mkdir(parents=True,exist_ok=True)
source=Path(args.source).read_text(encoding='utf-8')
marker='    unlock, isMuted:()=>muted,'
assert source.count(marker)==1
instrumented=source.replace(marker,'''    __scheduleTest(){
      clearInterval(M.timer); musBus.gain.cancelScheduledValues(0);musBus.gain.setValueAtTime(1,0);
      for(let i=0;i<64;i++)playStep(i,.1+i*stepDur());
    },
'''+marker)
(out/'probe.html').write_text(instrumented,encoding='utf-8')
report={'source_sha256':hashlib.sha256(Path(args.source).read_bytes()).hexdigest(),'samples':{},'diagnostic_only':True}
with sync_playwright() as pw:
    browser=pw.chromium.launch(channel=os.environ.get('GOO_BROWSER_CHANNEL','msedge'))
    for mode in ['cute','boss','bubble','graffiti','yoyo','hurt','mix']:
        seconds=12 if mode in ['cute','boss','mix'] else 2
        page=browser.new_page()
        errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
        page.add_init_script('''(()=>{
          window.__clock=0;window.__voices={osc:0,noise:0};
          let seed=12345;Math.random=()=>((seed=(Math.imul(seed,1664525)+1013904223)>>>0)/4294967296);
          window.AudioContext=function(){
            const c=new OfflineAudioContext(2,48000*SECONDS,48000);
            window.__offline=c;c.resume=()=>Promise.resolve();
            Object.defineProperty(c,'currentTime',{get:()=>window.__clock});
            const osc=c.createOscillator.bind(c),noise=c.createBufferSource.bind(c);
            c.createOscillator=()=>{__voices.osc++;return osc();};
            c.createBufferSource=()=>{__voices.noise++;return noise();};
            return c;
          };
          window.requestAnimationFrame=()=>0;
        })();'''.replace('SECONDS',str(seconds)))
        page.goto((out/'probe.html').as_uri())
        signal=page.evaluate('''async mode=>{
          if(['cute','boss','mix'].includes(mode)){
            SFX.musicStart();SFX.musicIntensity(mode==='boss'?1:0);SFX.__scheduleTest();
          }else SFX.unlock();
          if(['bubble','graffiti','yoyo','hurt'].includes(mode)){
            for(let i=0;i<4;i++){__clock=.1+i*.42;mode==='hurt'?SFX.hurt():SFX.shoot(mode);}
          }
          if(mode==='mix')for(let i=0;i<120;i++){
            __clock=.1+i/15;SFX.shoot(['bubble','graffiti','yoyo'][i%3]);SFX.hit();
            if(i%2===0)SFX.pickup();if(i===60)SFX.hurt();
          }
          const debug=SFX.musicDebug(),buffer=await __offline.startRendering();
          const channels=[buffer.getChannelData(0),buffer.getChannelData(1)];
          const bytes=new Uint8Array(buffer.length*4),view=new DataView(bytes.buffer);
          let peak=0,energy=0,clipped=0,nonfinite=0;
          for(let i=0;i<buffer.length;i++)for(let c=0;c<2;c++){
            const x=channels[c][i];if(!Number.isFinite(x))nonfinite++;
            peak=Math.max(peak,Math.abs(x));energy+=x*x;if(Math.abs(x)>=1)clipped++;
            view.setInt16((i*2+c)*2,Math.round(Math.max(-1,Math.min(1,x))*32767),true);
          }
          let chunks=[];for(let i=0;i<bytes.length;i+=16384)chunks.push(String.fromCharCode(...bytes.subarray(i,i+16384)));
          return {pcm:btoa(chunks.join('')),peak,rms:Math.sqrt(energy/(buffer.length*2)),clipped,nonfinite,voices:__voices,debug};
        }''',mode)
        pcm=base64.b64decode(signal.pop('pcm'))
        with wave.open(str(out/(mode+'.wav')),'wb') as wav:
            wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(48000);wav.writeframes(pcm)
        signal['errors']=errors
        assert not errors and not signal['nonfinite'] and not signal['clipped'] and signal['rms']>0,signal
        report['samples'][mode]=signal
        page.close()
    browser.close()
(out/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
