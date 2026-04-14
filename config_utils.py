"""
Configuration utilities for OmniTTS.

Reads omnitts_config.txt and resolves parameter values:
  - "default" → use built-in OmniVoice defaults
  - "api"     → use the value sent from SkyrimNet UI
  - <number>  → use that literal value
"""

from pathlib import Path
from loguru import logger

# Built-in OmniVoice defaults
DEFAULTS = {
    "guidance_scale": 2.0,
    "num_step": 24,
    "speed": 1.0,
    "denoise": True,
    "postprocess_output": True,
    "audio_chunk_threshold": 10.0,
    "audio_chunk_duration": 10.0,
    "model_path": "k2-fsa/OmniVoice",
    "enable_memory_cache": True,
    "enable_disk_cache": True,
    "use_cpu": False,
    "enable_tf32": True,
    "enable_torch_compile": True,
    "attention_backend": "sdpa",
    "vram_cleanup_threshold_gb": 3.0,
    "load_asr_model": False,
}

_config_cache: dict | None = None


def _parse_bool(val: str) -> bool:
    return val.strip().lower() in ("true", "1", "yes")


def _parse_value(val: str):
    """Try to parse a config value as float, bool, or leave as string."""
    v = val.strip().lower()
    if v in ("true", "false"):
        return _parse_bool(val)
    try:
        return float(val)
    except ValueError:
        return val.strip()


def load_config(config_path: str | Path | None = None) -> dict:
    """Load and parse omnitts_config.txt. Returns dict of key → raw string value."""
    if config_path is None:
        config_path = Path(__file__).parent / "omnitts_config.txt"
    else:
        config_path = Path(config_path)

    raw = {}
    if config_path.exists():
        for line in config_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, val = line.partition("=")
            raw[key.strip().lower()] = val.strip()
    else:
        logger.warning(f"Config file not found: {config_path}, using defaults")

    return raw


def get_tts_params(payload_params: dict | None = None) -> dict:
    """
    Resolve final TTS parameters by merging config file settings with API payload.

    For each parameter:
      - config says "default" → use DEFAULTS
      - config says "api"    → use payload_params value (from SkyrimNet UI)
      - config says a number → use that number
      - config not set       → use DEFAULTS

    Args:
        payload_params: dict with keys like 'cfg_scale', 'speaking_rate' from SkyrimNet.
                         Maps: cfg_scale→guidance_scale, speaking_rate→speed.

    Returns:
        dict with final OmniVoice generation parameters.
    """
    raw = load_config()
    payload = payload_params or {}

    # Map SkyrimNet UI param names → OmniVoice param names
    api_map = {
        "guidance_scale": payload.get("cfg_scale"),
        "speed": payload.get("speaking_rate"),
    }

    result = {}
    for key, default_val in DEFAULTS.items():
        raw_val = raw.get(key, "default").strip().lower()

        if raw_val == "default":
            result[key] = default_val
        elif raw_val == "api":
            api_val = api_map.get(key)
            if api_val is not None:
                try:
                    if isinstance(default_val, bool):
                        result[key] = _parse_bool(str(api_val))
                    elif isinstance(default_val, float):
                        result[key] = float(api_val)
                    elif isinstance(default_val, int):
                        result[key] = int(float(api_val))
                    else:
                        result[key] = str(api_val)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid API value for {key}: {api_val}, using default")
                    result[key] = default_val
            else:
                result[key] = default_val
        else:
            result[key] = _parse_value(raw_val)

    # Ensure correct types
    result["guidance_scale"] = float(result["guidance_scale"])
    result["num_step"] = int(result["num_step"])
    result["speed"] = float(result["speed"])
    result["denoise"] = bool(result["denoise"])
    result["postprocess_output"] = bool(result["postprocess_output"])
    result["audio_chunk_threshold"] = float(result["audio_chunk_threshold"])
    result["audio_chunk_duration"] = float(result["audio_chunk_duration"])
    result["use_cpu"] = bool(result["use_cpu"])
<<<<<<< HEAD
    result["max_memory_prompts"] = int(result["max_memory_prompts"])
    result["enable_tf32"] = bool(result["enable_tf32"])
    result["enable_torch_compile"] = bool(result["enable_torch_compile"])
    result["attention_backend"] = str(result["attention_backend"]).lower().strip()
    result["vram_cleanup_threshold_gb"] = float(result["vram_cleanup_threshold_gb"])
    result["load_asr_model"] = bool(result["load_asr_model"])
=======
>>>>>>> parent of 4f9d431 (feat: implement LRU memory cache limit for voice prompts and optimize VRAM management with garbage collection and CUDA cache clearing)

    return result
