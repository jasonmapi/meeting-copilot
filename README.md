# MeetingCopilot｜商谈智囊

实时理解对话，提示关键追问，辅助商业决策。

企业 AI 培训售前与现场商谈的本地工作台：背景尽调、报告导入、后台麦克风转写、实时辅导、成果墙和待核实问题。切换其他软件不影响后台收音。

## 使用许可

**公开源码，禁止未经授权的商用；不属于标准开源许可。** 从 v1.0.2 起，本项目原创内容采用 [MeetingCopilot 非商业与源码共享许可证 1.0](LICENSE)。

- 非商业使用及许可列明的机构使用可以；商业用途需相关权利人另行书面授权。
- 对外分发修改版，须向接收者提供对应源码；运行修改版在线服务，须向全部交互用户提供对应源码。
- 鼓励 [提交 PR](CONTRIBUTING.md) 回馈原仓库，但不强制提交，也不要求维护者合并。
- 源码义务不要求上传密钥、客户资料或业务数据；第三方依赖及模型遵循各自许可。

详见 [许可说明与场景示例](LICENSING.md)。这是自定义许可，尚未经律师审核。v1.0.1 继续按其随附旧许可处理，新条款不追溯改变已取得的旧版权利。商业授权可向 [维护者](https://github.com/jasonmapi) 提交不含私密信息的咨询。

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
