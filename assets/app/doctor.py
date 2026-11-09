"""No microphone recording. Optional API probe sends synthetic text only."""
import argparse,importlib,json,pathlib,platform,sys,time,urllib.request
from asr_runtime import settings,load_model,options
ROOT=pathlib.Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--load-model',action='store_true');p.add_argument('--api',action='store_true');p.add_argument('--audio');a=p.parse_args();errors=[]
 print(json.dumps({'os':platform.system(),'arch':platform.machine(),'python':sys.version.split()[0]},ensure_ascii=False))
 for name in ('faster_whisper','ctranslate2','sounddevice','numpy','scipy','psutil'):
  try:importlib.import_module(name);print(name+': OK')
  except Exception as e:errors.append(name+': '+type(e).__name__)
 c=settings();model=ROOT/c['model_path']
 print('ASR',c['device'],c['model_name'],c.get('language'),c.get('chunk_seconds'))
 if not (model/'model.bin').exists():errors.append('Model not installed')
 try:
  import sounddevice as sd
  inputs=[{'index':i,'name':x['name'],'default_samplerate':x['default_samplerate']} for i,x in enumerate(sd.query_devices()) if x['max_input_channels']>0]
  print('Microphone devices:',json.dumps(inputs,ensure_ascii=False))
  if not inputs:print('WARNING: no input devices; attach one before recording.')
 except Exception as e:errors.append('Audio devices: '+type(e).__name__)
 if a.load_model or a.audio:
  try:
   t=time.monotonic();m=load_model(c);print('Model load seconds:',round(time.monotonic()-t,2))
   if a.audio:
    from faster_whisper.audio import decode_audio
    audio=decode_audio(a.audio,sampling_rate=16000);rows=[];size=int(c['chunk_seconds']*16000)
    for i in range(0,len(audio),size):
     part=audio[i:i+size];t=time.monotonic();segments,_=m.transcribe(part,**options(c));text=''.join(s.text for s in segments);elapsed=time.monotonic()-t
     rows.append({'audio_seconds':len(part)/16000,'seconds':elapsed,'text':text})
    result={'runs':rows,'rtf':sum(x['seconds'] for x in rows)/(len(audio)/16000)}
    (ROOT/'results/asr-acceptance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('RTF:',round(result['rtf'],3),'(<1 required for sustained realtime; latency includes chunk collection)')
  except Exception as e:errors.append('Model/benchmark: '+type(e).__name__)
 if a.api:
  try:
   c=json.loads((ROOT/'analysis-config.json').read_text(encoding='utf-8-sig'));payload={'model':c['model'],'messages':[{'role':'user','content':'连接测试。只回复OK。'}],'max_tokens':16}
   if urllib.parse.urlparse(c['base_url']).hostname=='api.deepseek.com':payload['thinking']={'type':'disabled'}
   headers={'Content-Type':'application/json'}
   if c.get('api_key'):headers['Authorization']='Bearer '+c['api_key']
   req=urllib.request.Request(c['base_url'].rstrip('/')+'/chat/completions',data=json.dumps(payload).encode(),headers=headers)
   with urllib.request.urlopen(req,timeout=30) as r:data=json.load(r)
   assert data.get('choices');print('API: OK (synthetic probe, no meeting content)')
  except Exception as e:errors.append('API: '+type(e).__name__)
 for error in errors:print('ERROR:',error)
 return 1 if errors else 0
if __name__=='__main__':sys.exit(main())
