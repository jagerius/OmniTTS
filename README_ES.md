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

# OmniTTS para SkyrimNet

## Descripción
OmniTTS es un módulo avanzado de conversión de texto a voz (TTS) diseñado para sustituir el motor Chatterbox predeterminado en SkyrimNet. Al integrar el modelo de difusión de vanguardia OmniVoice de manera nativa, este software proporciona de forma dinámica una clonación de voz extremadamente realista para todos los personajes no jugables (NPCs) de Skyrim. Su procesamiento y generación de diálogos se ejecutan de forma local utilizando Gradio como backend.

## Instalación
1. Accede al directorio `OmniTTS` ubicado en la carpeta principal de tu instalación.
2. Ejecuta el archivo `setup_venv.bat` (Windows). Este script se encargará de crear un entorno de Python específico y de instalar dependencias clave como PyTorch (con aceleración CUDA).
3. Cerciórate de tener audios de muestra en formato `.wav` correspondientes a la voz de cada NPC almacenados en la carpeta `speakers/`.

## Uso
1. Abre `Start.bat` para levantar el servidor TTS en el puerto local 8000.
2. Mantén esta ventana abierta. Este servidor procesa todas las solicitudes API que manda el plugin (GamePlugin) de SkyrimNet internamente.
3. Ve a hablar dentro de Skyrim con un NPC; el componente mandará el texto y retornará automáticamente un archivo de audio perfectamente clonado.

## Configuración (`omnitts_config.txt`)
El panel de ajustes reside primordialmente en el archivo de texto `omnitts_config.txt`. Podrás calibrar lo siguiente:
* **`guidance_scale`**: Ajusta el rigor con el que el TTS se va a adherir a la precisión del original.
* **`num_step`**: Son los pasos inferenciales. Reducir la cifra (por ejemplo a 12 o 16 pasos) reduce bastante los segundos que tarda sin apenas perder calidad notable del audio.
* **`speed`**: Control sobre la cadencia del discurso y la velocidad con la que suena el PNJ.
* **`denoise`**: Eliminar distorsiones y ruidos extraños de fondo (se aconseja que esté en `true`).
* **`audio_chunk_threshold` & `audio_chunk_duration`**: Dos herramientas excelentes si la Inteligencia se bloquea generando guiones largos, forzándola a retransmitir y trocear las cuñas cortas sucesivamente.
* **`model_path`**: Referencia de donde se descarga/localiza el modelo pesado OmniVoice base.
* **`enable_memory_cache` & `enable_disk_cache`**: La activación previene la espera innecesaria entre carga de variables si interactúas múltiples veces con un mismo aldeano.
