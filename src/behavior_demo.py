import sys
import signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel
from PySide6.QtCore import QTimer
from src.anima import EyesWidget
import random

class BehaviorDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Avatar Behavior Demo")
        self.resize(800, 650)
        layout = QVBoxLayout(self)
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
        self.eyes = EyesWidget()
        layout.addWidget(self.eyes)
        self.eyes.set_led_intensity(1.0)
        self.eyes.set_screen_intensity(1.0)
        self.combo.currentIndexChanged.connect(self._reset_behavior)

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_behavior)
        self.timer.start(180)
        self.behavior = self.combo.currentText()

    def _reset_behavior(self):
        self.behavior = self.combo.currentText()

    def _update_behavior(self):
        if self.behavior == "Sad":
            self._sad_behavior()
        elif self.behavior == "Happy":
            self._happy_behavior()
        elif self.behavior == "Regular Talking":
            self._talking_behavior()
        elif self.behavior == "Tired":
            self._tired_behavior()
        elif self.behavior == "Sleepy":
            self._sleepy_behavior()

    def _sad_behavior(self):
        # Downward eyelids, slow, small movements, small pupils
        px = random.uniform(-0.2, 0.2)
        py = random.uniform(0.0, 0.3)
        self.eyes.set_pupil_pos(px, py)
        self.eyes.set_pupil_size(-0.5, 0.2)
        self.eyes.set_upper_lid(-0.3, 0.2)
        self.eyes.set_lower_lid(-0.3, 0.5)
        self.eyes.set_upper_lid_asymmetry(40)
        self.eyes.set_lower_lid_asymmetry(60)
        self.eyes.set_lid_curvature(0.7)
        if random.random() < 0.05:
            self.eyes.set_upper_lid(-0.3, -0.8)
            self.eyes.set_lower_lid(-0.3, -0.8)

    def _happy_behavior(self):
        # Upward eyelids, wide open, big pupils, lively movement
        px = random.uniform(-0.4, 0.4)
        py = random.uniform(-0.2, 0.1)
        self.eyes.set_pupil_pos(px, py)
        self.eyes.set_pupil_size(0.5, 0.5)
        self.eyes.set_upper_lid(0.3, 1.0)
        self.eyes.set_lower_lid(0.3, 1.0)
        self.eyes.set_upper_lid_asymmetry(60)
        self.eyes.set_lower_lid_asymmetry(40)
        self.eyes.set_lid_curvature(0.3)
        if random.random() < 0.08:
            self.eyes.set_upper_lid(0.3, -0.7)
            self.eyes.set_lower_lid(0.3, -0.7)

    def _talking_behavior(self):
        # Regular, attentive, moderate blinking, gaze shifts
        px = random.uniform(-0.3, 0.3)
        py = random.uniform(-0.1, 0.1)
        self.eyes.set_pupil_pos(px, py)
        self.eyes.set_pupil_size(0.0, 0.3)
        self.eyes.set_upper_lid(0.0, 0.7)
        self.eyes.set_lower_lid(0.0, 0.7)
        self.eyes.set_upper_lid_asymmetry(50)
        self.eyes.set_lower_lid_asymmetry(50)
        self.eyes.set_lid_curvature(0.5)
        if random.random() < 0.12:
            self.eyes.set_upper_lid(0.0, -0.7)
            self.eyes.set_lower_lid(0.0, -0.7)

    def _tired_behavior(self):
        # Droopy eyelids, slow, pupils small, occasional slow blink
        px = random.uniform(-0.1, 0.1)
        py = random.uniform(0.1, 0.3)
        self.eyes.set_pupil_pos(px, py)
        self.eyes.set_pupil_size(-0.7, 0.1)
        self.eyes.set_upper_lid(-0.2, 0.0)
        self.eyes.set_lower_lid(-0.2, 0.3)
        self.eyes.set_upper_lid_asymmetry(45)
        self.eyes.set_lower_lid_asymmetry(55)
        self.eyes.set_lid_curvature(0.8)
        if random.random() < 0.18:
            self.eyes.set_upper_lid(-0.2, -1.0)
            self.eyes.set_lower_lid(-0.2, -1.0)

    def _sleepy_behavior(self):
        # Very droopy eyelids, almost closed, slowest movement, smallest pupils
        px = random.uniform(-0.05, 0.05)
        py = random.uniform(0.2, 0.4)
        self.eyes.set_pupil_pos(px, py)
        self.eyes.set_pupil_size(-0.9, 0.05)
        self.eyes.set_upper_lid(-0.4, -0.7)
        self.eyes.set_lower_lid(-0.4, -0.5)
        self.eyes.set_upper_lid_asymmetry(50)
        self.eyes.set_lower_lid_asymmetry(50)
        self.eyes.set_lid_curvature(0.9)
        if random.random() < 0.25:
            self.eyes.set_upper_lid(-0.4, -1.0)
            self.eyes.set_lower_lid(-0.4, -1.0)

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = BehaviorDemo()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
