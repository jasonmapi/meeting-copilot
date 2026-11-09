// 可复用视觉模块，读取报告自身数据，禁止硬编码示范企业事实。
const reportSection=n=>document.getElementById('s'+String(n).padStart(2,'0'));
// 岗位与技术成果：保留原段落和出处，只增加分组容器。
function groupParagraphs(n,subheading,stop,kind){const section=reportSection(n);let active=false;[...section.children].forEach(el=>{if(el.tagName==='H3'){active=el.textContent.startsWith(subheading);return}if(!active||el.tagName!=='P')return;if(stop&&el.textContent.startsWith(stop)){active=false;return}if(el.firstElementChild?.tagName==='STRONG'){const box=document.createElement('div');box.className='research-card '+kind;section.insertBefore(box,el);box.append(el)}})}
groupParagraphs(3,'3.2','业务流程假设','role');groupParagraphs(4,'4.1',null,'technical');groupParagraphs(4,'4.3',null,'software');
// 四阶段：原始全文保留于可展开详情，不丢失课程表、试点与风险条件。
const plan=reportSection(8),blocks=[...plan.children].filter(el=>el.tagName!=='H2');const groups=[];let current=null;
blocks.forEach(el=>{if(el.tagName==='P'&&/^阶段[一二三四]：/.test(el.textContent)){current={title:el.textContent,nodes:[]};groups.push(current)}else if(current)current.nodes.push(el)});
if(groups.length!==4||!d.stage_visuals||d.stage_visuals.length!==4)throw Error('四阶段展示数据不完整');
const colors=['#65b29a','#7196cf','#bba06b','#9a8aba'];
const intro=document.createElement('p');intro.className='roadmap-intro';intro.textContent='先诊断，再训练与试点，验收后持续推广。以下均为有条件的合作建议，尚未立项。';
const rail=document.createElement('div');rail.className='phase-rail';rail.setAttribute('aria-label','四阶段路线');rail.innerHTML=d.stage_visuals.map((s,i)=>`<a href="#phase-${i+1}" style="--phase:${colors[i]}"><b>0${i+1}</b>${safe(s.short)}</a>`).join('');
const list=document.createElement('div');list.className='phase-list';
groups.forEach((g,i)=>{const s=d.stage_visuals[i];const phase=document.createElement('article');phase.className='phase';phase.id='phase-'+(i+1);phase.style.setProperty('--phase',colors[i]);phase.innerHTML=`<span class="phase-number">${i+1}</span><div class="phase-card"><div class="phase-top"><h3>${safe(g.title)}</h3><p>${safe(s.goal)}</p></div><div class="phase-grid"><div class="phase-field"><span>参与对象</span><p>${safe(s.audience)}</p></div><div class="phase-field"><span>核心动作</span><p>${safe(s.action)}</p></div><div class="phase-field"><span>交付成果</span><p>${safe(s.deliverables)}</p></div><div class="phase-field"><span>周期与安排</span><p>${safe(s.timing)}</p></div><div class="phase-field gate"><span>进入下一阶段的条件</span><p>${safe(s.gate)}</p></div></div><details class="phase-details"><summary>${safe(s.detail_label)}</summary><div class="phase-original"></div></details></div>`;const body=phase.querySelector('.phase-original');g.nodes.forEach(node=>body.append(node));list.append(phase)});
blocks.forEach(el=>{if(el.parentNode===plan)el.remove()});plan.append(intro,rail,list);
// 阶段三试点对照表转为两张逐字段卡，完整字段及原文保留。
const pilotTable=plan.querySelector('#phase-3 table');if(pilotTable){const heads=[...pilotTable.querySelectorAll('thead th')];const rows=[...pilotTable.querySelectorAll('tbody tr')];if(heads.length===3){const grid=document.createElement('div');grid.className='pilot-grid';for(let c=1;c<3;c++){const card=document.createElement('div');card.className='pilot-card';const title=document.createElement('h4');title.textContent=heads[c].textContent;card.append(title);const dl=document.createElement('dl');rows.forEach(row=>{const dt=document.createElement('dt');dt.textContent=row.cells[0].textContent;const dd=document.createElement('dd');dd.innerHTML=row.cells[c].innerHTML;dl.append(dt,dd)});card.append(dl);grid.append(card)}pilotTable.replaceWith(grid)}}
count();
// 打印时展开所有详情，打印后恢复用户选择，保证不遗漏证据和方案全文。
let previousDetails=[];addEventListener('beforeprint',()=>{previousDetails=[...document.querySelectorAll('details')].map(el=>[el,el.open]);previousDetails.forEach(([el])=>el.open=true)});addEventListener('afterprint',()=>previousDetails.forEach(([el,open])=>el.open=open));
