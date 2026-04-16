import sys
import signal
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from PySide6.QtCore import QTimer
from src.anima import EyesWidget
import random

class CrazyFaceDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crazy Autonomous Face Demo")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        self.eyes = EyesWidget()
        layout.addWidget(self.eyes)
        self.eyes.set_led_intensity(1.0)
        self.eyes.set_screen_intensity(1.0)

        self.timer = QTimer()
        self.timer.timeout.connect(self._crazy_update)
        self.timer.start(120)

    def _crazy_update(self):
        # Wild, erratic eye and eyelid movement
        px = random.uniform(-1.0, 1.0) + random.uniform(-0.2, 0.2)
        py = random.uniform(-1.0, 1.0) + random.uniform(-0.2, 0.2)
        px = max(-1.0, min(1.0, px))
        py = max(-1.0, min(1.0, py))
        self.eyes.set_pupil_pos(px, py)

        sx = random.uniform(-1.0, 1.0)
        sy = random.uniform(0.0, 1.0)
        self.eyes.set_pupil_size(sx, sy)

        upper_x = random.uniform(-1.0, 1.0)
        upper_y = random.uniform(-1.0, 1.0)
        lower_x = random.uniform(-1.0, 1.0)
        lower_y = random.uniform(-1.0, 1.0)
        self.eyes.set_upper_lid(upper_x, upper_y)
        self.eyes.set_lower_lid(lower_x, lower_y)

        # Asymmetry and curvature for extra craziness
        self.eyes.set_upper_lid_asymmetry(random.randint(0, 100))
        self.eyes.set_lower_lid_asymmetry(random.randint(0, 100))
        self.eyes.set_lid_curvature(random.uniform(0.0, 1.0))

        # Occasional blink
        if random.random() < 0.25:
            self.eyes.set_upper_lid(upper_x, -1.0)
            self.eyes.set_lower_lid(lower_x, -1.0)

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = CrazyFaceDemo()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
