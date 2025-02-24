import os
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon

class StartButton(QPushButton):
    def __init__(self):
        super().__init__("")
        self.setFixedSize(40, 40)

        # Charger l'icône
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/start_icon.png")
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.size())

        # 📌 Enlever le fond pour qu’il s’intègre dans la barre unifiée
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
