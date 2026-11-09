# 研究、资料导入与问题契约

研究流程完整包含于`research-skill/SKILL.md`，先按其证据契约完成研究。新报告默认11章，缺证据也保留章节与未知；现有报告只迁移界面时保留原评分/题数。不要将历史示例企业案例替换成目标公司名字当作新研究。

在部署venv中运行内置研究工具：
```text
<venv-python> <skill>/references/research-skill/scripts/validate_report.py report-data.json
<venv-python> <skill>/references/research-skill/scripts/render_report.py report-data.json report.html
```
渲染Markdown依赖由主安装器提供。数据契约在该目录assets/report-data.schema-notes.md，章节真源在assets/structure.json。结构通过不证明事实真实；来源核查由Agent执行。

准备三份输入：
1. 报告目录：HTML、MD、证据CSV、CSS/JS、图片/PDF；只能放允许分享至该部署的研究成果，不把API配置或访谈日志混进去。
2. `meeting-brief.md`：目标企业、研究日期、已知事实及E编号/URL、未知/冲突、待验证场景、现场目标、提问优先级和边界。上限32000字符；超限要保留原件并另写明确的现场摘要，不能静默截断。
3. `questions.json`：一项问题对应可观察的完成条件，避免“说到预算二字就完成”的关键词匹配。问题数依企业而定，1–60项。模板如下：
```json
{"questions":[{"id":"budget","priority":"P1","group":"预算与计划","question":"预算范围、审批条件和采购周期是什么？","criterion":"明确金额或尚未定预算、审批责任及采购周期；假设或问句中的数字不计。","source":"研究报告访谈清单"}]}
```
不要在模板预填status/answer/evidence。导入器会给ID加企业前缀，避免跨企业误用。

停止服务后，从Skill目录运行：
```text
python scripts/import_company.py --target <部署目录> --company "企业完整名称" --date 2026-11-09 --report-dir <报告目录> --report-html report.html --brief <meeting-brief.md路径> --checklist <questions.json路径>
```
若有简报HTML，另加`--brief-html brief.html`。HTML路径相对report-dir，可含子目录；复制范围限定为报告类型文件，不复制目录中的JSON密钥或脚本。导入器备份旧企业资料、创建新企业空会话；原访谈文件和成果仍保留。重启后核对页面企业名、加载字符数、完整报告入口、问题清单数量。

页面中灰色未获取，黄色部分回答，绿色已捕获完整回答，红色冲突。自动答案必须附本场转写中的连续原文；问题未完整回答、角色不明或疑似识别错误不能完成。用户可将自动完成项退回，直到新证据出现才重新自动判断。
