import socket,argparse,json,pathlib,subprocess,sys,time,urllib.request,webbrowser
ROOT=pathlib.Path(__file__).resolve().parent
PORT=json.loads((ROOT/'server-config.json').read_text()).get('port',8766) if (ROOT/'server-config.json').exists() else 8766
URL='http://127.0.0.1:'+str(PORT)
def health():
 try:
  with urllib.request.urlopen(URL+'/api/health',timeout=1) as r:return json.load(r)
 except Exception:return None
def stop():
 req=urllib.request.Request(URL+'/api/shutdown',data=b'{}',headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--stop',action='store_true');parser.add_argument('--no-browser',action='store_true');a=parser.parse_args()
 instance=json.loads((ROOT/'install-manifest.json').read_text())['instance_id'];h=health()
 if h:
  if h.get('instance_id')!=instance:raise SystemExit('Configured port belongs to another deployment; do not stop it.')
  if a.stop:stop();return
  if not a.no_browser:webbrowser.open(URL)
  print('Already running '+URL);return
 if a.stop:raise SystemExit('This deployment is not running.')
 with socket.socket() as sock:
  sock.settimeout(.5)
  if sock.connect_ex(('127.0.0.1',PORT))==0:raise SystemExit('Configured port is occupied by another service; choose a free environment, do not kill it.')
 child=subprocess.Popen([sys.executable,'-u',str(ROOT/'bridge.py')],cwd=ROOT)
 try:
  for _ in range(80):
   h=health()
   if h and h.get('instance_id')==instance:break
   if child.poll() is not None:raise SystemExit('Server failed; inspect the message above.')
   time.sleep(.25)
  else:raise SystemExit('Server did not become ready.')
  print(URL+' 路 Ctrl+C to stop service and recording',flush=True)
  if not a.no_browser:webbrowser.open(URL)
  child.wait()
 except KeyboardInterrupt:
  try:stop()
  except Exception:pass
  child.wait(timeout=30)
 finally:
  if child.poll() is None:
   try:stop();child.wait(timeout=30)
   except Exception:child.terminate()
if __name__=='__main__':main()
