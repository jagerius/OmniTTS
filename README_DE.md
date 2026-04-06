# OmniTTS für SkyrimNet

## Beschreibung
OmniTTS ist ein leistungsstarkes Text-to-Speech (TTS) Modul, welches die Standard-Chatterbox Engine in SkyrimNet ersetzt. Durch die native Integration des modernen, auf Diffusion basierenden OmniVoice TTS-Modells ermöglicht es realistische, dynamische Stimmkopien (Voice Cloning) und Dialogerstellung für NPCs in Skyrim. Die gesamte Generierung erfolgt lokal über ein Gradio-Backend, das nahtlos mit dem SkyrimNet C++ Client harmoniert.

## Installation
1. Navigieren Sie in den Ordner `OmniTTS` in der SkyrimNet Installation.
2. Führen Sie `setup_venv.bat` (Windows) aus. Dieses Skript erstellt automatisch eine virtuelle Python-Umgebung und installiert alle notwendigen Abhängigkeiten, einschließlich PyTorch mit CUDA-Unterstützung.
3. Stellen Sie sicher, dass sich Stimmproben für die NPCs als `.wav` im Verzeichnis `speakers/` befinden.

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
