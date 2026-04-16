import sys
import signal
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSlider, QLabel, QColorDialog, QLineEdit, QComboBox
from PySide6.QtCore import Qt
import socket
import json
from src.anima import JoystickWidget



class BehaviorGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Behavior Generator Control Panel")
        self.resize(420, 800)
        layout = QVBoxLayout(self)


    def __init__(self):
        super().__init__()
        self.setWindowTitle("Behavior Generator Control Panel")
        self.resize(420, 800)
        layout = QVBoxLayout(self)

        # Face color slider
        self.face_color_label = QLabel("Face Color:")
        layout.addWidget(self.face_color_label)
        self.face_color_slider = QSlider(Qt.Horizontal)
        self.face_color_slider.setRange(0, 255)
        self.face_color_slider.setValue(255)  # Default to red
        layout.addWidget(self.face_color_slider)

        # Face outline color picker (for the red line)
        self.face_outline_color = "#ff0000"  # Default to red
        self.face_outline_color_btn = QPushButton("Choose Face Outline Color")
        self.face_outline_color_btn.setStyleSheet(f"background-color: {self.face_outline_color}")
        self.face_outline_color_btn.clicked.connect(self.choose_face_outline_color)
        layout.addWidget(self.face_outline_color_btn)

        # Behavior selector
        self.behavior_label = QLabel("Select Behavior:")
        layout.addWidget(self.behavior_label)
        self.behavior_combo = QComboBox()
        self.behavior_combo.addItems([
            "Sad",
            "Happy",
            "Regular Talking",
            "Tired",
            "Sleepy"
        ])
        layout.addWidget(self.behavior_combo)

        # Joysticks for position, size, lids
        self.joy_pos = JoystickWidget("Posición (X/Y)", 0.0, 0.0)
        self.joy_sizes = JoystickWidget("Tamaños (Pupila / Brillo)", 0.0, 0.0)
        self.joy_upper = JoystickWidget("Párpado Superior", 0.3, -0.32)
        self.joy_lower = JoystickWidget("Párpado Inferior", 0.3, 0.28)
        layout.addWidget(self.joy_pos)
        layout.addWidget(self.joy_sizes)
        layout.addWidget(self.joy_upper)
        layout.addWidget(self.joy_lower)

        # Sliders for blink speed, iris speed, iris color
        self.blink_speed_label = QLabel("Blink Speed (ms):")
        layout.addWidget(self.blink_speed_label)
        self.blink_speed_slider = QSlider(Qt.Horizontal)
        self.blink_speed_slider.setRange(100, 2000)
        self.blink_speed_slider.setValue(340)
        layout.addWidget(self.blink_speed_slider)

        self.iris_speed_label = QLabel("Iris Speed (ms):")
        layout.addWidget(self.iris_speed_label)
        self.iris_speed_slider = QSlider(Qt.Horizontal)
        self.iris_speed_slider.setRange(50, 1000)
        self.iris_speed_slider.setValue(180)
        layout.addWidget(self.iris_speed_slider)

        self.color_btn = QPushButton("Choose Iris Color")
        self.color_btn.clicked.connect(self.choose_color)
        layout.addWidget(self.color_btn)
        self.iris_color = "red"


        # TTS
        self.tts_label = QLabel("Text to Speak:")
        layout.addWidget(self.tts_label)
        self.tts_input = QLineEdit()
        layout.addWidget(self.tts_input)

        # Language dropdown for TTS
        self.tts_lang_label = QLabel("TTS Language:")
        layout.addWidget(self.tts_lang_label)
        self.tts_lang_combo = QComboBox()
        self.tts_lang_combo.addItems(["en", "es"])
        layout.addWidget(self.tts_lang_combo)

        self.tts_btn = QPushButton("Speak")
        layout.addWidget(self.tts_btn)

        # Networking
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target = ("127.0.0.1", 5005)

        # Connect direct signals for synchronous control
        self.joy_pos.positionChanged.connect(self.send_all)
        self.joy_sizes.positionChanged.connect(self.send_all)
        self.joy_upper.positionChanged.connect(self.send_all)
        self.joy_lower.positionChanged.connect(self.send_all)
        self.blink_speed_slider.valueChanged.connect(self.send_all)
        self.iris_speed_slider.valueChanged.connect(self.send_all)
        self.face_color_slider.valueChanged.connect(self.send_all)
        self.face_outline_color_btn.clicked.connect(self.send_all)

    def choose_face_outline_color(self):
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor()
        if color.isValid():
            self.face_outline_color = color.name()
            self.face_outline_color_btn.setStyleSheet(f"background-color: {self.face_outline_color}")
            self.send_all()
        # Only send color when changed, not on every click (prevents overwriting user changes)
        self.behavior_combo.currentIndexChanged.connect(self.set_behavior_defaults)
        self.tts_btn.clicked.connect(self.send_tts)

        # Set initial defaults
        self.set_behavior_defaults()

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.iris_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self.iris_color}")
            self.send_all()

    def set_behavior_defaults(self):
        # Block signals to avoid triggering send_all during set_pos/setValue
        self.joy_pos.blockSignals(True)
        self.joy_sizes.blockSignals(True)
        self.joy_upper.blockSignals(True)
        self.joy_lower.blockSignals(True)
        self.blink_speed_slider.blockSignals(True)
        self.iris_speed_slider.blockSignals(True)

        behavior = self.behavior_combo.currentText()
        # Set default parameters for each behavior
        if behavior == "Sad":
            self.joy_pos.set_pos(0.0, 0.15)
            self.joy_sizes.set_pos(-0.5, 0.2)
            self.joy_upper.set_pos(-0.3, 0.2)
            self.joy_lower.set_pos(-0.3, 0.5)
            self.blink_speed_slider.setValue(700)
            self.iris_speed_slider.setValue(300)
            self.iris_color = "#3a3a8a"
        elif behavior == "Happy":
            self.joy_pos.set_pos(0.0, -0.05)
            self.joy_sizes.set_pos(0.5, 0.5)
            self.joy_upper.set_pos(0.3, 1.0)
            self.joy_lower.set_pos(0.3, 1.0)
            self.blink_speed_slider.setValue(340)
            self.iris_speed_slider.setValue(180)
            self.iris_color = "#ff6600"
        elif behavior == "Regular Talking":
            self.joy_pos.set_pos(0.0, 0.0)
            self.joy_sizes.set_pos(0.0, 0.3)
            self.joy_upper.set_pos(0.0, 0.7)
            self.joy_lower.set_pos(0.0, 0.7)
            self.blink_speed_slider.setValue(400)
            self.iris_speed_slider.setValue(200)
            self.iris_color = "#0099cc"
        elif behavior == "Tired":
            self.joy_pos.set_pos(0.0, 0.2)
            self.joy_sizes.set_pos(-0.7, 0.1)
            self.joy_upper.set_pos(-0.2, 0.0)
            self.joy_lower.set_pos(-0.2, 0.3)
            self.blink_speed_slider.setValue(1200)
            self.iris_speed_slider.setValue(400)
            self.iris_color = "#666666"
        elif behavior == "Sleepy":
            self.joy_pos.set_pos(0.0, 0.3)
            self.joy_sizes.set_pos(-0.9, 0.05)
            self.joy_upper.set_pos(-0.4, -0.7)
            self.joy_lower.set_pos(-0.4, -0.5)
            self.blink_speed_slider.setValue(1800)
            self.iris_speed_slider.setValue(600)
            self.iris_color = "#222222"
        self.color_btn.setStyleSheet(f"background-color: {self.iris_color}")

        # Re-enable signals
        self.joy_pos.blockSignals(False)
        self.joy_sizes.blockSignals(False)
        self.joy_upper.blockSignals(False)
        self.joy_lower.blockSignals(False)
        self.blink_speed_slider.blockSignals(False)
        self.iris_speed_slider.blockSignals(False)

        self.send_all()

    def send_all(self, *args):
        msg = {
            "type": "settings",
            "iris_x": self.joy_pos.pos_x,
            "iris_y": self.joy_pos.pos_y,
            "pupil_size": self.joy_sizes.pos_x,
            "shine_size": self.joy_sizes.pos_y,
            "upper_lid_tilt": self.joy_upper.pos_x,
            "upper_lid_open": self.joy_upper.pos_y,
            "lower_lid_tilt": self.joy_lower.pos_x,
            "lower_lid_open": self.joy_lower.pos_y,
            "blink_speed": self.blink_speed_slider.value(),
            "iris_speed": self.iris_speed_slider.value(),
            "iris_color": self.iris_color,
            "behavior": self.behavior_combo.currentText(),
            "face_color": self.face_color_slider.value(),
            "face_outline_color": self.face_outline_color
        }
        self.sock.sendto(json.dumps(msg).encode(), self.target)

    def send_tts(self):
        text = self.tts_input.text()
        lang = self.tts_lang_combo.currentText()
        print(f"Sending TTS: {text} (lang={lang})")
        if text:
            msg = {"type": "tts", "text": text, "lang": lang}
            self.sock.sendto(json.dumps(msg).encode(), self.target)


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = BehaviorGenerator()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
