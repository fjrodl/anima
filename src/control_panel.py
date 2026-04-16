import sys
import signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel, QSlider, QPushButton, QLineEdit, QColorDialog, QHBoxLayout
from PySide6.QtCore import Qt
import socket
import json
import threading


class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avatar Control Panel")
        self.resize(400, 400)
        layout = QVBoxLayout(self)

        # Fine iris position controls
        self.iris_x_label = QLabel("Iris X (-1.0 to 1.0):")
        layout.addWidget(self.iris_x_label)
        self.iris_x_slider = QSlider(Qt.Horizontal)
        self.iris_x_slider.setRange(-100, 100)
        self.iris_x_slider.setValue(0)
        layout.addWidget(self.iris_x_slider)

        self.iris_y_label = QLabel("Iris Y (-1.0 to 1.0):")
        layout.addWidget(self.iris_y_label)
        self.iris_y_slider = QSlider(Qt.Horizontal)
        self.iris_y_slider.setRange(-100, 100)
        self.iris_y_slider.setValue(0)
        layout.addWidget(self.iris_y_slider)

        # Blink speed control
        self.blink_speed_label = QLabel("Blink Speed (ms):")
        layout.addWidget(self.blink_speed_label)
        self.blink_speed_slider = QSlider(Qt.Horizontal)
        self.blink_speed_slider.setRange(100, 2000)
        self.blink_speed_slider.setValue(340)
        layout.addWidget(self.blink_speed_slider)

        # Behavior selection
        self.label = QLabel("Select Behavior:")
        layout.addWidget(self.label)
        self.combo = QComboBox()
        self.combo.addItems([
            "Sad",
            "Happy",
            "Regular Talking",
            "Tired",
            "Sleepy"
        ])
        layout.addWidget(self.combo)

        # Iris speed
        self.speed_label = QLabel("Iris Speed (ms):")
        layout.addWidget(self.speed_label)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(50, 1000)
        self.speed_slider.setValue(180)
        layout.addWidget(self.speed_slider)

        # Iris color
        color_layout = QHBoxLayout()
        self.color_label = QLabel("Iris Color:")
        color_layout.addWidget(self.color_label)
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_color)
        color_layout.addWidget(self.color_btn)
        layout.addLayout(color_layout)
        self.iris_color = "red"

        # TTS
        self.tts_label = QLabel("Text to Speak:")
        layout.addWidget(self.tts_label)
        self.tts_input = QLineEdit()
        layout.addWidget(self.tts_input)
        self.tts_btn = QPushButton("Speak")
        layout.addWidget(self.tts_btn)

        # Send button
        self.send_btn = QPushButton("Send Settings")
        layout.addWidget(self.send_btn)

        self.send_btn.clicked.connect(self.send_settings)
        self.tts_btn.clicked.connect(self.send_tts)

        # Networking
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.target = ("127.0.0.1", 5005)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.iris_color = color.name()
            self.color_btn.setStyleSheet(f"background-color: {self.iris_color}")

    def send_settings(self):
        msg = {
            "type": "settings",
            "behavior": self.combo.currentText(),
            "iris_speed": self.speed_slider.value(),
            "iris_color": self.iris_color,
            "iris_x": self.iris_x_slider.value() / 100.0,
            "iris_y": self.iris_y_slider.value() / 100.0,
            "blink_speed": self.blink_speed_slider.value()
        }
        self.sock.sendto(json.dumps(msg).encode(), self.target)

    def send_tts(self):
        text = self.tts_input.text()
        if text:
            msg = {"type": "tts", "text": text}
            self.sock.sendto(json.dumps(msg).encode(), self.target)


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = ControlPanel()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
