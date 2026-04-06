# OmniTTS dla SkyrimNet

## Opis
OmniTTS to wysokowydajny moduł zamiany tekstu na mowę (TTS), który zastępuje domyślny silnik Chatterbox w SkyrimNet. Integruje on nowoczesny model dyfuzyjny OmniVoice, aby zapewnić realistyczne klonowanie głosu postaci i generowanie dialogów dla NPC ze Skyrim. Całe generowanie odbywa się lokalnie za pośrednictwem serwera Gradio, zaprojektowanego tak, by był w pełni kompatybilny z klientem SkyrimNet w C++.

## Instalacja
1. Przejdź do folderu `OmniTTS` w głównym katalogu moda.
2. Uruchom plik `setup_venv.bat` (Windows). Skrypt ten automatycznie utworzy środowisko wirtualne Pythona i zainstaluje wszystkie wymagane biblioteki (w tym PyTorch z obsługą CUDA dla kart NVIDIA).
3. Upewnij się, że umieściłeś odpowiednie pliki `.wav` z próbkami głosów postaci w folderze `speakers/`.

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
