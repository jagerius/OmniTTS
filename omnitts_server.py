"""
OmniTTS Server — SkyrimNet-compatible TTS using OmniVoice.

Drop-in replacement for SkyrimNet_CHATTERBOX. Exposes an identical Gradio API
endpoint (/api/generate_audio) with the same 28-parameter signature so that
the SkyrimNet C++ DLL sees no difference.

Usage:
    python omnitts_server.py --server 0.0.0.0 --port 7860
"""

import os
import sys
import re
import gc
from argparse import ArgumentParser
from pathlib import Path
from time import perf_counter_ns

import gradio as gr
import torch
from loguru import logger

# ---------------------------------------------------------------------------
# Add OmniVoice to Python path
# ---------------------------------------------------------------------------
OMNIVOICE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "OmniVoice")
if os.path.isdir(OMNIVOICE_DIR):
    sys.path.insert(0, OMNIVOICE_DIR)

from omnivoice import OmniVoice, OmniVoiceGenerationConfig

from config_utils import get_tts_params, load_config, DEFAULTS
from audio_cache import (
    get_cache_key,
    load_prompt_cache,
    save_prompt_cache,
    save_wav,
    clear_output_directories,
    clear_cache_files,
)

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------
START_DIRECTORY = Path.cwd()

_initial_config = load_config()
_use_cpu_override = _initial_config.get("use_cpu", "false").lower() == "true"

# Check for --device in launch args early
_custom_device = "cuda:0"
if "--device" in sys.argv:
    try:
        _custom_device = sys.argv[sys.argv.index("--device") + 1]
    except IndexError:
        pass

# Force CUDA if available
if torch.cuda.is_available() and not _use_cpu_override:
    DEVICE = _custom_device
    DTYPE = torch.bfloat16
    logger.info(f"CUDA available: {torch.cuda.get_device_name(DEVICE)} (Using device: {DEVICE}) (VRAM: {torch.cuda.get_device_properties(DEVICE).total_memory / 1024**3:.1f} GB)")
else:
    DEVICE = "cpu"
    DTYPE = torch.float32
    if _use_cpu_override:
        logger.info("Running on CPU as requested by use_cpu=true in config.")
    else:
        logger.warning("CUDA NOT available! Running on CPU. Check your PyTorch installation:")
        logger.warning(f"  torch version: {torch.__version__}")
        logger.warning(f"  torch.cuda.is_available(): {torch.cuda.is_available()}")
        logger.warning("  Install CUDA PyTorch: pip install torch --extra-index-url https://download.pytorch.org/whl/cu128")

MODEL: OmniVoice = None
IGNORE_PING = None
SILENCE_AUDIO_PATH = str(START_DIRECTORY / "assets" / "silence_100ms.wav")
CACHE_DIR = START_DIRECTORY / "cache"


# ---------------------------------------------------------------------------
# Language code mapping (Chatterbox 2-letter → OmniVoice name)
# ---------------------------------------------------------------------------
LANG_CODE_TO_NAME = {
    "ar": "Arabic", "da": "Danish", "de": "German", "el": "Greek",
    "en": "English", "es": "Spanish", "fi": "Finnish", "fr": "French",
    "he": "Hebrew", "hi": "Hindi", "it": "Italian", "ja": "Japanese",
    "ko": "Korean", "ms": "Malay", "nl": "Dutch", "no": "Norwegian",
    "pl": "Polish", "pt": "Portuguese", "ru": "Russian", "sv": "Swedish",
    "sw": "Swahili", "tr": "Turkish", "zh": "Chinese",
}


