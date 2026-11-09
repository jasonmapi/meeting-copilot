"""Import prepared research and questions; never invent company facts."""
import argparse,datetime,hashlib,json,pathlib,shutil,socket,uuid
def inside(folder,name):
 p=(folder/name).resolve()
 if not p.is_relative_to(folder) or not p.is_file():raise ValueError('Invalid report path: '+name)
 return p
def main():
 p=argparse.ArgumentParser();p.add_argument('--target',required=True);p.add_argument('--company',required=True);p.add_argument('--date',required=True);p.add_argument('--report-dir',required=True);p.add_argument('--report-html',required=True);p.add_argument('--brief-html');p.add_argument('--brief',required=True);p.add_argument('--checklist',required=True);a=p.parse_args()
 target=pathlib.Path(a.target).expanduser().resolve();source=pathlib.Path(a.report_dir).expanduser().resolve()
 if not (target/'install-manifest.json').exists():raise SystemExit('Not an installed deployment')
 port=json.loads((target/'server-config.json').read_text()).get('port',8766) if (target/'server-config.json').exists() else 8766
 with socket.socket() as sock:
  sock.settimeout(.5)
  if sock.connect_ex(('127.0.0.1',port))==0:raise SystemExit('Stop the local service with run.py --stop before importing a company.')
 inside(source,a.report_html)
 if a.brief_html:inside(source,a.brief_html)
 text=pathlib.Path(a.brief).read_text(encoding='utf-8-sig')
 if not text.strip() or len(text)>32000:raise SystemExit('Brief must be nonempty and at most 32000 characters; retain full report as originals.')
 raw=json.loads(pathlib.Path(a.checklist).read_text(encoding='utf-8-sig'));questions=raw['questions']
 if not isinstance(questions,list) or not questions or len(questions)>60:raise ValueError('Provide 1–60 questions')
 ids=set();normalized=[];company_id=hashlib.sha256(a.company.encode()).hexdigest()[:12]
 for q in questions:
  if not all(isinstance(q.get(k),str) and q[k].strip() for k in ('id','question','criterion')):raise ValueError('Question requires id/question/criterion')
  if q['id'] in ids:raise ValueError('Duplicate question ID')
  ids.add(q['id'])
  normalized.append({'id':company_id+'-'+q['id'],'priority':q.get('priority','P1'),'group':q.get('group','待核实'),'question':q['question'],'criterion':q['criterion'],'source':q.get('source','本企业调研报告')})
 files=[];allowed={'.html','.md','.csv','.css','.js','.png','.jpg','.jpeg','.svg','.pdf'}
 for file in source.rglob('*'):
  if file.is_file() and not file.is_symlink() and file.suffix.lower() in allowed and not any(x.startswith('.') for x in file.relative_to(source).parts):files.append(file)
 if not files:raise ValueError('No report files')
 stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6];backup=target/'backups'/('company-'+stamp);backup.mkdir(parents=True)
 # Stage a complete new set before replacing active data.
 stage=target/'research'/('stage-'+stamp);stage.mkdir(parents=True)
 for file in files:
  dest=stage/file.relative_to(source);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
 for name in ('meeting-brief.md','meeting-brief.meta.json','verification-checklist.json'):
  if (target/name).exists():shutil.copy2(target/name,backup/name)
 current=target/'research/current'
 if current.exists():current.rename(backup/'research')
 stage.rename(current)
 (target/'meeting-brief.md').write_text(text,encoding='utf-8')
 meta={'company':a.company,'title':a.company+' · AI售前研究','research_date':a.date,'report_url':'/research/'+a.report_html,'characters':len(text),'sha256':hashlib.sha256((target/'meeting-brief.md').read_bytes()).hexdigest(),'source_files':[{'name':str(f.relative_to(source)).replace('\\','/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in files]}
 if a.brief_html:meta['brief_url']='/research/'+a.brief_html
 (target/'meeting-brief.meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
 (target/'verification-checklist.json').write_text(json.dumps({'company':a.company,'questions':normalized},ensure_ascii=False,indent=2),encoding='utf-8')
 (target/'transcripts'/('新企业-'+stamp+'.txt')).write_text('',encoding='utf-8')
 print(json.dumps({'company':a.company,'files':len(files),'characters':len(text),'questions':len(normalized),'backup':str(backup)},ensure_ascii=False))
if __name__=='__main__':main()
