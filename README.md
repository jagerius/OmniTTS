<p align="center">
  <a href="README.md">🇬🇧 English</a> •
  <a href="README_pl.md">🇵🇱 Polski</a> •
  <a href="README_de.md">🇩🇪 Deutsch</a> •
  <a href="README_es.md">🇪🇸 Español</a> •
  <a href="README_ru.md">🇷🇺 Русский</a> •
  <a href="README_cs.md">🇨🇿 Čeština</a> •
  <a href="README_uk.md">🇺🇦 Українська</a> •
  <a href="README_zh.md">🇨🇳 中文</a> •
  <a href="README_ja.md">🇯🇵 日本語</a>
</p>

# OmniTTS for SkyrimNet

## Description
OmniTTS is a high-performance, drop-in text-to-speech (TTS) module replacing the default Chatterbox engine in SkyrimNet. It integrates the cutting-edge OmniVoice diffusion-based TTS natively to provide realistic, dynamic voice cloning and dialogue generation for Skyrim NPCs. It performs all generation locally via a Gradio backend, specifically engineered to be seamlessly compatible with the SkyrimNet C++ client.

## Installation
1. Navigate to the `OmniTTS` directory inside your SkyrimNet installation.
2. Run `setup_venv.bat` (Windows). This script will automatically create a Python virtual environment and install all necessary dependencies, including PyTorch with CUDA support.
3. Make sure to provide voice sample `.wav` files inside the `speakers/` directory for character voice cloning.
4. **Important for Windows users**: OmniVoice requires the `torchcodec` library, which relies on a full installation of FFmpeg. 
   - Download the full FFmpeg build from [BtBN FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds/releases).
   - Extract the contents and rename the folder to `ffmpeg`.
   - Place this `ffmpeg` folder directly inside the parent directory (`SkyrimNetOmniVoice`), or inside `OmniTTS`, so that the path `ffmpeg/bin` exists. OmniTTS will automatically detect and load the FFmpeg DLLs to prevent crashes.

> [!NOTE]
> By default, OmniTTS requires an NVIDIA graphics card to run (it uses CUDA acceleration). If you do not have a compatible GPU, you can force it to run on your processor (CPU) by setting `use_cpu = true` in the `omnitts_config.txt` file (note: generation will be significantly slower).

## Usage
1. To start the TTS server, run `Start.bat`. This will launch a local Gradio server endpoint on port 8000.
2. The server will actively listen for API requests from the SkyrimNet GamePlugin. 
3. When interacting with an NPC in Skyrim, SkyrimNet will send the text, and OmniTTS will generate the dialogue and provide back the audio path.

## Configuration (`omnitts_config.txt`)
The `omnitts_config.txt` file allows you to fine-tune generation metrics and performance. The following parameters can be adjusted:
* **`guidance_scale`**: Defines how closely the AI adheres to the voice prompt and the text. (Higher = stricter adherence).
* **`num_step`**: Inference steps for the diffusion model. Lowering this value (e.g., 12 or 16) results in massive speedups at a minor cost to quality.
* **`speed`**: Controls the speaking speed of the NPC.
* **`denoise`**: Enables a denoising token for cleaner audio output (recommended to keep `true`).
* **`audio_chunk_threshold` & `audio_chunk_duration`**: Prevents the TTS from cutting off during long sentences by breaking down extensive dialogue strings into smaller, digestible audio chunks.
* **`model_path`**: Specifies the HuggingFace repository or local path for the OmniVoice model.
* **`enable_memory_cache` & `enable_disk_cache`**: Caches voice clone prompts to massively drastically speed up inference when conversing with the same NPC repeatedly.

## Credits
* **OmniVoice**: This project utilizes the cutting-edge OmniVoice TTS model available at [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice).
* **Chatterbox**: The integration and API structure are heavily based on the [langfod/chatterbox](https://github.com/langfod/chatterbox) plugin.
