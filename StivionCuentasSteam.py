import sys
import random
import threading
import time
import os
from dotenv import load_dotenv

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSizePolicy, QSpacerItem
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QRect, QTimer
from PyQt6.QtGui import QFont, QColor, QPalette

from supabase import create_client, Client

# Cargar variables del .env
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise Exception("❌ No se encontraron SUPABASE_URL o SUPABASE_KEY en el .env")

supabase: Client = create_client(url, key)

class CuentaGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Cuentas")
        self.setFixedSize(800, 600)

        self.cuentas_usadas = 0
        self.total_cuentas = 0
        self.usuarios_conectados = 0

        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(20, 20, 20))
        self.setPalette(pal)

        self.init_ui()
        self.start_updater()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        title = QLabel("Generador de Cuentas")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        self.boton = QPushButton("Obtener cuenta")
        self.boton.setFixedSize(250, 60)
        self.boton.setStyleSheet("""
            QPushButton {
                background-color: #4169E1;
                color: white;
                border-radius: 12px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #6495ED;
            }
            QPushButton:pressed {
                background-color: #1E3F8F;
            }
        """)
        self.boton.clicked.connect(self.obtener_cuenta)
        main_layout.addWidget(self.boton, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Área de cuenta
        self.usuario_label = QLabel("Usuario:")
        self.usuario_label.setStyleSheet("color: #B0B0B0; font-size: 16px;")
        self.usuario_val = QLabel("")
        self.usuario_val.setStyleSheet("color: #E6E6E6; font-size: 20px; font-weight: bold;")
        self.usuario_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        self.contrasena_label = QLabel("Contraseña:")
        self.contrasena_label.setStyleSheet("color: #B0B0B0; font-size: 16px;")
        self.contrasena_val = QLabel("")
        self.contrasena_val.setStyleSheet("color: #E6E6E6; font-size: 20px; font-weight: bold;")
        self.contrasena_val.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

        cuenta_layout = QVBoxLayout()
        user_hbox = QHBoxLayout()
        user_hbox.addWidget(self.usuario_label)
        user_hbox.addWidget(self.usuario_val)
        cuenta_layout.addLayout(user_hbox)

        pass_hbox = QHBoxLayout()
        pass_hbox.addWidget(self.contrasena_label)
        pass_hbox.addWidget(self.contrasena_val)
        cuenta_layout.addLayout(pass_hbox)

        main_layout.addLayout(cuenta_layout)

        self.indicador = QLabel("")
        self.indicador.setStyleSheet("color: #64ff64; font-size: 14px;")
        self.indicador.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.indicador)

        main_layout.addStretch()

        # Status inferior
        status_layout = QHBoxLayout()
        self.label_usuarios = QLabel("Usuarios conectados: 0")
        self.label_usuarios.setStyleSheet("color: #909090; font-size: 12px;")
        self.label_cuentas_usadas = QLabel("Cuentas usadas: 0")
        self.label_cuentas_usadas.setStyleSheet("color: #909090; font-size: 12px;")
        self.label_cuentas_libres = QLabel("Total cuentas: 0")
        self.label_cuentas_libres.setStyleSheet("color: #909090; font-size: 12px;")

        status_layout.addWidget(self.label_usuarios)
        status_layout.addWidget(self.label_cuentas_usadas)
        status_layout.addWidget(self.label_cuentas_libres)
        main_layout.addLayout(status_layout)

        self.setLayout(main_layout)

    def obtener_cuenta(self):
        cuentas = supabase.table('cuentas').select('id, usuario, contrasena').execute()
        if cuentas.data and len(cuentas.data) > 0:
            cuenta_random = random.choice(cuentas.data)
            self.usuario_val.setText(cuenta_random['usuario'])
            self.contrasena_val.setText(cuenta_random['contrasena'])
            self.cuentas_usadas += 1
            self.indicador.setText("✅ Cuenta mostrada")
            self.indicador.setStyleSheet("color: #64ff64; font-size: 14px;")
            self.animar_fade_scale(self.usuario_val)
            self.animar_fade_scale(self.contrasena_val)
            self.animar_fade_scale(self.indicador)
        else:
            self.usuario_val.setText("")
            self.contrasena_val.setText("")
            self.indicador.setText("❌ No hay cuentas disponibles")
            self.indicador.setStyleSheet("color: #ff6464; font-size: 14px;")
            self.animar_fade_scale(self.indicador)

    def animar_fade_scale(self, widget):
        duration = 600
        fade_anim = QPropertyAnimation(widget, b"windowOpacity")
        fade_anim.setStartValue(0.0)
        fade_anim.setEndValue(1.0)
        fade_anim.setDuration(duration)
        fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        rect = widget.geometry()
        center = rect.center()
        start_rect = QRect(center.x(), center.y(), 0, 0)
        scale_anim = QPropertyAnimation(widget, b"geometry")
        scale_anim.setStartValue(start_rect)
        scale_anim.setEndValue(rect)
        scale_anim.setDuration(duration)
        scale_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)

        group = QParallelAnimationGroup()
        group.addAnimation(fade_anim)
        group.addAnimation(scale_anim)
        group.start()
        widget.anim = group  # evita garbage collection

    def actualizar_datos(self):
        total = supabase.table('cuentas').select('id').execute()
        self.total_cuentas = len(total.data) if total and total.data else 0
        self.label_cuentas_libres.setText(f"Total cuentas: {self.total_cuentas}")
        self.label_cuentas_usadas.setText(f"Cuentas mostradas: {self.cuentas_usadas}")
        self.label_usuarios.setText(f"Usuarios conectados: {self.usuarios_conectados}")

    def start_updater(self):
        def loop():
            while True:
                QTimer.singleShot(0, self.actualizar_datos)
                time.sleep(4)
        threading.Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CuentaGenerator()
    window.show()
    sys.exit(app.exec())
