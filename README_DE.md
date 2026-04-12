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

# OmniTTS für SkyrimNet

## Beschreibung
OmniTTS ist ein leistungsstarkes Text-to-Speech (TTS) Modul, welches die Standard-Chatterbox Engine in SkyrimNet ersetzt. Durch die native Integration des modernen, auf Diffusion basierenden OmniVoice TTS-Modells ermöglicht es realistische, dynamische Stimmkopien (Voice Cloning) und Dialogerstellung für NPCs in Skyrim. Die gesamte Generierung erfolgt lokal über ein Gradio-Backend, das nahtlos mit dem SkyrimNet C++ Client harmoniert.

## Installation
1. Navigieren Sie in den Ordner `OmniTTS` in der SkyrimNet Installation.
2. Führen Sie `setup_venv.bat` (Windows) aus. Dieses Skript erstellt automatisch eine virtuelle Python-Umgebung und installiert alle notwendigen Abhängigkeiten, einschließlich PyTorch mit CUDA-Unterstützung.
3. Stellen Sie sicher, dass sich Stimmproben für die NPCs als `.wav` im Verzeichnis `speakers/` befinden.
4. **Wichtig für Windows-Nutzer**: OmniVoice benötigt die Bibliothek `torchcodec`, welche wiederum eine vollständige Installation von FFmpeg voraussetzt.
   - Laden Sie den vollständigen (FULL) FFmpeg-Build von [BtBN FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds/releases) herunter.
   - Entpacken Sie das Verzeichnis und benennen Sie den Ordner in `ffmpeg` um.
   - Platzieren Sie diesen `ffmpeg`-Ordner direkt im Hauptverzeichnis (`SkyrimNetOmniVoice`) oder in `OmniTTS`, sodass der Pfad `ffmpeg/bin` existiert. OmniTTS erkennt diesen automatisch und lädt die DLLs, um Abstürze zu vermeiden.

> [!NOTE]
> Standardmäßig benötigt OmniTTS eine NVIDIA-Grafikkarte (es verwendet CUDA-Beschleunigung). Wenn Sie keine kompatible GPU haben, können Sie die Ausführung auf dem Prozessor (CPU) erzwingen, indem Sie `use_cpu = true` in der Datei `omnitts_config.txt` setzen (Hinweis: Die Generierung wird deutlich langsamer sein).

## Nutzung
1. Starten Sie `Start.bat`, um den TTS-Server zu aktivieren. Danach wartet ein lokaler Gradio-Server am Port 8000 auf Befehle.
2. Der Server lauscht auf API-Anfragen des SkyrimNet GamePlugins.
3. Sprechen Sie in Skyrim mit einem NPC. SkyrimNet sendet den Text automatisch an OmniTTS und spielt daraufhin den generierten Dialog ab.

## Konfiguration (`omnitts_config.txt`)
Die Datei `omnitts_config.txt` ermöglicht tiefgreifende Optimierungen:
* **`guidance_scale`**: Definiert wie stark sich die KI an den Originalstimmen Prompt und den Text hält.
* **`num_step`**: Berechnungsschritte der KI-Diffusion. Eine Verringerung (z.B. auf 12) macht das Modell viel schneller, ohne allzu massive Qualitätsverluste.
* **`speed`**: Kontrolliert die Sprechgeschwindigkeit des NPCs.
* **`denoise`**: Entfernt Artefakte und Hintergrundgeräusche aus dem generierten Audio (empfohlen: `true`).
* **`audio_chunk_threshold` & `audio_chunk_duration`**: Verhindert abgehackte Sätze bei langen Texten, indem sehr lange Passagen in passendere Audio-Chunks unterteilt werden.
* **`model_path`**: Lokal- oder HuggingFace-Pfad zum OmniVoice Model.
* **`enable_memory_cache` & `enable_disk_cache`**: Caching von Stimmen. Beschleunigt das Generieren enorm, falls man mehrmals hintereinander mit demselben Charakter spricht.

## Danksagungen (Credits)
* **OmniVoice**: Dieses Projekt verwendet das fortschrittliche OmniVoice TTS-Modell, verfügbar unter [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice).
* **Chatterbox**: Die Implementierung und die API-Struktur basieren stark auf dem [langfod/chatterbox](https://github.com/langfod/chatterbox) Plugin.
