
import sys
import signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer, Signal, QObject
from src.anima import EyesWidget
import random
import socket
import json
import threading

# --- Piper TTS integration ---
import os
from piper import PiperVoice
import sounddevice as sd
import numpy as np
import io
import soundfile as sf

# Paths to downloaded Piper models (adjust as needed)



# Look for models in the voices/mi_carpeta_voz directory (downloaded with Hugging Face CLI)
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'voices', 'mi_carpeta_voz'))
PIPER_MODELS = {
    'en': os.path.join(MODEL_DIR, 'en', 'en_US', 'amy', 'medium', 'en_US-amy-medium.onnx'),
    'es': os.path.join(MODEL_DIR, 'es', 'es_ES', 'sharvard', 'medium', 'es_ES-sharvard-medium.onnx'),
}

loaded_voices = {}
def get_voice(lang):
    if lang not in loaded_voices:
        model_path = PIPER_MODELS.get(lang)
        if not model_path or not os.path.exists(model_path):
            print(f"Piper model for '{lang}' not found: {model_path}")
            return None
        loaded_voices[lang] = PiperVoice.load(model_path)
    return loaded_voices[lang]

class FaceDisplay(QWidget):
    class MsgHandler(QObject):
        update_settings = Signal(dict)
        tts = Signal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avatar Face Display")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        self.eyes = EyesWidget()
        layout.addWidget(self.eyes)
        self.eyes.set_led_intensity(1.0)
        self.eyes.set_screen_intensity(1.0)
        self.behavior = "Happy"
        self.iris_speed = 180
        self.iris_color = "red"
        self.face_color = 255  # Default to red
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_behavior)
        self.timer.start(self.iris_speed)

        # Networking (UDP listener)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", 5005))
        self.sock.setblocking(False)
        self.msg_handler = self.MsgHandler()
        self.msg_handler.update_settings.connect(self._handle_settings)
        self.msg_handler.tts.connect(self._handle_tts)
        self.listen_thread = threading.Thread(target=self._listen, daemon=True)
        self.listen_thread.start()

    def _listen(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(4096)
                msg = json.loads(data.decode())
                if msg.get("type") == "settings":
                    self.msg_handler.update_settings.emit(msg)
                elif msg.get("type") == "tts":
                    self.msg_handler.tts.emit(msg)
            except Exception:
                pass

    def _handle_settings(self, msg):
        self.behavior = msg.get("behavior", self.behavior)
        self.iris_speed = msg.get("iris_speed", self.iris_speed)
        self.iris_color = msg.get("iris_color", self.iris_color)
        self.face_color = msg.get("face_color", 255)
        self.face_front_color = msg.get("face_color", 255)
        self.face_outline_color = msg.get("face_outline_color", "#ff0000")
        self.timer.setInterval(self.iris_speed)
        if hasattr(self.eyes, "set_face_color"):
            self.eyes.set_face_color(self.face_color)
        if hasattr(self.eyes, "set_face_outline_color"):
            self.eyes.set_face_outline_color(self.face_outline_color)
        if hasattr(self.eyes, "set_face_front_color"):
            self.eyes.set_face_front_color(self.face_front_color)
        # Fine iris position
        if "iris_x" in msg and "iris_y" in msg:
            self.eyes.set_pupil_pos(msg["iris_x"], msg["iris_y"])
        # Blink speed
        if "blink_speed" in msg:
            # If you have a method to set blink speed, call it here
            pass
        self.eyes.set_iris_color(self.iris_color)

    def _handle_tts(self, tts_msg):
        # Accept both string and dict for backward compatibility
        if isinstance(tts_msg, dict):
            text = tts_msg.get('text', '')
            lang = tts_msg.get('lang', 'en')
        else:
            text = tts_msg
            # Fallback: detect language by text
            lang = 'es' if any(c in text.lower() for c in 'ñáéíóú') else 'en'
        print(f"TTS called with: {text} (lang={lang})")
        voice = get_voice(lang)
        if voice and text:
            # PiperVoice.synthesize returns a generator of AudioChunk
            audio_chunks = list(voice.synthesize(text))
            if not audio_chunks:
                print("No audio chunks returned from Piper.")
                return
            # Concatenate all audio_float_array from chunks
            audio = np.concatenate([chunk.audio_float_array for chunk in audio_chunks])
            samplerate = audio_chunks[0].sample_rate
            sd.play(audio, samplerate)
            sd.wait()
        else:
            print(f"No Piper voice loaded for lang: {lang}")

    def _update_behavior(self):
        # Use iris_color for iris (requires EyesWidget patch for full color support)
        if self.behavior == "Sad":
            px = random.uniform(-0.2, 0.2)
            py = random.uniform(0.0, 0.3)
            self.eyes.set_pupil_pos(px, py)
            self.eyes.set_pupil_size(-0.5, 0.2)
            self.eyes.set_upper_lid(-0.3, 0.2)
            self.eyes.set_lower_lid(-0.3, 0.5)
            self.eyes.set_upper_lid_asymmetry(40)
            self.eyes.set_lower_lid_asymmetry(60)
            self.eyes.set_lid_curvature(0.7)
        elif self.behavior == "Happy":
            px = random.uniform(-0.4, 0.4)
            py = random.uniform(-0.2, 0.1)
            self.eyes.set_pupil_pos(px, py)
            self.eyes.set_pupil_size(0.5, 0.5)
            self.eyes.set_upper_lid(0.3, 1.0)
            self.eyes.set_lower_lid(0.3, 1.0)
            self.eyes.set_upper_lid_asymmetry(60)
            self.eyes.set_lower_lid_asymmetry(40)
            self.eyes.set_lid_curvature(0.3)
        elif self.behavior == "Regular Talking":
            px = random.uniform(-0.3, 0.3)
            py = random.uniform(-0.1, 0.1)
            self.eyes.set_pupil_pos(px, py)
            self.eyes.set_pupil_size(0.0, 0.3)
            self.eyes.set_upper_lid(0.0, 0.7)
            self.eyes.set_lower_lid(0.0, 0.7)
            self.eyes.set_upper_lid_asymmetry(50)
            self.eyes.set_lower_lid_asymmetry(50)
            self.eyes.set_lid_curvature(0.5)
        elif self.behavior == "Tired":
            px = random.uniform(-0.1, 0.1)
            py = random.uniform(0.1, 0.3)
            self.eyes.set_pupil_pos(px, py)
            self.eyes.set_pupil_size(-0.7, 0.1)
            self.eyes.set_upper_lid(-0.2, 0.0)
            self.eyes.set_lower_lid(-0.2, 0.3)
            self.eyes.set_upper_lid_asymmetry(45)
            self.eyes.set_lower_lid_asymmetry(55)
            self.eyes.set_lid_curvature(0.8)
        elif self.behavior == "Sleepy":
            px = random.uniform(-0.05, 0.05)
            py = random.uniform(0.2, 0.4)
            self.eyes.set_pupil_pos(px, py)
            self.eyes.set_pupil_size(-0.9, 0.05)
            self.eyes.set_upper_lid(-0.4, -0.7)
            self.eyes.set_lower_lid(-0.4, -0.5)
            self.eyes.set_upper_lid_asymmetry(50)
            self.eyes.set_lower_lid_asymmetry(50)
            self.eyes.set_lid_curvature(0.9)



def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = FaceDisplay()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