def resolve_language(lang_code: str | None) -> str | None:
    """Convert a 2-letter language code to OmniVoice language name."""
    if lang_code is None:
        return None
    code = lang_code.strip().lower()
    if code in LANG_CODE_TO_NAME:
        return LANG_CODE_TO_NAME[code]
    # If it's already a full name or unknown, pass through
    return lang_code


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------
def load_model():
    """Load the OmniVoice model."""
    global MODEL
    from config_utils import get_tts_params
    params = get_tts_params()

    model_path = params.get("model_path", DEFAULTS["model_path"])
    load_asr = params.get("load_asr_model", False)

    logger.info(f"Loading OmniVoice from: {model_path}")
    logger.info(f"Device: {DEVICE}, Dtype: {DTYPE}, Load ASR: {load_asr}")

    if params.get("enable_tf32", True) and torch.cuda.is_available():
        logger.info("Enabling TF32 optimizations")
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.set_float32_matmul_precision('high')

    attn_backend = params.get("attention_backend", "default").lower().strip()
    if attn_backend == "sage":
        logger.warning("SageAttention is currently not supported with OmniVoice on Windows. "
                       "Falling back to PyTorch default SDPA (which already uses FlashAttention when available).")
        attn_backend = "default"
    
    if attn_backend == "sdpa":
        # PyTorch 2.x uses SDPA (including FlashAttention) by default.
        # No monkey-patching needed — just log it.
        logger.info("Attention backend: PyTorch SDPA (FlashAttention enabled by default on compatible GPUs)")
    else:
        logger.info(f"Attention backend: {attn_backend} (PyTorch will choose automatically)")

    MODEL = OmniVoice.from_pretrained(
        model_path,
        device_map=DEVICE,
        torch_dtype=DTYPE,
        load_asr=load_asr,
        asr_model_name="openai/whisper-base" if load_asr else None,
    )

    if params.get("enable_torch_compile", True):
        logger.info("Applying torch.compile to MODEL to boost performance (this may take a minute on first run)")
        try:
            compiled_something = False
            if hasattr(MODEL, 'llm'):
                MODEL.llm = torch.compile(MODEL.llm)
                compiled_something = True
            if hasattr(MODEL, 'flow'):
                MODEL.flow = torch.compile(MODEL.flow)
                compiled_something = True
            
            if not compiled_something:
                MODEL = torch.compile(MODEL)
        except Exception as e:
            logger.warning(f"Failed to apply torch.compile: {e}. Running without compile.")

    logger.info(f"Model loaded. Sampling rate: getattr(MODEL, 'sampling_rate', 24000) Hz")
    
    return MODEL


# ---------------------------------------------------------------------------
# Voice clone prompt caching
# ---------------------------------------------------------------------------
def get_cached_prompt(audio_path: str | None):
    """Get or create a VoiceClonePrompt with memory/disk caching."""
    if not audio_path or not Path(audio_path).is_file():
        if audio_path:
            logger.warning(f"Speaker audio file not found or invalid: {audio_path}. Falling back to default voice.")
        return None

    config = load_config()
    enable_memory = config.get("enable_memory_cache", "true").lower() != "false"
    enable_disk = config.get("enable_disk_cache", "true").lower() != "false"

    cache_key = get_cache_key(audio_path)
    if cache_key and (enable_memory or enable_disk):
        cached = load_prompt_cache(cache_key, CACHE_DIR, enable_memory, enable_disk)
        if cached is not None:
            return cached

    # Create new voice clone prompt
    logger.info(f"Creating voice clone prompt from: {Path(audio_path).name}")
    try:
        from config_utils import get_tts_params
        if not get_tts_params().get("load_asr_model", False):
            logger.warning(f"load_asr_model=False, but generating prompt for new voice {Path(audio_path).name}! "
                           "This may crash if OmniVoice tries to load ASR on the fly or requires ref_text.")
        prompt = MODEL.create_voice_clone_prompt(
            ref_audio=audio_path,
            ref_text=None,  # Auto-transcribe with Whisper
            preprocess_prompt=True,
        )
    except ValueError as e:
        if "empty after silence removal" in str(e):
            logger.warning(f"Reference audio empty after silence removal, retrying without preprocessing: {e}")
            prompt = MODEL.create_voice_clone_prompt(
                ref_audio=audio_path,
                ref_text=None,
                preprocess_prompt=False,
            )
        else:
            raise

    if cache_key and (enable_memory or enable_disk):
        save_prompt_cache(cache_key, prompt, CACHE_DIR, enable_memory, enable_disk)

    return prompt


