"""可选视觉契约检查。依赖playwright及本机Edge；不替代截图审读或事实核验。
用法：python scripts/check_visual.py 报告.html
"""
from pathlib import Path
import sys,json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 browser=p.chromium.launch(channel='msedge',headless=True)
 page=browser.new_page(viewport={'width':1100,'height':1000});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.goto(Path(sys.argv[1]).resolve().as_uri())
 d=page.locator('#report-data').text_content();d=json.loads(d)
 assert page.locator('section[data-section]').count()==11
 assert page.locator('.phase').count()==4
 assert page.locator('.phase-details').count()==4
 assert page.locator('#phase-4 h3').inner_text()=='阶段四：企业持续应用与安全治理'
 assert page.locator('.question').count()==len(d['interviews'])
 assert page.locator('.rating').count()==len(d['opportunities'])*2
 assert page.locator('.op-demo').count()==len(d['opportunities'])
 for width in [1100,390]:
  page.set_viewport_size({'width':width,'height':900})
  assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.locator('[data-question]').first.check()
 assert page.locator('.interview-progress').get_attribute('aria-valuenow')=='1'
 page.reload();assert page.locator('.question.done').count()==1
 page.locator('#clear-interviews').click()
 assert page.locator('.interview-progress').get_attribute('aria-valuenow')=='0'
 for n in range(1,5):
  detail=page.locator(f'#phase-{n} details');detail.locator('summary').click()
  assert detail.get_attribute('open') is not None
  assert detail.locator('.phase-original').inner_text().strip()
 assert not errors,errors
 browser.close()
print('全11章视觉结构、双评分条、访谈进度与持久化、四阶段详情和窄屏检查通过。')
