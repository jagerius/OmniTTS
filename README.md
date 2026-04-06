# OmniTTS for SkyrimNet

## Description
OmniTTS is a high-performance, drop-in text-to-speech (TTS) module replacing the default Chatterbox engine in SkyrimNet. It integrates the cutting-edge OmniVoice diffusion-based TTS natively to provide realistic, dynamic voice cloning and dialogue generation for Skyrim NPCs. It performs all generation locally via a Gradio backend, specifically engineered to be seamlessly compatible with the SkyrimNet C++ client.

## Installation
1. Navigate to the `OmniTTS` directory inside your SkyrimNet installation.
2. Run `setup_venv.bat` (Windows). This script will automatically create a Python virtual environment and install all necessary dependencies, including PyTorch with CUDA support.
3. Make sure to provide voice sample `.wav` files inside the `speakers/` directory for character voice cloning.

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
