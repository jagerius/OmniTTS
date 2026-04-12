"""
Audio cache and WAV output management for OmniTTS.

Handles:
  - VoiceClonePrompt caching (memory + disk)
  - WAV file saving to output_temp/
  - Cache key generation from speaker audio paths
"""

import hashlib
import os
from pathlib import Path
from time import time

import soundfile as sf
import torch
from loguru import logger

START_DIRECTORY = Path.cwd()

# In-memory VoiceClonePrompt cache
_memory_cache = {}


def get_cache_key(audio_path: str | None) -> str | None:
    """Generate a cache key from the speaker audio file path."""
    if not audio_path:
        return None
    p = Path(audio_path)
    if not p.is_file():
        return None
    # Use filename + file size + mtime as cache key
    stat = p.stat()
    raw = f"{p.name}_{stat.st_size}_{stat.st_mtime}"
    return hashlib.md5(raw.encode()).hexdigest()


def load_prompt_cache(cache_key: str, cache_dir: Path,
                      enable_memory: bool = True,
                      enable_disk: bool = True):
    """Load a VoiceClonePrompt from memory or disk cache."""
    if enable_memory and cache_key in _memory_cache:
        logger.debug(f"Cache hit (memory): {cache_key}")
        return _memory_cache[cache_key]

    if enable_disk:
        disk_path = cache_dir / f"{cache_key}.pt"
        if disk_path.exists():
            try:
                prompt = torch.load(disk_path, weights_only=False)
                if enable_memory:
                    _memory_cache[cache_key] = prompt

                logger.debug(f"Cache hit (disk): {cache_key}")
                return prompt
            except Exception as e:
                logger.warning(f"Failed to load disk cache {disk_path}: {e}")

    return None


def save_prompt_cache(cache_key: str, prompt, cache_dir: Path,
                      enable_memory: bool = True,
                      enable_disk: bool = True):
    """Save a VoiceClonePrompt to memory and/or disk cache."""
    if enable_memory:
        _memory_cache[cache_key] = prompt

    if enable_disk:
        cache_dir.mkdir(parents=True, exist_ok=True)
        disk_path = cache_dir / f"{cache_key}.pt"
        try:
            torch.save(prompt, disk_path)
            logger.debug(f"Saved to disk cache: {disk_path}")
        except Exception as e:
            logger.warning(f"Failed to save disk cache {disk_path}: {e}")


def save_wav(audio_tensor: torch.Tensor, sample_rate: int,
             audio_prompt_path: str | None = None,
             target_sample_rate: int = 44100) -> Path:
    """
    Save generated audio to output_temp/ directory.

    Returns the path relative to START_DIRECTORY (for Gradio file serving).
    """
    import shutil
    
    # Cleanup old output folders (keep max 10)
    output_temp = START_DIRECTORY / "output_temp"
    if output_temp.exists():
        folders = [f for f in output_temp.iterdir() if f.is_dir()]
        folders.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for folder in folders[10:]:
            shutil.rmtree(folder, ignore_errors=True)

    # Create timestamped output directory
    timestamp = str(int(time() * 1000))
    output_dir = output_temp / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    # Name the file based on the reference speaker
    if audio_prompt_path and Path(audio_prompt_path).stem:
        base_name = Path(audio_prompt_path).stem
    else:
        base_name = "generated"
    wav_path = output_dir / f"{base_name}.wav"

    # Resample if needed
    if target_sample_rate and sample_rate != target_sample_rate:
        import torchaudio
        audio_tensor = torchaudio.functional.resample(audio_tensor, sample_rate, target_sample_rate)
        sample_rate = target_sample_rate

    # Save audio tensor as WAV using soundfile (avoids torchaudio torchcodec dep)
    if audio_tensor.dim() == 1:
        audio_tensor = audio_tensor.unsqueeze(0)

    # soundfile expects (T, C) float32 numpy array
    audio_np = audio_tensor.cpu().float().numpy().T  # (1, T) -> (T, 1)
    sf.write(str(wav_path), audio_np, sample_rate)
    logger.info(f"Saved WAV: {wav_path} @ {sample_rate}Hz")

    return wav_path.relative_to(START_DIRECTORY)


def clear_output_directories() -> int:
    """Remove all folders in output_temp/ directory."""
    output_dir = START_DIRECTORY / "output_temp"
    count = 0
    if output_dir.exists():
        import shutil
        for child in output_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
                count += 1
    return count


def clear_cache_files() -> int:
    """Remove all .pt cache files."""
    cache_dir = START_DIRECTORY / "cache"
    count = 0
    if cache_dir.exists():
        for f in cache_dir.glob("*.pt"):
            f.unlink(missing_ok=True)
            count += 1
    _memory_cache.clear()
    return count