# ---------------------------------------------------------------------------
# Core generation (internal)
# ---------------------------------------------------------------------------
def generate_tts(text: str, speaker_audio: str | None, language: str = "en",
                 cfg_scale=None, speaking_rate=None) -> str:
    """
    Generate speech with OmniVoice and return the relative WAV path.
    """
    global MODEL
    if MODEL is None:
        load_model()

    func_start = perf_counter_ns()

    # Resolve parameters from config
    params = get_tts_params(payload_params={
        "cfg_scale": cfg_scale,
        "speaking_rate": speaking_rate,
    })

    # Get or create VoiceClonePrompt
    voice_prompt = get_cached_prompt(speaker_audio)

    # Resolve language
    lang = resolve_language(language)

    # Build generation config
    gen_config = OmniVoiceGenerationConfig(
        num_step=int(params["num_step"]),
        guidance_scale=float(params["guidance_scale"]),
        denoise=bool(params["denoise"]),
        postprocess_output=bool(params["postprocess_output"]),
        audio_chunk_threshold=float(params["audio_chunk_threshold"]),
        audio_chunk_duration=float(params["audio_chunk_duration"]),
    )

    # Generate
    logger.info(f'Generating: "{text[:80]}..." lang={lang} speaker={Path(speaker_audio).name if speaker_audio else "None"}')

    speed_val = float(params["speed"])
    try:
        audios = MODEL.generate(
            text=text,
            language=lang,
            voice_clone_prompt=voice_prompt,
            speed=speed_val if speed_val != 1.0 else None,
            generation_config=gen_config,
        )

        # Save first audio result
        audio_tensor = audios[0]
        
        if audio_tensor.numel() == 0:
            logger.warning(f"Model generated empty audio for text: '{text}'. Using silence fallback.")
            wav_path = Path(SILENCE_AUDIO_PATH).absolute()
            audio_len_s = 0.0
        else:
            wav_path = save_wav(audio_tensor, MODEL.sampling_rate, speaker_audio)
            audio_len_s = audio_tensor.shape[-1] / MODEL.sampling_rate

        # Log timing
        elapsed_s = (perf_counter_ns() - func_start) / 1_000_000_000
        
        speed_factor = (audio_len_s / elapsed_s) if elapsed_s > 0 else 0.0
        logger.info(f"Generated audio: {audio_len_s:.2f}s @ {MODEL.sampling_rate/1000:.0f}kHz "
                    f"in {elapsed_s:.2f}s. Speed: {speed_factor:.2f}x")

        del audios
        return str(wav_path)
    except Exception as e:
        logger.exception(f"CRITICAL ERROR during MODEL.generate or save_wav: {e}")
        raise
    finally:
        # VRAM Leak Fix: Smart garbage collection based on threshold
        if DEVICE.startswith("cuda") and torch.cuda.is_available():
            vram_limit_gb = float(params.get("vram_cleanup_threshold_gb", 3.0))
            reserved_gb = torch.cuda.memory_reserved(DEVICE) / (1024**3)
            
            if reserved_gb > vram_limit_gb:
                logger.info(f"VRAM reserved ({reserved_gb:.2f} GB) exceeded limit ({vram_limit_gb} GB). Clearing cache...")
                gc.collect()
                torch.cuda.empty_cache()


