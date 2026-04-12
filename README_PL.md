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

# OmniTTS dla SkyrimNet

## Opis
OmniTTS to wysokowydajny moduł zamiany tekstu na mowę (TTS), który zastępuje domyślny silnik Chatterbox w SkyrimNet. Integruje on nowoczesny model dyfuzyjny OmniVoice, aby zapewnić realistyczne klonowanie głosu postaci i generowanie dialogów dla NPC ze Skyrim. Całe generowanie odbywa się lokalnie za pośrednictwem serwera Gradio, zaprojektowanego tak, by był w pełni kompatybilny z klientem SkyrimNet w C++.

## Instalacja
1. Przejdź do folderu `OmniTTS` w głównym katalogu moda.
2. Uruchom plik `setup_venv.bat` (Windows). Skrypt ten automatycznie utworzy środowisko wirtualne Pythona i zainstaluje wszystkie wymagane biblioteki (w tym PyTorch z obsługą CUDA dla kart NVIDIA).
3. Upewnij się, że umieściłeś odpowiednie pliki `.wav` z próbkami głosów postaci w folderze `speakers/`.
4. **Ważne dla użytkowników Windows**: OmniVoice wymaga biblioteki `torchcodec`, dla której niezbędna jest pełna wersja zestawu narzędzi FFmpeg.
   - Pobierz pełną wersję (FULL) z [BtBN FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds/releases).
   - Wypakuj archiwum i zmień nazwę wypakowanego folderu na `ffmpeg`.
   - Umieść ten folder w głównym katalogu (`SkyrimNetOmniVoice`) lub bezpośrednio w `OmniTTS` (tak aby powstała ścieżka `ffmpeg/bin`). Serwer automatycznie go wykryje, co zapobiegnie błędom.

> [!NOTE]
> Domyślnie OmniTTS wymaga do działania karty graficznej NVIDIA (wykorzystuje rdzenie CUDA). Jeżeli nie posiadasz kompatybilnej karty, możesz wymusić działanie na procesorze (CPU), zmieniając opcję `use_cpu = true` w pliku `omnitts_config.txt` (uwaga: generowanie głosu będzie znacznie wolniejsze).

## Używanie
1. Aby uruchomić serwer TTS, uruchom `Start.bat`. Zainicjuje to lokalny serwer Gradio nasłuchujący na porcie 8000.
2. Serwer ten będzie czekał na żądania API od wtyczki SkyrimNet (GamePlugin).
3. Podczas rozmowy z NPC w grze, SkyrimNet wyśle tekst i automatycznie otrzyma odtworzone audio.

## Konfiguracja (`omnitts_config.txt`)
Plik konfiguracyjny `omnitts_config.txt` pozwala na dopracowanie jakości i wydajności głosu:
* **`guidance_scale`**: Decyduje o tym, jak bardzo sztuczna inteligencja trzyma się tekstu i dostarczonej próbki głosu.
* **`num_step`**: Liczba kroków odszumiania. Zmniejszenie tej wartości (np. do 12) drastycznie przyspiesza generowanie kosztem nieznacznej utraty jakości.
* **`speed`**: Pozwala na zmianę tempa mowy postaci.
* **`denoise`**: Włącza odszumianie wygenerowanego dźwięku. Opcję najlepiej zostawić włączoną (`true`).
* **`audio_chunk_threshold` & `audio_chunk_duration`**: Zapobiega ucinaniu długich wypowiedzi przez dzielenie rozbudowanych zdań na mniejsze, odtwarzalne kawałki.
* **`model_path`**: Ścieżka lokalna lub nazwa repozytorium HuggingFace skąd pobierany jest model OmniVoice.
* **`enable_memory_cache` & `enable_disk_cache`**: Cechy te przyspieszają kolejne odpowiedzi tego samego NPC poprzez cachowanie ustawień jego tonu głosu.

## Podziękowania (Credits)
* **OmniVoice**: Projekt ten korzysta z zaawansowanego modelu OmniVoice TTS dostępnego na [k2-fsa/OmniVoice](https://github.com/k2-fsa/OmniVoice).
* **Chatterbox**: Implementacja i struktura API opiera się w głównej mierze na wtyczce [langfod/chatterbox](https://github.com/langfod/chatterbox).
