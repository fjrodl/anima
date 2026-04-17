import sys
import signal
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QVariantAnimation, QTimer
from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QSlider,
    QLabel,
)


class JoystickWidget(QWidget):
    positionChanged = Signal(float, float)

    def __init__(self, title, def_x=0.0, def_y=0.0):
        super().__init__()
        self.setMinimumSize(160, 180)
        self.setMaximumSize(250, 250)
        self.title = title
        self.pos_x = def_x
        self.pos_y = def_y
        self.moving = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # draw title
        painter.setPen(QColor("black"))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, 0, w, 20), Qt.AlignCenter, self.title)

        # Joy area - Siempre cuadrado para círculo perfecto
        size = min(w - 20, h - 35)
        joy_rect = QRectF((w - size) / 2, 25 + (h - 35 - size) / 2, size, size)

        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QColor(40, 40, 40))
        painter.drawEllipse(joy_rect)

        # Draw axes
        center = joy_rect.center()
        painter.setPen(QPen(QColor(70, 70, 70), 1, Qt.DashLine))
        painter.drawLine(
            QPointF(joy_rect.left(), center.y()), QPointF(joy_rect.right(), center.y())
        )
        painter.drawLine(
            QPointF(center.x(), joy_rect.top()), QPointF(center.x(), joy_rect.bottom())
        )

        # Draw dot
        r = size / 2.0
        cx = center.x() + self.pos_x * r
        cy = center.y() - self.pos_y * r

        painter.setBrush(QColor("white"))
        painter.setPen(QPen(QColor("black"), 2))
        painter.drawEllipse(QPointF(cx, cy), 12, 12)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.update_pos(event.position())
            self.moving = True

    def mouseMoveEvent(self, event):
        if self.moving:
            self.update_pos(event.position())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.moving = False

    def update_pos(self, pos):
        w = self.width()
        h = self.height()
        size = min(w - 20, h - 35)
        center = QPointF(w / 2, 25 + (h - 35) / 2)
        r = size / 2.0

        dx = pos.x() - center.x()
        dy = center.y() - pos.y()

        dist = (dx**2 + dy**2) ** 0.5
        if dist > r:
            dx = dx * r / dist
            dy = dy * r / dist

        self.pos_x = dx / r
        self.pos_y = dy / r

        self.positionChanged.emit(self.pos_x, self.pos_y)
        self.update()

    def set_pos(self, x, y):
        self.pos_x = x
        self.pos_y = y
        self.positionChanged.emit(self.pos_x, self.pos_y)
        self.update()


