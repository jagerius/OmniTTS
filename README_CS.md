# OmniTTS pro SkyrimNet

## Popis
OmniTTS je vysoce výkonný text-to-speech (TTS) modul, který nahrazuje výchozí engin Chatterbox ve SkyrimNetu. Nativně integruje moderní difúzní TTS model OmniVoice pro poskytování realistického, dynamického klonování hlasu a generování dialogů pro NPC ve Skyrimu. Veškeré generování probíhá lokálně prostřednictvím Gradio backendu, který je plně kompatibilní s C++ klientem SkyrimNet.

## Instalace
1. Přejděte do složky `OmniTTS` v rámci instalace SkyrimNet.
2. Spusťte `setup_venv.bat` (Windows). Tento skript automaticky vytvoří virtuální prostředí Pythonu a nainstaluje všechny závislosti, včetně PyTorch s podporou CUDA.
3. Ujistěte se, že ve složce `speakers/` jsou umístěny `.wav` soubory se zvukovými vzorky pro klonování hlasu NPC.

## Použití
1. Pro spuštění TTS serveru spusťte `Start.bat`. Otevře se lokální Gradio server naslouchající na portu 8000.
2. Server bude čekat na API požadavky ze SkyrimNet GamePluginu.
3. Během interakce s NPC ve Skyrimu odešle SkyrimNet text a OmniTTS automaticky vygeneruje dialog a poskytne cestu ke zvuku.

## Konfigurace (`omnitts_config.txt`)
Soubor `omnitts_config.txt` umožňuje doladit kvalitu a výkon generování zvuku:
* **`guidance_scale`**: Určuje, jak přesně se umělá inteligence drží hlasové předlohy a textu.
* **`num_step`**: Počet kroků difúzního modelu. Snížení této hodnoty (např. na 12) výrazně zrychlí generování s minimální ztrátou kvality.
* **`speed`**: Upravuje rychlost řeči postavy.
* **`denoise`**: Povoluje odšumování vygenerovaného zvuku (doporučeno ponechat na `true`).
* **`audio_chunk_threshold` & `audio_chunk_duration`**: Zabraňuje ustřižení dlouhých vět tím, že rozdělí rozsáhlé textové řetězce do kratších, snáze zpracovatelných zvukových bloků.
* **`model_path`**: Definuje repozitář na HuggingFace nebo lokální cestu k modelu OmniVoice.
* **`enable_memory_cache` & `enable_disk_cache`**: Ukládá parametry naklonovaného hlasu do vyrovnávací paměti, což radikálně zrychluje proces při opakovaném rozhovoru se stejným NPC.