# ---------------------------------------------------------------------------
# SkyrimNet-compatible API function
# ---------------------------------------------------------------------------
def generate_audio(
    model_choice=None,
    text="Hello adventurer, welcome to Whiterun.",
    language="en",
    speaker_audio=None,
    prefix_audio=None,
    e1=None, e2=None, e3=None, e4=None,
    e5=None, e6=None, e7=None, e8=None,
    vq_single=None,
    fmax=None,
    pitch_std=None,
    speaking_rate=None,
    dnsmos_ovrl=None,
    speaker_noised: bool = None,
    cfg_scale=0.3,
    top_p=1.0,
    top_k=None,
    min_p=0.5,
    linear=None,
    confidence=None,
    quadratic=None,
    job_id=-1,
    randomize_seed: bool = False,
    unconditional_keys: list = None,
):
    """
    SkyrimNet-compatible generate_audio endpoint.

    This function signature EXACTLY matches the Chatterbox server's generate_audio()
    so that the SkyrimNet C++ DLL can call it without any changes.
    """
    global IGNORE_PING

    # Handle Gradio audio dict format
    if isinstance(speaker_audio, dict) and "path" in speaker_audio:
        speaker_audio = speaker_audio["path"]
    elif isinstance(speaker_audio, str) and speaker_audio.strip().startswith("{") and "'path':" in speaker_audio:
        import ast
        try:
            parsed = ast.literal_eval(speaker_audio)
            if isinstance(parsed, dict) and 'path' in parsed:
                speaker_audio = parsed['path']
        except Exception:
            pass
            
    # Clean up any potential garbage chars from string to be safe on Windows
    if isinstance(speaker_audio, str) and (":" in speaker_audio[2:] or "{" in speaker_audio):
        logger.warning(f"speaker_audio seems invalid or raw dict string. Clearing it to avoid file system error: {speaker_audio[:50]}")
        speaker_audio = None

    # --- Sanitize text from Universal Translator ---
    # Universal Translator czesto wysyla tekst ze znakami nowej linii (\n), 
    # co powoduje ucinanie generacji przez model teksowy wewnatrz OmniVoice.
    original_text_len = len(text)
    text = text.replace('\r', ' ').replace('\n', ' ').replace('|', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) != original_text_len or "\n" in text:
        logger.info("Zoptymalizowano tekst wejsciowy (usunieto \\n).")

    logger.info(f"inputs: text={text[:60]}, language={language}, "
                f"speaker_audio={Path(speaker_audio).stem if speaker_audio else 'None'}, "
                f"seed={job_id}")

    # --- Ping handling (heartbeat from SkyrimNet) ---
    if text == "ping":
        if IGNORE_PING is None:
            IGNORE_PING = "pending"
        else:
            logger.info("Ping request received, sending silence audio.")
            return SILENCE_AUDIO_PATH, job_id

    # --- Generate audio ---
    wav_out = generate_tts(
        text=text,
        speaker_audio=speaker_audio,
        language=language,
        cfg_scale=cfg_scale,
        speaking_rate=speaking_rate,
    )

    # Handle first-run ping
    if IGNORE_PING == "pending":
        IGNORE_PING = True
        logger.info(f"First generation complete (ping pending): {wav_out}")
        Path(wav_out).unlink(missing_ok=True)
        wav_out = SILENCE_AUDIO_PATH

    return wav_out, job_id


