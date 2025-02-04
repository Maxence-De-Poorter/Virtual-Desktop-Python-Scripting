from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer, QTime
import sys
import os

class BureauVirtuel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bureau Virtuel")
        self.setGeometry(100, 100, 800, 600)
        
        # Création du widget principal (le bureau)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Ajouter la barre des tâches
        self.init_taskbar()

    def init_taskbar(self):
        """Crée et ajoute une barre des tâches en bas de la fenêtre."""
        self.taskbar = QWidget(self)
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        self.taskbar.setStyleSheet("background-color: #222; color: white;")

        # Layout de la barre des tâches
        layout = QHBoxLayout(self.taskbar)
        layout.setContentsMargins(5, 5, 10, 5)
        layout.setSpacing(10)

        # Charger l'icône du bouton Démarrer
        icon_path = os.path.join(os.path.dirname(__file__), "assets/start_icon.png")
        self.start_button = QPushButton("")
        self.start_button.setFixedSize(40, 40)
        self.start_button.setIcon(QIcon(icon_path))  # Ajout de l'icône
        self.start_button.setIconSize(self.start_button.size())  # Ajuste l'icône à la taille du bouton
        self.start_button.setStyleSheet("""
            QPushButton {
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        layout.addWidget(self.start_button)

        # Ajout d'un espace entre le bouton Démarrer et l'horloge
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)

        # Horloge
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock_label.setStyleSheet("font-size: 16px; padding-right: 10px;")  # Ajout d'un padding à droite

        # Timer pour mettre à jour l'heure
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Mise à jour toutes les secondes
        self.update_time()

        layout.addWidget(self.clock_label)
        self.taskbar.setLayout(layout)

    def update_time(self):
        """Met à jour l'horloge de la barre des tâches."""
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.clock_label.setText(current_time)

    def resizeEvent(self, event):
        """Met à jour la barre des tâches lors du redimensionnement de la fenêtre."""
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BureauVirtuel()
    window.show()
    sys.exit(app.exec())
