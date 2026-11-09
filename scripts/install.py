"""Install an isolated Windows/macOS deployment. Run with Python 3.10–3.12."""
import socket,getpass,argparse,datetime,json,os,pathlib,platform,shutil,subprocess,sys,venv,uuid
SKILL=pathlib.Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--target',required=True);p.add_argument('--port',type=int,default=8766);p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--model',choices=['turbo','small'],default='turbo');p.add_argument('--language',default=None);p.add_argument('--model-source');p.add_argument('--skip-deps',action='store_true');p.add_argument('--skip-model',action='store_true');p.add_argument('--plan',action='store_true');a=p.parse_args()
 target=pathlib.Path(a.target).expanduser().resolve()
 if platform.system() not in ('Windows','Darwin','Linux'):raise SystemExit('Supported hosts: Windows/macOS; Linux is best effort.')
 if not (3,10)<=sys.version_info[:2]<=(3,12):raise SystemExit('Use Python 3.10–3.12 (recommended 3.12) for this package.')
 if platform.system()=='Darwin' and a.device=='cuda':raise SystemExit('macOS has no CUDA path; choose --device cpu.')
 language=a.language or ('yue' if a.model=='turbo' else 'zh')
 if language=='yue' and a.model=='small':raise SystemExit('small has no yue token; use turbo or zh language.')
 print(json.dumps({'target':str(target),'os':platform.system(),'arch':platform.machine(),'port':a.port,'device':a.device,'model':a.model,'language':language,'chunk_seconds':5 if a.device=='cuda' or a.model=='small' else 12},ensure_ascii=False),flush=True)
 if not 1024<=a.port<=65535:raise SystemExit('Port must be 1024–65535')
 if a.plan:return
 server_config=target/'server-config.json'
 port=json.loads(server_config.read_text()).get('port',a.port) if server_config.exists() else a.port
 with socket.socket() as sock:
  sock.settimeout(.5)
  if sock.connect_ex(('127.0.0.1',port))==0:raise SystemExit('Port occupied. Stop this deployment before upgrade, or choose a free --port for a new installation.')
 marker=target/'install-manifest.json'
 if target.exists() and any(target.iterdir()) and not marker.exists():raise SystemExit('Target is not an empty deployment directory; choose another path.')
 target.mkdir(parents=True,exist_ok=True)
 if not server_config.exists():server_config.write_text(json.dumps({'port':port}),encoding='utf-8')
 prior=json.loads(marker.read_text()) if marker.exists() else {}
 stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:4]
 backup=target/'backups'/stamp
 # Never overwrite business data or credentials on upgrade.
 preserve={'analysis-config.json','asr-config.json','meeting-brief.md','meeting-brief.meta.json','verification-checklist.json'}
 for src in (SKILL/'assets/app').rglob('*'):
  if not src.is_file() or '__pycache__' in src.parts:continue
  rel=src.relative_to(SKILL/'assets/app');dst=target/rel
  if dst.exists() and str(rel) in preserve:continue
  if dst.exists():
   old=backup/rel;old.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,old)
  dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
 for name in ('LICENSE','NOTICE','LICENSING.md','CONTRIBUTING.md'):
  dst=target/name
  if dst.exists():
   backup.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,backup/name)
  shutil.copy2(SKILL/name,dst)
 for name in ('results','transcripts','models','research/current'):(target/name).mkdir(parents=True,exist_ok=True)
 config=target/'analysis-config.json'
 if not config.exists():shutil.copy2(target/'analysis-config.example.json',config)
 if os.name!='nt':os.chmod(config,0o600)
 else:subprocess.run(['icacls',str(config),'/inheritance:r','/grant:r',getpass.getuser()+':(F)','SYSTEM:(F)'],check=True,stdout=subprocess.DEVNULL)
 asr=target/'asr-config.json'
 if not asr.exists():asr.write_text(json.dumps({'device':a.device,'model_name':a.model,'model_path':'models/'+a.model,'language':language,'cpu_threads':4,'chunk_seconds':5 if a.device=='cuda' or a.model=='small' else 12,'input_device':None},ensure_ascii=False,indent=2),encoding='utf-8')
 selected=json.loads(asr.read_text(encoding='utf-8'))
 if selected['model_name']!=a.model or selected['device']!=a.device:raise SystemExit('Existing asr-config preserved. Re-run using matching --model / --device; change config intentionally if needed.')
 marker.write_text(json.dumps({'app':'enterprise-ai-fieldwork','version':'1.0.2','instance_id':prior.get('instance_id',uuid.uuid4().hex),'created':prior.get('created',stamp),'updated':stamp,'device':a.device,'os':platform.system(),'python':sys.version.split()[0]},indent=2),encoding='utf-8')
 env=target/'.venv';py=env/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
 if not py.exists():venv.EnvBuilder(with_pip=True).create(env)
 if not a.skip_deps:
  subprocess.run([str(py),'-m','pip','install','--disable-pip-version-check','-r',str(target/'requirements.txt')],check=True)
  if a.device=='cuda':subprocess.run([str(py),'-m','pip','install','torch>=2.7,<3','--index-url','https://download.pytorch.org/whl/cu128'],check=True)
  with (target/'installed-packages.txt').open('w',encoding='utf-8') as f:subprocess.run([str(py),'-m','pip','freeze'],stdout=f,check=True)
 modelpath=target/selected['model_path']
 if not a.skip_model:
  if a.model_source:
   source=pathlib.Path(a.model_source).expanduser().resolve()
   for name in ('model.bin','config.json','tokenizer.json'):
    if not (source/name).is_file():raise SystemExit('Model source missing '+name)
   modelpath.mkdir(parents=True,exist_ok=True)
   for name in ('model.bin','config.json','tokenizer.json','vocabulary.json','vocabulary.txt','preprocessor_config.json'):
    if (source/name).exists():shutil.copy2(source/name,modelpath/name)
  elif not (modelpath/'model.bin').exists():
   repo='dropbox-dash/faster-whisper-large-v3-turbo' if a.model=='turbo' else 'Systran/faster-whisper-small'
   code='from huggingface_hub import snapshot_download;import sys;snapshot_download(sys.argv[1],local_dir=sys.argv[2],allow_patterns=["model.bin","config.json","tokenizer.json","vocabulary.*","preprocessor_config.json"])'
   subprocess.run([str(py),'-c',code,repo,str(modelpath)],check=True)
 launch=target/'启动现场助手.command'
 launch.write_text('#!/bin/bash\ncd "$(dirname "$0")"\nexec ".venv/bin/python" run.py\n',encoding='utf-8',newline='\n');launch.chmod(0o755)
 (target/'启动现场助手.cmd').write_text('@echo off\r\ncd /d "%~dp0"\r\n".venv\\Scripts\\python.exe" run.py\r\npause\r\n',encoding='utf-8',newline='')
 if not a.skip_deps and not a.skip_model:subprocess.run([str(py),str(target/'doctor.py')],cwd=target,check=True)
 print('Installed. Run deployment venv Python run.py; configure API in browser. No microphone has started.',flush=True)
 if a.skip_deps or a.skip_model:print('Partial installation: skipped steps must be completed before recording.',flush=True)
if __name__=='__main__':main()