class EyesWidget(QWidget):

    def set_face_color(self, value):
        # value: 0 (gray) to 255 (red)
        self.face_color = QColor(value, 0, 0)
        self.update()

    def set_face_outline_color(self, color):
        # color: string (e.g. '#ff0000') or QColor
        if isinstance(color, str):
            self.face_outline_color = QColor(color)
        elif isinstance(color, QColor):
            self.face_outline_color = color
        else:
            self.face_outline_color = QColor("#ff0000")
        self.update()

    def __init__(self):
        super().__init__()
        self.pupil_x = 0.0
        self.pupil_y = 0.0
        self.pupil_size_mod = 0.0
        self.shine_size_mod = 0.0
        self.upper_lid_tilt = 0.0
        self.upper_lid_open = 1.0
        self.lower_lid_tilt = 0.0
        self.lower_lid_open = 1.0
        self.eye_separation_offset = 0.0  # Obsoleto, ver abajo
        self.iris_convergence_offset = 0.0
        self.pupil_size_asymmetry = 0.0
        self.upper_lid_asymmetry = 0.0
        self.lower_lid_asymmetry = 0.0
        self.lid_curvature = 0.5
        self.led_intensity = 0.0
        self.screen_intensity = 0.0
        self.iris_color = QColor("red")
        self.face_color = QColor(255, 0, 0)  # Default to red
        self.face_outline_color = QColor("#ff0000")  # Default to red
        self.setMinimumSize(800, 500)

    def set_iris_color(self, color):
        if isinstance(color, str):
            self.iris_color = QColor(color)
        elif isinstance(color, QColor):
            self.iris_color = color
        self.update()

    def set_screen_intensity(self, val):
        self.screen_intensity = val
        self.update()

    def get_screen_color(self, base_color):
        # Pantalla apagada: Gris casi negro total (más oscuro)
        c_off = QColor(15, 15, 15)
        t = self.screen_intensity
        rr = c_off.red() + (base_color.red() - c_off.red()) * t
        gg = c_off.green() + (base_color.green() - c_off.green()) * t
        bb = c_off.blue() + (base_color.blue() - c_off.blue()) * t
        return QColor(int(rr), int(gg), int(bb))

    def set_lid_curvature(self, val):
        # val de 0.0 a 1.0
        self.lid_curvature = val
        self.update()

    def set_led_intensity(self, val):
        self.led_intensity = val
        self.update()

    def get_led_color(self):
        # Transición de Color: Red (On) -> Gris muy oscuro (Off)
        c_on = QColor("red")
        c_off = QColor(45, 45, 45)  # Gris oscuro elegante
        t = self.led_intensity
        rr = c_off.red() + (c_on.red() - c_off.red()) * t
        gg = c_off.green() + (c_on.green() - c_off.green()) * t
        bb = c_off.blue() + (c_on.blue() - c_off.blue()) * t
        return QColor(int(rr), int(gg), int(bb))

    def set_pupil_pos(self, x, y):
        self.pupil_x = x
        self.pupil_y = y
        self.update()

    def set_iris_convergence(self, value):
        # Mapeo de 0-100 a offset -30 a +30 pixeles para converger/diverger
        self.iris_convergence_offset = (value - 50) * 0.8
        self.update()

    def set_eye_separation(self, value):
        # Redirigir por compatibilidad si es necesario o simplemente borrar
        self.set_iris_convergence(value)

    def set_pupil_size(self, x, y):
        self.pupil_size_mod = x
        self.shine_size_mod = y
        self.update()

    def set_pupil_asymmetry(self, value):
        self.pupil_size_asymmetry = (value - 50) / 50.0  # -1.0 a 1.0
        self.update()

    def set_upper_lid(self, x, y):
        self.upper_lid_tilt = x
        self.upper_lid_open = y
        self.update()

    def set_upper_lid_asymmetry(self, value):
        self.upper_lid_asymmetry = (value - 50) / 50.0
        self.update()

    def set_lower_lid(self, x, y):
        self.lower_lid_tilt = x
        self.lower_lid_open = y
        self.update()

    def set_lower_lid_asymmetry(self, value):
        self.lower_lid_asymmetry = (value - 50) / 50.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background
        painter.fillRect(self.rect(), QColor("lightgray"))

        w = self.width()
        h = self.height()

        # Ojos subidos ligeramente y perfectamente tangentes al círculo superior de la cabeza
        R = 68
        cy = h / 2.0
        cy_eyes = cy - 30

        # Base separation is 215 (FIJA ahora, la asimetría es del iris)
        sep = 215
        cx1 = w / 2.0 - sep
        cx2 = w / 2.0 + sep

        # Primero dibujamos la cabeza
        self.draw_head(painter, w / 2.0, cy, w, h)

        # Luego los ojos (usando cy_eyes)
        self.draw_eye(painter, cx1, cy_eyes, R, mirror=1, eye_idx=0)
        self.draw_eye(painter, cx2, cy_eyes, R, mirror=-1, eye_idx=1)

    def draw_head(self, painter, cx, cy, w, h):
        import math

        # Tamaños fijos independientes de la ventana
        hh = 450
        r1 = 140
        r2 = 110

        # Geometría base circular para el robot (RESTABLECIDA)
        cy1 = cy - ((hh / 2) - r1) * 0.6
        cy2 = cy + ((hh / 2) - r2) * 0.6
        D = cy2 - cy1
        # Evitar division by zero or domain errors
        if D <= abs(r1 - r2):
            return
        phi = math.asin((r1 - r2) / D)
        theta = math.degrees(phi)

        # Camino base (Contorno Negro)
        path = QPainterPath()
        start_x = cx + r1 * math.cos(math.radians(-theta))
        start_y = cy1 - r1 * math.sin(math.radians(-theta))
        path.moveTo(start_x, start_y)
        path.arcTo(cx - r1, cy1 - r1, r1 * 2, r1 * 2, -theta, 180 + 2 * theta)
        left_c2_x = cx + r2 * math.cos(math.radians(180 + theta))
        left_c2_y = cy2 - r2 * math.sin(math.radians(180 + theta))
        path.lineTo(left_c2_x, left_c2_y)
        path.arcTo(cx - r2, cy2 - r2, r2 * 2, r2 * 2, 180 + theta, 180 - 2 * theta)
        path.lineTo(start_x, start_y)


        # Tamaños fijos independientes de la ventana
        hh = 450
        r1 = 140
        r2 = 110

        # Geometría base circular para el robot (RESTABLECIDA)
        cy1 = cy - ((hh / 2) - r1) * 0.6
        cy2 = cy + ((hh / 2) - r2) * 0.6
        D = cy2 - cy1
        # Evitar division by zero or domain errors
        if D <= abs(r1 - r2):
            return
        phi = math.asin((r1 - r2) / D)
        theta = math.degrees(phi)

        # Camino base (Contorno Negro)
        path = QPainterPath()
        start_x = cx + r1 * math.cos(math.radians(-theta))
        start_y = cy1 - r1 * math.sin(math.radians(-theta))
        path.moveTo(start_x, start_y)
        path.arcTo(cx - r1, cy1 - r1, r1 * 2, r1 * 2, -theta, 180 + 2 * theta)
        left_c2_x = cx + r2 * math.cos(math.radians(180 + theta))
        left_c2_y = cy2 - r2 * math.sin(math.radians(180 + theta))
        path.lineTo(left_c2_x, left_c2_y)
        path.arcTo(cx - r2, cy2 - r2, r2 * 2, r2 * 2, 180 + theta, 180 - 2 * theta)
        path.lineTo(start_x, start_y)

        # 1. Semicírculo superior negro (head background)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("black"))
        painter.drawChord(QRectF(cx - r1, cy1 - r1, r1 * 2, r1 * 2), 0, 180 * 16)

        # 1b. (Removed semicircle fill for front face)

        # Círculo negro central (Núcleo al fondo)
        painter.setBrush(QColor("black"))
        painter.drawEllipse(QPointF(cx, cy1), r1 / 2, r1 / 2)

        # Elipse azul celeste muy alargada - Ajustada (-10% largo y subida 5px)
        r_major = r1 * 0.85
        r_minor = r1 * 0.11
        # Color dinámico (On: Skyblue, Off: DarkGray)
        color_led = self.get_led_color()

        # Subida ligeramente (5px más arriba de la base cy1)
        painter.setBrush(color_led)
        painter.drawEllipse(QPointF(cx, cy1 - r_minor - 5), r_major, r_minor)

        # 2. Contorno base negro (Circular)
        pen = QPen(QColor("black"))
        pen.setWidth(12)  # Ligeramente más grueso
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        # 3. Segundo contorno: color configurable (face_outline_color)
        pen_outline = QPen(self.face_outline_color)
        pen_outline.setWidth(3)
        pen_outline.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen_outline)
        painter.drawPath(path)


    def draw_eye(self, painter, cx, cy, R, mirror, eye_idx):
        painter.save()

        # 1. Base Eyeball and Clip Region
        eye_path = QPainterPath()
        eye_path.addEllipse(QPointF(cx, cy), R, R)

        painter.setClipPath(eye_path)

        # Color de fondo (Esclera) condicional al encendido
        painter.setBrush(self.get_screen_color(QColor("white")))
        painter.setPen(Qt.NoPen)
        painter.drawPath(eye_path)

        # 2. Iris (Azul) - Escalable
        iris_R = R * 0.6
        conv_shift = (
            self.iris_convergence_offset
            if eye_idx == 0
            else -self.iris_convergence_offset
        )
        px_offset = self.pupil_x * (R - iris_R) * 1.2 + conv_shift
        py_offset = -self.pupil_y * (R - iris_R) * 1.2
        iris_cx = cx + px_offset
        iris_cy = cy + py_offset

        painter.setBrush(self.get_screen_color(self.iris_color))
        painter.drawEllipse(QPointF(iris_cx, iris_cy), iris_R, iris_R)

        # 3. Pupila interna (Negra) - Desplazada para efecto esférico
        asym_mod = (
            self.pupil_size_asymmetry if eye_idx == 1 else -self.pupil_size_asymmetry
        )
        base_pupil_r = iris_R * 0.4
        current_pupil_mod = max(-1.0, min(1.0, self.pupil_size_mod + asym_mod * 0.3))

        if current_pupil_mod > 0:
            pupil_r = base_pupil_r + current_pupil_mod * (iris_R - base_pupil_r)
        else:
            pupil_r = base_pupil_r + current_pupil_mod * (base_pupil_r - iris_R * 0.1)

        # Efecto Parallax: la pupila se desplaza un poco más que el iris hacia el borde
        raw_p_off_x = self.pupil_x * pupil_r * 0.65
        raw_p_off_y = -self.pupil_y * pupil_r * 0.65

        # Restricción: la pupila NUNCA sobrepasa el borde del iris
        # Distancia máxima permitida para el centro de la pupila
        max_p_dist = max(0.0, iris_R - pupil_r)
        curr_dist = (raw_p_off_x**2 + raw_p_off_y**2) ** 0.5

        p_off_x, p_off_y = raw_p_off_x, raw_p_off_y
        if curr_dist > max_p_dist and curr_dist > 0:
            p_off_x = raw_p_off_x * max_p_dist / curr_dist
            p_off_y = raw_p_off_y * max_p_dist / curr_dist

        painter.setBrush(self.get_screen_color(QColor("black")))
        painter.drawEllipse(
            QPointF(iris_cx + p_off_x, iris_cy + p_off_y), pupil_r, pupil_r
        )

        # 4. Brillo (Blanco) - El brillo SÍ puede salirse un poco para realismo
        shine_r = max(0.0, self.shine_size_mod * (pupil_r * 0.7))
        if shine_r > 0.05:
            offset_x = pupil_r * 0.45 + raw_p_off_x * 0.5
            offset_y = -pupil_r * 0.45 + raw_p_off_y * 0.5
            painter.setBrush(self.get_screen_color(QColor("white")))
            painter.drawEllipse(
                QPointF(iris_cx + offset_x, iris_cy + offset_y), shine_r, shine_r
            )

        # 5. Párpados (Negros) con asimetria
        up_asym = (
            self.upper_lid_asymmetry if eye_idx == 1 else -self.upper_lid_asymmetry
        )
        low_asym = (
            self.lower_lid_asymmetry if eye_idx == 1 else -self.lower_lid_asymmetry
        )

        current_upper_open = max(-1.0, min(1.5, self.upper_lid_open + up_asym * 0.5))
        # El parpado inferior como mucho hasta la mitad (0.0)
        current_lower_open = max(-1.5, min(1.5, self.lower_lid_open + low_asym * 0.5))

        # Dibujamos primero el inferior (fondo) y luego el superior (encima) en el eje Z
        y_lid_low = cy + R * current_lower_open
        self.draw_lid_poly(
            painter,
            cx,
            cy,
            R,
            y_lid_low,
            self.lower_lid_tilt,
            mirror,
            is_upper=False,
            norm_open=current_lower_open,
        )

        y_lid = cy - R * current_upper_open
        self.draw_lid_poly(
            painter,
            cx,
            cy,
            R,
            y_lid,
            self.upper_lid_tilt,
            mirror,
            is_upper=True,
            norm_open=current_upper_open,
        )

        painter.restore()

        # 6. Borde negro fijo y perimetral de los ojos
        border_pen = QPen(QColor("black"))
        border_pen.setWidth(8)
        painter.setPen(border_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(eye_path)

    def draw_lid_poly(
        self, painter, cx, cy, R, y_offset, tilt, mirror=1, is_upper=True, norm_open=1.0
    ):
        dx = 1.5 * R
        m_tilt = tilt * mirror
        dy = m_tilt * R * 0.8

        # Cálculo de Curvatura Complementaria (Efecto Puzzle)
        # 0.5 es neutral (bias 0.0), < 0.5 es bias negativo (sube), > 0.5 es bias positivo (baja)
        # Rango muy reducido para máxima sutileza
        bias = (self.lid_curvature - 0.5) * R * 2.4

        if is_upper:
            curve_factor = (-norm_open * R * 1.6) + bias
        else:
            curve_factor = (abs(norm_open) * R * 1.6) + bias

        # Compensación de Apex:
        # Para que el punto más alto del párpado esté siempre en la posición del joystick,
        # ajustamos y_offset sabiendo que el apex de una Bezier cuadrática regular
        # está en y_center + 0.5 * curve_factor. Por tanto y_center = y_target - 0.5*cf
        y_center = y_offset - 0.5 * curve_factor

        p1_x = cx - dx
        p1_y = y_center - dy
        p2_x = cx + dx
        p2_y = y_center + dy

        cp_x = cx
        cp_y = y_center + curve_factor

        path = QPainterPath()
        path.moveTo(p1_x, p1_y)
        path.quadTo(cp_x, cp_y, p2_x, p2_y)

        if is_upper:
            path.lineTo(cx + dx, cy - dx * 2)
            path.lineTo(cx - dx, cy - dx * 2)
        else:
            path.lineTo(cx + dx, cy + dx * 2)
            path.lineTo(cx - dx, cy + dx * 2)

        path.closeSubpath()

        # Los párpados son parte de la pantalla (se oscurecen al apagar)
        painter.setBrush(self.get_screen_color(QColor(50, 50, 50)))
        pen = QPen(self.get_screen_color(QColor("black")))
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawPath(path)


class CirclesInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animatronic Eyes")
        self.resize(1000, 600)
        self.setStyleSheet("background-color: lightgray;")

        layout = QHBoxLayout(self)
        self.is_awake = False
        self.is_blinking = False
        self.leds_enabled = True  # Estado lógico deseado para los LEDs

        # Controls Layout
        controls_layout = QVBoxLayout()
        controls_layout.setSpacing(5)

        self.joy_pos = JoystickWidget("Posición (X/Y)", 0.0, 0.0)
        self.joy_sizes = JoystickWidget("Tamaños (Pupila / Brillo)", 0.0, 0.0)
        # Iniciar CERRADO (pose de pestaña con tilt interior)
        self.joy_upper = JoystickWidget("Párpado Superior", 0.3, -0.32)
        self.joy_lower = JoystickWidget("Párpado Inferior", 0.3, 0.28)

        # Añadir controles con sliders para asimetría
        self.slider1 = self._create_asym_slider()
        self.slider2 = self._create_asym_slider()
        self.slider3 = self._create_asym_slider()
        self.slider4 = self._create_asym_slider()
        self.slider5 = self._create_asym_slider() # Nuevo: Curvatura Global

        controls_layout.addLayout(self._wrap_with_slider(self.joy_pos, self.slider1))
        controls_layout.addLayout(self._wrap_with_slider(self.joy_sizes, self.slider2))
        controls_layout.addLayout(self._wrap_with_slider(self.joy_upper, self.slider3))
        
        # El parpado inferior tiene el de asimetría y el de curvatura
        lower_joy_layout = QHBoxLayout()
        lower_joy_layout.addWidget(self.joy_lower)
        lower_joy_layout.addWidget(self.slider4)
        lower_joy_layout.addWidget(self.slider5)
        controls_layout.addLayout(lower_joy_layout)

        self.btn_blink = QPushButton("PARPADEO (Blink)")
        self.btn_blink.setMinimumHeight(40)
        self.btn_blink.setCursor(Qt.PointingHandCursor)
        self.btn_blink.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #3b3b3b; }
        """)
        self.btn_blink.clicked.connect(self.animate_blink)

        self.btn_leds = QPushButton()
        self.btn_leds.setMinimumHeight(40)
        self.btn_leds.setCursor(Qt.PointingHandCursor)
        self._update_led_button_style()
        self.btn_leds.clicked.connect(self.toggle_leds)

        # --- Configuración de Sliders de Parpadeo ---
        self.slider_blink_speed = QSlider(Qt.Horizontal)
        self.slider_blink_speed.setRange(210, 850)
        self.slider_blink_speed.setValue(340)

        self.slider_blink_freq = QSlider(Qt.Horizontal)
        self.slider_blink_freq.setRange(0, 20)
        self.slider_blink_freq.setValue(0)

        blink_label = QLabel("Duración Blink")
        blink_label.setAlignment(Qt.AlignCenter)
        blink_label.setStyleSheet("color: #444; font-size: 10px;")

        freq_label = QLabel("Frecuencia (Seg)")
        freq_label.setAlignment(Qt.AlignCenter)
        freq_label.setStyleSheet("color: #444; font-size: 10px;")

        # Empaquetar en el layout principal
        controls_layout.addWidget(self.btn_blink)

        blink_sliders_layout = QHBoxLayout()
        blink_sliders_layout.addWidget(self.slider_blink_speed)
        blink_sliders_layout.addWidget(self.slider_blink_freq)
        controls_layout.addLayout(blink_sliders_layout)

        blink_labels_layout = QHBoxLayout()
        blink_labels_layout.addWidget(blink_label)
        blink_labels_layout.addWidget(freq_label)
        controls_layout.addLayout(blink_labels_layout)

        controls_layout.addWidget(self.btn_leds)

        self.auto_blink_timer = QTimer()
        self.auto_blink_timer.timeout.connect(self.animate_blink)
        self.slider_blink_freq.valueChanged.connect(self.update_auto_blink)

        self.btn_reset = QPushButton("RESTABLECER (Reset)")
        self.btn_reset.setMinimumHeight(40)
        self.btn_reset.setCursor(Qt.PointingHandCursor)
        self.btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #4a1515;
                color: white;
                font-weight: bold;
                border: 2px solid #632222;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #5a1a1a; }
            QPushButton:pressed { background-color: #3a1010; }
        """)
        self.btn_reset.clicked.connect(self.animate_reset)
        controls_layout.addWidget(self.btn_reset)

        self.btn_power = QPushButton("DESPERTAR (Wake Up)")
        self.btn_power.setMinimumHeight(50)
        self.is_awake = False
        self.btn_power.setStyleSheet("""
            QPushButton {
                background-color: #1a4a15;
                color: white;
                font-weight: bold;
                border: 2px solid #226322;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1e5a1a; }
        """)
        self.btn_power.clicked.connect(self.toggle_power)
        controls_layout.addWidget(self.btn_power)

        self.eyes = EyesWidget()
        # Inicializar ojos en el estado de los mandos (cerrados y apagados)
        self._sync_all_params()
        # Asegurar intensidades en 0 al inicio
        self.eyes.set_led_intensity(0.0)
        self.eyes.set_screen_intensity(0.0)
        self.is_blinking = False

        layout.addLayout(controls_layout, 1)
        layout.addWidget(self.eyes, 4)

        # Connect signals via proxies
        self.joy_pos.positionChanged.connect(self._sync_pupil_pos)
        self.joy_sizes.positionChanged.connect(self._sync_pupil_size)
        self.joy_upper.positionChanged.connect(self._sync_upper_lid)
        self.joy_lower.positionChanged.connect(self._sync_lower_lid)

        self.slider1.valueChanged.connect(self._sync_iris_conv)
        self.slider2.valueChanged.connect(self._sync_pupil_asym)
        self.slider3.valueChanged.connect(self._sync_upper_asym)
        self.slider4.valueChanged.connect(self._sync_lower_asym)
        self.slider5.valueChanged.connect(self._sync_curvature)

    def _sync_pupil_pos(self, x, y):
        # Permitimos mover el iris incluso parpadeando
        self.eyes.set_pupil_pos(x, y)

    def _sync_pupil_size(self, x, y):
        self.eyes.set_pupil_size(x, y)

    def _sync_upper_lid(self, x, y):
        if not self.is_blinking:
            self.eyes.set_upper_lid(x, y)

    def _sync_lower_lid(self, x, y):
        if not self.is_blinking:
            self.eyes.set_lower_lid(x, y)

    def _sync_iris_conv(self, v):
        self.eyes.set_iris_convergence(v)

    def _sync_pupil_asym(self, v):
        self.eyes.set_pupil_asymmetry(v)

    def _sync_upper_asym(self, v):
        if not self.is_blinking:
            self.eyes.set_upper_lid_asymmetry(v)

    def _sync_lower_asym(self, v):
        if not self.is_blinking:
            self.eyes.set_lower_lid_asymmetry(v)

    def _sync_curvature(self, v):
        # Mapeo de slider 0-100 a 0.0-1.0
        self.eyes.set_lid_curvature(v / 100.0)

    def _create_asym_slider(self):
        slider = QSlider(Qt.Vertical)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setFixedWidth(20)
        slider.setStyleSheet("""
            QSlider::groove:vertical {
                background: #444;
                width: 4px;
                border-radius: 2px;
            }
            QSlider::handle:vertical {
                background: #888;
                height: 14px;
                margin: 0 -5px;
                border-radius: 7px;
            }
        """)
        return slider

    def _wrap_with_slider(self, joy, slider):
        hbox = QHBoxLayout()
        hbox.addWidget(joy)
        hbox.addWidget(slider)
        return hbox

    def animate_blink(self):
        if self.is_blinking:
            return
        if (
            hasattr(self, "blink_anim")
            and self.blink_anim.state() == QVariantAnimation.Running
        ):
            return

        self.btn_blink.setDisabled(True)
        self.is_blinking = True

        # Recuperar estado actual
        start_u_y = self.joy_upper.pos_y
        start_u_x = self.joy_upper.pos_x
        start_l_y = self.joy_lower.pos_y
        start_l_x = self.joy_lower.pos_x

        # Objetivos de cierre condicionales
        blink_default_l = 0.28
        # Objetivos de cierre condicionales (Más profundos para asegurar contacto)
        blink_default_l = 0.4

        if start_l_y > blink_default_l:
            # Caso normal: el inferior se mueve al target profundo
            target_l_y = blink_default_l
            target_u_y = -0.45  # Solapamiento ajustado (antes -0.5)
            target_tilt_l = 0.3
        else:
            # Caso entrecerrado: el inferior se queda, el superior baja a buscarlo
            target_l_y = start_l_y
            target_u_y = -(start_l_y + 0.05)  # Solapamiento ajustado (antes 0.15)
            target_tilt_l = start_l_x

        # El parpado superior siempre se alinea al inferior
        target_tilt_u = target_tilt_l

        duration = self.slider_blink_speed.value()

        self.blink_anim = QVariantAnimation()
        self.reset_anim = None
        self.blink_anim.setDuration(duration)
        self.blink_anim.setStartValue(0.0)
        self.blink_anim.setEndValue(1.0)

        # Fases de animación: 0.0-0.4 cierre, 0.4-0.6 reposo (cerrado), 0.6-1.0 apertura
        def update_blink(v):
            if v <= 0.4:
                # Fase de cierre
                t = v / 0.4
                curr_u = start_u_y + (target_u_y - start_u_y) * t
                curr_l = start_l_y + (target_l_y - start_l_y) * t
                curr_u_x = start_u_x + (target_tilt_u - start_u_x) * t
                curr_l_x = start_l_x + (target_tilt_l - start_l_x) * t
            elif v <= 0.6:
                # Fase de reposo cerrado
                curr_u = target_u_y
                curr_l = target_l_y
                curr_u_x = target_tilt_u
                curr_l_x = target_tilt_l
            else:
                # Fase de apertura
                t = (v - 0.6) / 0.4
                curr_u = target_u_y + (start_u_y - target_u_y) * t
                curr_l = target_l_y + (start_l_y - target_l_y) * t
                curr_u_x = target_tilt_u + (start_u_x - target_tilt_u) * t
                curr_l_x = target_tilt_l + (start_l_x - target_tilt_l) * t

            self.eyes.set_upper_lid(curr_u_x, curr_u)
            self.eyes.set_lower_lid(curr_l_x, curr_l)

        self.blink_anim.valueChanged.connect(update_blink)
        self.blink_anim.finished.connect(self._on_blink_finished)
        self.blink_anim.start()

    def _on_blink_finished(self):
        self.is_blinking = False
        self.btn_blink.setDisabled(False)
        # Sincronizar estado final con posición actual de mandos
        self.eyes.set_upper_lid(self.joy_upper.pos_x, self.joy_upper.pos_y)
        self.eyes.set_lower_lid(self.joy_lower.pos_x, self.joy_lower.pos_y)

    def animate_reset(self):
        if self.is_blinking:
            return
        self.is_blinking = True
        # Capturar estados actuales
        start_state = {
            "p_x": self.joy_pos.pos_x,
            "p_y": self.joy_pos.pos_y,
            "s_x": self.joy_sizes.pos_x,
            "s_y": self.joy_sizes.pos_y,
            "u_x": self.joy_upper.pos_x,
            "u_y": self.joy_upper.pos_y,
            "l_x": self.joy_lower.pos_x,
            "l_y": self.joy_lower.pos_y,
            "sl1": self.slider1.value(),
            "sl2": self.slider2.value(),
            "sl3": self.slider3.value(),
            "sl4": self.slider4.value(),
            "sl5": self.slider5.value(),
        }

        # Objetivos
        end_state = {
            "p_x": 0.0,
            "p_y": 0.0,
            "s_x": 0.0,
            "s_y": 0.0,
            "u_x": 0.0,
            "u_y": 1.0,
            "l_x": 0.0,
            "l_y": 1.0,
            "sl1": 50,
            "sl2": 50,
            "sl3": 50,
            "sl4": 50,
            "sl5": 50,
        }

        self.reset_anim = QVariantAnimation()
        self.reset_anim.setDuration(500)  # 500ms de suavidad
        self.reset_anim.setStartValue(0.0)
        self.reset_anim.setEndValue(1.0)

        def update_values(v):
            def lerp(a, b, t):
                return a + (b - a) * t

            ux = lerp(start_state["u_x"], end_state["u_x"], v)
            uy = lerp(start_state["u_y"], end_state["u_y"], v)
            lx = lerp(start_state["l_x"], end_state["l_x"], v)
            ly = lerp(start_state["l_y"], end_state["l_y"], v)
            px = lerp(start_state["p_x"], end_state["p_x"], v)
            py = lerp(start_state["p_y"], end_state["p_y"], v)
            sx = lerp(start_state["s_x"], end_state["s_x"], v)
            sy = lerp(start_state["s_y"], end_state["s_y"], v)

            # Actualizar todos los joysticks (UI)
            self.joy_pos.set_pos(px, py)
            self.joy_sizes.set_pos(sx, sy)
            self.joy_upper.set_pos(ux, uy)
            self.joy_lower.set_pos(lx, ly)

            # Actualizar sliders (UI)
            v1 = int(lerp(start_state["sl1"], end_state["sl1"], v))
            v2 = int(lerp(start_state["sl2"], end_state["sl2"], v))
            v3 = int(lerp(start_state["sl3"], end_state["sl3"], v))
            v4 = int(lerp(start_state["sl4"], end_state["sl4"], v))
            v5 = int(lerp(start_state["sl5"], end_state["sl5"], v))
            self.slider1.setValue(v1)
            self.slider2.setValue(v2)
            self.slider3.setValue(v3)
            self.slider4.setValue(v4)
            self.slider5.setValue(v5)

            # Actualizar ojos DIRECTAMENTE (el proxy bloquea mientras is_blinking=True)
            self.eyes.set_pupil_pos(px, py)
            self.eyes.set_pupil_size(sx, sy)
            self.eyes.set_upper_lid(ux, uy)
            self.eyes.set_lower_lid(lx, ly)
            self.eyes.set_iris_convergence(v1)
            self.eyes.set_pupil_asymmetry(v2)
            self.eyes.set_upper_lid_asymmetry(v3)
            self.eyes.set_lower_lid_asymmetry(v4)
            self.eyes.set_lid_curvature(v5 / 100.0)

        self.reset_anim.valueChanged.connect(update_values)
        self.reset_anim.finished.connect(self._on_reset_finished)
        self.reset_anim.start()

    def _on_reset_finished(self):
        self.is_blinking = False

    def update_auto_blink(self):
        val = self.slider_blink_freq.value()
        if val == 0:
            self.auto_blink_timer.stop()
        else:
            # val es segundos entre parpadeos
            self.auto_blink_timer.start(val * 1000)

    def _sync_all_params(self):
        # Sincronización inicial o tras animación
        self.eyes.set_pupil_pos(self.joy_pos.pos_x, self.joy_pos.pos_y)
        self.eyes.set_pupil_size(self.joy_sizes.pos_x, self.joy_sizes.pos_y)
        self.eyes.set_upper_lid(self.joy_upper.pos_x, self.joy_upper.pos_y)
        self.eyes.set_lower_lid(self.joy_lower.pos_x, self.joy_lower.pos_y)
        self.eyes.set_iris_convergence(self.slider1.value())
        self.eyes.set_pupil_asymmetry(self.slider2.value())
        self.eyes.set_upper_lid_asymmetry(self.slider3.value())
        self.eyes.set_lower_lid_asymmetry(self.slider4.value())
        self.eyes.set_lid_curvature(self.slider5.value() / 100.0)

    def toggle_power(self):
        if self.is_blinking:
            return

        if not self.is_awake:
            self.animate_power(wake=True)
        else:
            self.animate_power(wake=False)

    def animate_power(self, wake=True):
        self.is_blinking = True  # Bloquear

        if wake:
            # --- FASE 1: Encendido de Pantallas y LEDs ---
            led_start = self.eyes.led_intensity
            led_target = 1.0 if self.leds_enabled else 0.0

            self.screen_anim = QVariantAnimation()
            self.screen_anim.setDuration(1200)  # Fundido suave de aparición
            self.screen_anim.setStartValue(0.0)
            self.screen_anim.setEndValue(1.0)

            def update_screens(v):
                def lerp(a, b, t):
                    return a + (b - a) * t

                self.eyes.set_screen_intensity(v)
                self.eyes.set_led_intensity(lerp(led_start, led_target, v))

            self.screen_anim.valueChanged.connect(update_screens)

            def start_phase_2():
                # --- FASE 2: Espera de 1 segundo ---
                QTimer.singleShot(1000, start_phase_3)

            def start_phase_3():
                # --- FASE 3: Apertura de Párpados ---
                self._run_eyelid_power_anim(wake=True)

            self.screen_anim.finished.connect(start_phase_2)
            self.screen_anim.start()
        else:
            # Al dormir, bajamos todo a la vez (Pantallas, Párpados y LEDs)
            self._run_eyelid_power_anim(wake=False, fade_screens=True)

    def _run_eyelid_power_anim(self, wake, fade_screens=False):
        # Implementación de la animación de párpados (antigua animate_power)
        s_u_y, s_u_x = self.joy_upper.pos_y, self.joy_upper.pos_x
        s_l_y, s_l_x = self.joy_lower.pos_y, self.joy_lower.pos_x
        s_screen = self.eyes.screen_intensity

        # Objetivos
        if wake:
            t_u_y, t_u_x = 1.0, 0.0
            t_l_y, t_l_x = 1.0, 0.0
        else:
            t_u_y, t_u_x = -0.45, 0.3
            t_l_y, t_l_x = 0.4, 0.3

        led_start = self.eyes.led_intensity
        led_target = (1.0 if self.leds_enabled else 0.0) if wake else 0.0
        screen_target = 1.0 if wake else 0.0

        self.power_anim = QVariantAnimation()
        # Apertura rápida (250ms) al despertar, dormir lento (1500ms)
        self.power_anim.setDuration(250 if wake else 1500)
        self.power_anim.setStartValue(0.0)
        self.power_anim.setEndValue(1.0)

        def update_p(v):
            def lerp(a, b, t):
                return a + (b - a) * t

            self.joy_upper.set_pos(lerp(s_u_x, t_u_x, v), lerp(s_u_y, t_u_y, v))
            self.joy_lower.set_pos(lerp(s_l_x, t_l_x, v), lerp(s_l_y, t_l_y, v))

            # Actualizar ojos
            self.eyes.set_upper_lid(self.joy_upper.pos_x, self.joy_upper.pos_y)
            self.eyes.set_lower_lid(self.joy_lower.pos_x, self.joy_lower.pos_y)
            self.eyes.set_led_intensity(lerp(led_start, led_target, v))
            if fade_screens:
                self.eyes.set_screen_intensity(lerp(s_screen, screen_target, v))

        self.power_anim.valueChanged.connect(update_p)

        def on_finished():
            self.is_blinking = False
            self.is_awake = wake
            if wake:
                self.btn_power.setText("DORMIR (Sleep)")
                self.btn_power.setStyleSheet(
                    "background-color: #4a1515; color: white; font-weight: bold; border-radius: 8px; font-size: 14px;"
                )
                self.slider_blink_freq.setValue(3)
            else:
                self.btn_power.setText("DESPERTAR (Wake Up)")
                self.btn_power.setStyleSheet(
                    "background-color: #1a4a15; color: white; font-weight: bold; border-radius: 8px; font-size: 14px;"
                )
                self.slider_blink_freq.setValue(0)

        self.power_anim.finished.connect(on_finished)
        self.power_anim.start()

    def toggle_leds(self):
        # Transición suave de los LEDs azul celeste
        if (
            hasattr(self, "led_anim")
            and self.led_anim
            and self.led_anim.state() == QVariantAnimation.Running
        ):
            return

        self.leds_enabled = not self.leds_enabled  # Invertir estado lógico
        self._update_led_button_style()

        start_v = self.eyes.led_intensity
        end_v = 1.0 if self.leds_enabled else 0.0

        self.led_anim = QVariantAnimation()
        self.led_anim.setDuration(800)  # 800ms para un fundido elegante
        self.led_anim.setStartValue(start_v)
        self.led_anim.setEndValue(end_v)
        self.led_anim.valueChanged.connect(self.eyes.set_led_intensity)
        self.led_anim.start()

    def _update_led_button_style(self):
        if self.leds_enabled:
            self.btn_leds.setText("LEDS: ON")
            self.btn_leds.setStyleSheet("""
                QPushButton {
                    background-color: #8d0000;
                    color: white; font-weight: bold;
                    border: 2px solid #ff0000; border-radius: 8px;
                }
                QPushButton:hover { background-color: #b20000; }
            """)
        else:
            self.btn_leds.setText("LEDS: OFF")
            self.btn_leds.setStyleSheet("""
                QPushButton {
                    background-color: #2b2b2b;
                    color: #888; font-weight: bold;
                    border: 2px solid #444; border-radius: 8px;
                }
                QPushButton:hover { background-color: #3b3b3b; }
            """)


def main():
    # Permite capturar la señal SIGINT (Ctrl+C) ordenadamente
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    window = CirclesInterface()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
