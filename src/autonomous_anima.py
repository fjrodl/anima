import sys
import signal
import random
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication

from src.anima import CirclesInterface

class AutonomousCirclesInterface(CirclesInterface):
    def __init__(self):
        super().__init__()
        # Autonomous behavior timer
        self.auto_eye_timer = QTimer()
        self.auto_eye_timer.timeout.connect(self._autonomous_update)
        self.auto_eye_timer.start(180)  # Update every 0.18s for more frantic motion

    def toggle_power(self):
        super().toggle_power()
        # Start/stop autonomous behavior based on awake state
        if not self.is_awake:
            self.auto_eye_timer.stop()
        else:
            self.auto_eye_timer.start(700)

    def _autonomous_update(self):
        if not self.is_awake or self.is_blinking:
            return
        # "Crazy" erratic, independent eye behavior
        # Each update, jump to a new random position, sometimes extreme
        px = random.uniform(-1.0, 1.0) * random.choice([1, -1]) * random.uniform(0.7, 1.0)
        py = random.uniform(-1.0, 1.0) * random.choice([1, -1]) * random.uniform(0.7, 1.0)
        # Add jitter for more chaos
        px += random.uniform(-0.2, 0.2)
        py += random.uniform(-0.2, 0.2)
        px = max(-1.0, min(1.0, px))
        py = max(-1.0, min(1.0, py))
        self.joy_pos.set_pos(px, py)
        self.eyes.set_pupil_pos(px, py)

        # Rapid, wild pupil size and shine
        sx = random.uniform(-1.0, 1.0)
        sy = random.uniform(0.0, 1.0)
        self.joy_sizes.set_pos(sx, sy)
        self.eyes.set_pupil_size(sx, sy)

        # Rapid, random eyelid movement for "crazy" effect
        upper_x = random.uniform(-1.0, 1.0)
        upper_y = random.uniform(-1.0, 1.0)
        lower_x = random.uniform(-1.0, 1.0)
        lower_y = random.uniform(-1.0, 1.0)
        self.joy_upper.set_pos(upper_x, upper_y)
        self.eyes.set_upper_lid(upper_x, upper_y)
        self.joy_lower.set_pos(lower_x, lower_y)
        self.eyes.set_lower_lid(lower_x, lower_y)

        # Much more frequent and sometimes double blinks
        if random.random() < 0.35:
            self.animate_blink()
        # Occasionally do a "double blink"
        if random.random() < 0.10:
            QTimer.singleShot(120, self.animate_blink)


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QApplication(sys.argv)
    window = AutonomousCirclesInterface()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
