# Setup Instructions for Anima Behavior Control with Piper TTS

## 1. Install Python Dependencies (using uv)

Run this command in your project directory:

```
uv pip install piper-tts sounddevice soundfile PySide6
```


## 2. Download Piper Voice Models (with Hugging Face CLI)

Install the Hugging Face CLI if you don't have it:
```
pip install -U huggingface_hub
```

Download the models and config files to a dedicated folder:
```
hf download rhasspy/piper-voices --include "es/es_ES/sharvard/medium/*" --local-dir ./mi_carpeta_voz
hf download rhasspy/piper-voices --include "en/en_US/amy/medium/*" --local-dir ./mi_carpeta_voz
```

This will create a folder `mi_carpeta_voz` with the following files:
  - `mi_carpeta_voz/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx`
  - `mi_carpeta_voz/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json`
  - `mi_carpeta_voz/en/en_US/amy/medium/en_US-amy-medium.onnx`
  - `mi_carpeta_voz/en/en_US/amy/medium/en_US-amy-medium.onnx.json`

Update the model path in your code if you use a different directory.

## 3. Run the System

- Start the face display:
  ```
  python3 -m src.face_display
  ```
- Start the behavior generator or control panel:
  ```
  python3 -m src/behavior_generator
  ```

## 4. Notes
- You can add more Piper voices by downloading additional models from the [Piper Hugging Face page](https://huggingface.co/rhasspy/piper-voices/tree/main).
- If you place the models in a different directory, update the paths in `face_display.py` accordingly.
- All dependencies are managed by uv for reproducibility and speed.
