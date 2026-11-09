# 部署手册

本包是Agent可执行的源码部署，不是签名的macOS App或Windows MSI。首次安装需要互联网下载Python依赖和模型；日常语音识别在本机完成，模型辅导需要已配置API网络。浏览器与服务运行在同一台电脑，只监听127.0.0.1:8766，不发布到局域网或公网。默认端口8766；冲突时首次安装加`--port 8876`等空闲端口，启动器会显示实际网址。配置保存在server-config.json，升级保留。

## 准备

- Python 3.10–3.12（建议3.12）。缺少时由目标Agent通过该设备已有的包管理器或Python官方安装程序补齐，再运行安装器；不改系统Python。
- Windows x64；macOS Apple Silicon或Intel，须有相应Python/依赖轮子。建议16GB以上内存和至少8GB可用磁盘，GPU环境另预留数GB依赖空间。实际速度以录音实测为准。
- Windows可选NVIDIA CUDA。安装器会在**自己的venv**安装PyTorch cu128轮子提供运行库，仍需系统GPU驱动；不从其他项目借DLL。该可选新安装路径尚须目标机实测。
- macOS默认CPU int8，不提供CUDA/MPS/Metal加速。CPU turbo采用12秒分段降低频繁推理负担；这也意味着约12秒收音等待，再加推理和分析间隔，并非逐字零延迟。

## 安装命令

将整个Skill目录解压；下例在Skill目录执行，目标目录可更换。`python`/`python3`应指向上述支持版本。

Windows PowerShell：
```powershell
python scripts/install.py --target "$env:USERPROFILE/EnterpriseAIFieldwork" --plan
python scripts/install.py --target "$env:USERPROFILE/EnterpriseAIFieldwork"
& "$env:USERPROFILE/EnterpriseAIFieldwork/.venv/Scripts/python.exe" "$env:USERPROFILE/EnterpriseAIFieldwork/doctor.py" --load-model
& "$env:USERPROFILE/EnterpriseAIFieldwork/.venv/Scripts/python.exe" "$env:USERPROFILE/EnterpriseAIFieldwork/run.py"
```

Mac Terminal（建议使用原生架构Python，不在Apple Silicon上混用Rosetta环境）：
```bash
python3 scripts/install.py --target "$HOME/EnterpriseAIFieldwork" --plan
python3 scripts/install.py --target "$HOME/EnterpriseAIFieldwork"
"$HOME/EnterpriseAIFieldwork/.venv/bin/python" "$HOME/EnterpriseAIFieldwork/doctor.py" --load-model
"$HOME/EnterpriseAIFieldwork/.venv/bin/python" "$HOME/EnterpriseAIFieldwork/run.py"
```

安装后可双击Windows的`启动现场助手.cmd`。Mac可从Terminal运行`bash 启动现场助手.command`，或在系统允许时双击。操作系统提示权限时由用户正常授权，不关闭Gatekeeper/TCC。Terminal窗口需要保持运行，可最小化并切换其他软件；无需输入框焦点。

可选：Windows适配NVIDIA硬件时首次安装加`--device cuda`；普通话轻量测试加`--model small --language zh`。已有ASR配置会保留，升级时参数应与其一致。安装器`--skip-deps`/`--skip-model`仅用于离线分步或测试，使用后不能声称完整可录音。

模型下载失败：检查网络、目标设备代理及Hugging Face访问，不无限重试。可先在联网设备获取可信CTranslate2目录，再传入`--model-source <本地模型目录>`，至少包含model.bin/config.json/tokenizer.json。不要将模型权重或venv塞进Skill ZIP。

## 配置

页面“分析模型设置”填写base URL、模型名称和API密钥，然后保存启用。默认示例为DeepSeek的`https://api.deepseek.com`、`deepseek-flash`；其他兼容服务替换对应值。地址不要包含`/chat/completions`，程序会追加。服务必须支持Chat Completions流式文本；默认要求JSON mode，不支持时在`analysis-config.json`中设`json_mode:false`（仍需模型输出合法JSON）。不能把厂商网站展示名直接猜作API模型ID。

API密钥只存在部署目录`analysis-config.json`，网页不回显。Mac/Linux文件0600；Windows安装器限制该文件ACL为当前用户与SYSTEM。密钥不作为Skill文件或迁移示例分发。

`asr-config.json`可调整：
```json
{"device":"cpu","model_name":"turbo","model_path":"models/turbo","language":"yue","cpu_threads":4,"chunk_seconds":12,"input_device":null}
```
`input_device:null`使用系统默认输入；`doctor.py`列出可用设备索引，可选真实麦克风，避免Steam等虚拟设备。language设`null`可自动识别，`zh`为中文，`yue`只用于支持该token的模型。更换模型路径前先安装对应权重并自检。

## 停止、升级与迁移

先点停止录音；也可在另一终端以部署venv运行`run.py --stop`，安全停止录音与服务。Ctrl+C会走停止流程，强制结束/关机不保证尾段保存。

升级前停止服务，重新执行同一安装命令；程序旧版放`backups/时间戳`，API、ASR配置、企业资料、transcripts/results保留。重装前先用目标目录manifest确认是本程序，不在其他项目目录硬装。安装器仅更新代码，不替换已有企业信息。

迁移业务资料时只复制用户需要的research、meeting-brief文件、verification-checklist、transcripts和results；原机器的venv不可直接跨平台复制。API密钥由用户在新机器重新填。仅迁移模板时，不携带真实客户会话。

## 技术依据（2026-11-09核对）

- CTranslate2支持Windows x64、macOS x64/ARM64，Mac CPU采用相应底层库：[安装文档](https://opennmt.net/CTranslate2/installation.html)、[硬件文档](https://opennmt.net/CTranslate2/hardware_support.html)。
- sounddevice在Windows/macOS通过pip安装时包含PortAudio：[安装文档](https://python-sounddevice.readthedocs.io/en/latest/installation.html)。
- Mac麦克风在“系统设置→隐私与安全性→麦克风”授权实际启动程序：[Apple说明](https://support.apple.com/en-tj/guide/mac-help/mchla1b1e1fe/mac)。
- GPU可选依赖来自[PyTorch官方索引](https://pytorch.org/get-started/locally/)，目标机驱动兼容性须另测。
