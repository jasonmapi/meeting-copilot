"""校验结构、交互数据和证据关联；不替代人工事实核验。"""
from pathlib import Path
import json,re,sys
def validate(d,schema):
 errors=[]
 def check(ok,msg):
  if not ok:errors.append(msg)
 check(d.get('schema_version')==schema['version'],'模板版本不一致')
 expected_count=d.get('content_preservation',{}).get('interview_count',12)
 expected=[h.replace('{企业简称}',d['short_name']) for h in schema['sections']]
 expected[6]=expected[6].replace('12个问题',str(expected_count)+'个问题')
 check([s['title'] for s in d['sections']]==expected,'11章标题或顺序不一致')
 for n,heads in schema['subsections'].items():
  actual=re.findall(r'^### (.+)$',d['sections'][int(n)-1]['body'],re.M)
  check(actual==heads,f'第{n}章子节漂移')
 for w,n in [('map',5),('opportunities',6),('interviews',7)]:
  check(f'<!-- widget:{w} -->' in d['sections'][n-1]['body'],w+'位置或模块缺失')
 check(len(d['interviews'])==expected_count,'访谈题数与基准不一致')
 for stage in schema['stages']:check(stage in d['sections'][7]['body'],'阶段缺失：'+stage)
 ids=[s['id'] for s in d['sources']];check(len(ids)==len(set(ids)),'重复证据ID')
 for s in d['sources']:
  for k in ['id','title','url','level','state','event_date','published_date','accessed','location','claim','limit','family','subject']:check(bool(s.get(k)),f'{s.get("id")}缺来源字段{k}')
  check(s['url'].startswith('https://'),'来源链接非https')
 for o in d['opportunities']:
  for k in ['id','name','department','value','ease','value_range','ease_range','status','confidence','evidence','input_output','gate','review','metric','alternative','demo']:check(k in o,f'机会缺字段{k}')
  for key in ['value','ease']:
   lo,hi=o[key+'_range'];check(1<=lo<=hi<=5,'评分区间不合法')
   if d.get('scoring_mode')=='five_dimension_intervals':check(o[key] is None,'区间迁移禁止生成点分')
   else:check(1<=o[key]<=5,'评分超范围');check(lo<=o[key]<=hi,'默认分不在区间')
  check(bool(o['evidence']) and all(x in ids for x in o['evidence']),'机会证据悬空')
 for q in d['interviews']:
  for k in ['id','theme','owner','question','evidence','impact']:check(bool(q.get(k)),'访谈缺字段'+k)
 check(len(set(q['id'] for q in d['interviews']))==expected_count,'访谈ID重复')
 for a in d['addresses']:check(all(x in ids for x in a['evidence']),'地址证据悬空')
 for n,header in [(3,'| 业务领域 | 已发现的信息 | 对AI售前的价值 |'),(4,'| 专利 | 发现的关键事实 |'),(4,'| 年份 | 公开记录 | 证据性质 |'),(9,'| 信息类别 | 本次情况 | 建议下一步 |'),(10,'| 资料 | 用途 |')]:
  check(header in d['sections'][n-1]['body'],f'第{n}章表头漂移：{header}')
 basic=['企业名称','经营状态','成立日期','注册资本','法定代表人','企业类型','统一社会信用代码','注册地址']
 for field in basic:check('| '+field+' |' in d['sections'][1]['body'],'工商字段缺失：'+field)
 gaps=['股权与管理团队','营业收入、利润','现有客户和主要订单','产品目录和规格','完整专利及软著清单','招投标与供应商关系','司法、行政及经营风险','官网和社交媒体','当前员工与岗位数量','信息化基础','AI使用现状与预算','数据保密及部署要求']
 for field in gaps:check('| '+field+' |' in d['sections'][8]['body'],'缺口类别缺失：'+field)
 check(not re.search(r'|turn\d+(search|view)',json.dumps(d,ensure_ascii=False)),'残留聊天内部引用')
 check(len(d.get('stage_visuals',[]))==4,'阶段可视化必须4项')
 for s in d.get('stage_visuals',[]):
  for key in ['short','goal','audience','action','deliverables','timing','gate','detail_label']:check(bool(s.get(key)),'阶段摘要缺字段：'+key)
 if d.get('scoring_mode')=='five_dimension_intervals':
  for o in d['opportunities']:
   check(len(o.get('score_range',[]))==2 and o.get('priority_group') in [1,2,3,4],'原分数或优先组缺失')
  check(bool(d.get('content_preservation',{}).get('baseline')),'内容迁移未声明基准')
 return errors
if __name__=='__main__':
 d=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));s=json.loads((Path(__file__).resolve().parents[1]/'assets/structure.json').read_text(encoding='utf-8'))
 e=validate(d,s);print(json.dumps({'passed':not e,'errors':e,'sections':len(d['sections']),'sources':len(d['sources']),'opportunities':len(d['opportunities']),'interviews':len(d['interviews'])},ensure_ascii=False));sys.exit(bool(e))
