# SkyrimNet OmniTTS

## 简介 (Description)
OmniTTS 是一款高性能文本转语音 (TTS) 模块，用来替换 SkyrimNet 的默认 Chatterbox 引擎。它原生集成了先进的基于扩散机制的 OmniVoice TTS 模型，可为上古卷轴 (Skyrim) 中的 NPC 提供极为逼真、动态的语音克隆与对话生成功能。所有的推理生成直接通过本地 Gradio 后端实现，与 SkyrimNet 的 C++ 客户端完全对接兼容。

## 安装指南 (Installation)
1. 进入 SkyrimNet 安装目录下的 `OmniTTS` 文件夹。
2. 运行 `setup_venv.bat` 脚本（Windows系统）。该脚本将自动创建 Python 虚拟环境，并安装包括支持 CUDA 的 PyTorch 等所有必需依赖库。
3. 请确保将目标 NPC 的语音参考样本 `.wav` 文件放置在 `speakers/` 目录中。

## 使用方法 (Usage)
1. 想启动此 TTS 服务器时，请双击运行 `Start.bat`。此操作将在本地 8000 端口启动 Gradio 服务器。
2. 本地服务器将全自动监听来自 SkyrimNet GamePlugin 插件发送出的 API 请求。
3. 当在游戏中与 NPC 互动时，SkyrimNet 会向你部署好的服务发送文本，随后 OmniTTS 会生成语音文件并将其路径返还至客户端直接播放。

## 配置文件 (`omnitts_config.txt`)
`omnitts_config.txt` 文件允许您对生成的语音质量和性能进行微调控制，包含如下内容：
* **`guidance_scale`**: 控制生成质量与给定语音模板（和文本）的贴合度。
* **`num_step`**: 扩散模型的渲染推理步数。适当降低（如调到 12 步）能大幅加快生成速度，虽然会伴随极其微小的音质下降。
* **`speed`**: 用于调整 NPC 的说话语速。
* **`denoise`**: 是否对生成的最终音频应用降噪清除回音瑕疵（推荐保持为 `true`）。
* **`audio_chunk_threshold` & `audio_chunk_duration`**: 通过将大段长的对话串分解转化为多个较小的可消化音频片段，防止超长句子生成因为显存爆炸而中断切分。
* **`model_path`**: 定义从 HuggingFace 还是本地绝对路径加载 OmniVoice 大模型。
* **`enable_memory_cache` & `enable_disk_cache`**: 对同一 NPC 多次交谈时，利用缓存克隆语音属性以极大地提高了音频生成响应的时间。
