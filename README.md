# MeetingCopilot｜商谈智囊

实时理解对话，提示关键追问，辅助商业决策。

企业 AI 培训售前与现场商谈的本地工作台：背景尽调、报告导入、后台麦克风转写、实时辅导、成果墙和待核实问题。切换其他软件不影响后台收音。

## 使用许可

**公开源码，非商业许可；不是允许自由商用的开源项目。** 本项目原创代码、Skill、文档和素材采用 [PolyForm Noncommercial 1.0.0](LICENSE)。允许符合条款的非商业使用、修改与分发。商业使用（如企业商业业务中的销售辅助、收费咨询或培训服务、收费部署、商业产品集成）应先取得权利人的单独授权。许可明确允许教育、公益、政府等指定机构使用，具体范围以 LICENSE 原文为准。

商业授权请通过 [GitHub 账号主页](https://github.com/jasonmapi) 联系维护者；可提交不含私密信息的 Issue 说明授权需求。本仓库没有自动授予商用权。第三方依赖及模型权重遵循各自许可证，不因本仓库许可而改变。

## 功能

- 企业背景尽调：内嵌完整研究 Skill、证据规则、报告模板与渲染脚本。
- 本机后台语音转写：faster-whisper，默认 turbo / 粤语 / CPU / 12 秒分段。
- 实时辅导：“下一问”“为什么”“待确认”独立展示。
- 转写自动跟随、信息成果墙、待核实问题自动填答和颜色状态。
- 新一场清空当前页面，保留历史会话；企业报告和客户展示素材入口。
- 用户在本机填写兼容 Chat Completions 的 API 配置；启用分析后，相关文字和会前资料会发送到该模型服务。

## 交给 Agent 安装

下载或克隆本仓库，让具备联网和本地命令执行能力的 Agent 阅读根目录 [SKILL.md](SKILL.md)，按部署、资料导入与验收流程执行。Skill 标识保留 `enterprise-ai-fieldwork-deploy`。

```sh
git clone https://github.com/jasonmapi/meeting-copilot.git
cd meeting-copilot
```

需要 Python 3.10–3.12。首次安装需联网下载依赖和模型；模型权重不随仓库分发。

Windows（PowerShell）：

```powershell
python scripts/install.py --target "$HOME/MeetingCopilot" --plan
python scripts/install.py --target "$HOME/MeetingCopilot"
& "$HOME/MeetingCopilot/.venv/Scripts/python.exe" "$HOME/MeetingCopilot/run.py"
```

macOS（Terminal）：

```sh
python3 scripts/install.py --target "$HOME/MeetingCopilot" --plan
python3 scripts/install.py --target "$HOME/MeetingCopilot"
"$HOME/MeetingCopilot/.venv/bin/python" "$HOME/MeetingCopilot/run.py"
```

打开启动器显示的网址，默认 `http://127.0.0.1:8766/`，填写 API 地址、模型名称、密钥并启用分析。点击开始录音；macOS 需允许 Terminal/Python 使用麦克风。默认仅监听本机。端口占用时安装可加 `--port 8876`。

完整说明：[部署](references/deployment.md) · [企业资料导入](references/company-import.md) · [验收与故障定位](references/acceptance.md)

## 验证与限制

Windows 隔离安装、CPU 模型加载、模拟接口和网页交互已验证，详见 [验证记录](references/validation.md)。macOS 按 CPU 路径提供部署支持，**尚未进行 macOS 实机验收**；不提供 Metal 加速承诺。不同设备的粤语准确度、转写速度和资源占用需现场实测。12 秒分段不是逐字零延迟，模型分析还受网络和 API 响应速度影响。

成果墙与绿色问题状态表示已从对话捕获对应信息，不代表外部事实已核实；重要商业决策仍需人工判断。

## 包完整性与行为验证

```sh
python scripts/verify_package.py
python scripts/smoke_test.py --target assets/app
```

行为测试使用临时目录及模拟接口，不启动麦克风、不调用付费 API。仓库不包含 API 密钥、客户研究报告、客户录音、会话成果、虚拟环境或模型权重。版本包见 [Releases](https://github.com/jasonmapi/meeting-copilot/releases)。
