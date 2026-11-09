"""Isolated behavior tests: no recording, no real API, no deployment data edits."""
import argparse,importlib.util,json,pathlib,tempfile,threading,urllib.request,shutil
from http.server import HTTPServer,BaseHTTPRequestHandler
def main():
 p=argparse.ArgumentParser();p.add_argument('--target',required=True);a=p.parse_args();target=pathlib.Path(a.target).resolve()
 spec=importlib.util.spec_from_file_location('fieldwork_test',target/'bridge.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 with tempfile.TemporaryDirectory() as temp:
  b.ROOT=pathlib.Path(temp);b.CONFIG=b.ROOT/'analysis-config.json'
  for folder in ('results','transcripts','research/current'):(b.ROOT/folder).mkdir(parents=True)
  shutil.copy2(target/'verification-checklist.json',b.ROOT)
  b.CONFIG.write_text(json.dumps({'enabled':False,'api_key':'synthetic-secret','base_url':'https://example.invalid','model':'mock'}))
  b.STATE.update(file='one.txt',transcript='客户确认本次以员工提效为主，希望减少报价错误。',facts=[],checks=b.load_checks())
  (b.ROOT/'transcripts/one.txt').write_text(b.STATE['transcript'],encoding='utf-8')
  qid=b.STATE['checks'][0]['id'];text=b.STATE['transcript']
  answer={'question':'最近一次任务怎么流转？','why':'确认流程','confirm':['谁审核？'],'facts':[{'category':'goal','value':'减少报价错误','evidence':text},{'category':'budget','value':'一百万元','evidence':'不存在的预算原文'}],'checks':[{'id':qid,'status':'completed','answer':'员工提效','evidence':text,'missing':''}]}
  class Mock(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_POST(self):
    self.rfile.read(int(self.headers['Content-Length']));self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
    result=json.dumps(answer,ensure_ascii=False)
    for token in (result[:20],result[20:]):self.wfile.write(('data: '+json.dumps({'choices':[{'delta':{'content':token}}]},ensure_ascii=False)+'\n\n').encode())
    self.wfile.write(b'data: [DONE]\n\n')
  mock=HTTPServer(('127.0.0.1',0),Mock);threading.Thread(target=mock.serve_forever,daemon=True).start()
  b.analyze(text,1,{'base_url':'http://127.0.0.1:'+str(mock.server_port),'model':'mock'},'one.txt');mock.shutdown()
  assert len(b.STATE['facts'])==1 and b.STATE['checks'][0]['status']=='completed'
  assert b.load_checks('one.txt')[0]['status']=='completed'
  assert all(q['status']=='pending' for q in b.load_checks('other.txt'))
  server=b.ThreadingHTTPServer(('127.0.0.1',0),b.Handler);threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)
  with urllib.request.urlopen(url+'/api/state') as r:state=json.load(r)
  assert 'api_key' not in state['config'] and 'synthetic-secret' not in json.dumps(state)
  def post(path,data):
   with urllib.request.urlopen(urllib.request.Request(url+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json'})) as r:return json.load(r)
  post('/api/check/reopen',{'file':'one.txt','id':qid,'revision':1});b.apply_result(answer,'one.txt',2);assert b.STATE['checks'][0]['status']=='partial'
  post('/api/session/new',{});assert b.STATE['transcript']=='' and b.STATE['advice']=={} and b.STATE['facts']==[]
  assert all(q['status']=='pending' for q in b.STATE['checks']) and (b.ROOT/'transcripts/one.txt').exists()
  assert not b.apply_result(answer,'one.txt',3)
  server.shutdown()
 print('PASS: mock SSE, evidence validation, cumulative progress, persistence, manual reopen, fresh-session isolation, secret redaction. No microphone or paid API used.')
if __name__=='__main__':main()