# ---------------------------------------------------------------------------
# Gradio UI + API
# ---------------------------------------------------------------------------
with gr.Blocks() as demo:

    gr.set_static_paths(["assets", "cache", "output_temp"])

    # --- Visible UI ---
    with gr.Row():
        with gr.Column():
            text = gr.Textbox(
                value="Hello adventurer, welcome to Whiterun. The guards have been talking about you.",
                label="Text to synthesize",
                lines=5,
            )
            ref_wav = gr.Audio(
                sources=["upload", "microphone"],
                type="filepath",
                label="Reference Audio File",
                value=None,
            )
            with gr.Accordion("OmniVoice Settings", open=False):
                guidance_scale_slider = gr.Slider(
                    0.0, 4.0, step=0.1, label="Guidance Scale (CFG)",
                    value=2.0,
                )
                num_step_slider = gr.Slider(
                    4, 64, step=4, label="Diffusion Steps (quality vs speed)",
                    value=32,
                )
                speed_slider = gr.Slider(
                    0.7, 1.3, step=0.05, label="Speaking Speed",
                    value=1.0,
                )
            seed_num = gr.Number(value=0, label="Job ID / Seed")
            run_btn = gr.Button("Generate", variant="primary")

        with gr.Column():
            audio_output = gr.Audio(
                label="Output Audio", type="filepath", autoplay=True,
            )

    # Visible button click → direct generate
    run_btn.click(
        fn=lambda txt, ref, gs, ns, spd, sid: generate_tts(txt, ref, "en", gs, spd),
        inputs=[text, ref_wav, guidance_scale_slider, num_step_slider,
                speed_slider, seed_num],
        outputs=audio_output,
    )

    # --- Hidden inputs for SkyrimNet C++ DLL API compatibility ---
    # These MUST match the exact Chatterbox signature
    model_choice = gr.Textbox(visible=False)
    language = gr.Textbox(visible=False)
    speaker_audio = gr.Textbox(visible=False)
    prefix_audio = gr.Textbox(visible=False)
    emotion1 = gr.Number(visible=False)
    emotion2 = gr.Number(visible=False)
    emotion3 = gr.Number(visible=False)
    emotion4 = gr.Number(visible=False)
    emotion5 = gr.Number(visible=False)
    emotion6 = gr.Number(visible=False)
    emotion7 = gr.Number(visible=False)
    emotion8 = gr.Number(visible=False)
    vq_single = gr.Number(visible=False)
    fmax = gr.Number(visible=False)
    pitch_std = gr.Number(visible=False)
    speaking_rate = gr.Number(visible=False)
    dnsmos = gr.Number(visible=False)
    speaker_noised_checkbox = gr.Checkbox(visible=False)
    cfg_scale = gr.Number(visible=False)
    top_p = gr.Number(visible=False)
    min_k = gr.Number(visible=False)
    min_p = gr.Number(visible=False)
    linear = gr.Number(visible=False)
    confidence = gr.Number(visible=False)
    quadratic = gr.Number(visible=False)
    randomize_seed_toggle = gr.Checkbox(visible=False)
    unconditional_keys = gr.Textbox(visible=False)

    # --- Hidden API button (the actual endpoint SkyrimNet calls) ---
    hidden_btn = gr.Button(visible=False)
    hidden_btn.click(
        fn=generate_audio,
        api_name="generate_audio",
        inputs=[
            model_choice,
            text,
            language,
            speaker_audio,
            prefix_audio,
            emotion1, emotion2, emotion3, emotion4,
            emotion5, emotion6, emotion7, emotion8,
            vq_single, fmax, pitch_std, speaking_rate, dnsmos,
            speaker_noised_checkbox,
            cfg_scale, top_p, min_k, min_p,
            linear, confidence, quadratic,
            seed_num,
            randomize_seed_toggle,
            unconditional_keys,
        ],
        outputs=[audio_output, seed_num],
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_arguments():
    parser = ArgumentParser(description="OmniTTS Server for SkyrimNet")
    parser.add_argument("--share", action="store_true",
                        help="Create a public Gradio link")
    parser.add_argument("--server", type=str, default="0.0.0.0",
                        help="Server address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=7860,
                        help="Port (default: 7860)")
    parser.add_argument("--inbrowser", action="store_true",
                        help="Open browser on launch")
    parser.add_argument("--clearoutput", action="store_true",
                        help="Clear output directories and exit")
    parser.add_argument("--clearcache", action="store_true",
                        help="Clear cache files and exit")
    parser.add_argument("--device", type=str, default="cuda:0",
                        help="CUDA device to use (e.g., cuda:0, cuda:1)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    if args.clearoutput:
        count = clear_output_directories()
        logger.info(f"Cleared {count} output directories.")
        sys.exit(0)

    if args.clearcache:
        count = clear_cache_files()
        logger.info(f"Cleared {count} cache files.")
        sys.exit(0)

    import atexit
    atexit.register(clear_output_directories)

    # Load model at startup
    logger.info("=" * 60)
    logger.info("  OmniTTS Server for SkyrimNet")
    logger.info("  Powered by OmniVoice (k2-fsa)")
    logger.info("=" * 60)

    load_model()

    # Allowed paths: let Gradio serve files from these directories
    # This fixes Gradio 5.x InvalidPathError for speaker files and output audio
    allowed = [
        str(START_DIRECTORY),
        str(START_DIRECTORY / "assets"),
        str(START_DIRECTORY / "speakers"),
        str(START_DIRECTORY / "output_temp"),
        str(START_DIRECTORY / "cache"),
    ]
    # Also allow the parent directory (for speaker paths that might be absolute)
    allowed.append(str(START_DIRECTORY.parent))

    demo.queue(
        max_size=50,
        default_concurrency_limit=2,  # Zmniejszono z 4 do 2, by zapobiec opóźnieniom i timeoutom klienta
    ).launch(
        server_name=args.server,
        server_port=args.port,
        share=args.share,
        inbrowser=args.inbrowser,
        allowed_paths=allowed,
    )
