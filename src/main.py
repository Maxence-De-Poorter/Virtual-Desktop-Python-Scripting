# main.py

import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.taskbar import TaskBar
import django
from django.contrib.auth.models import User

# Configuration Django pour la gestion des fichiers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/../virtualfs"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virtualfs.settings")
django.setup()

class BureauVirtuel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bureau Virtuel")
        self.setGeometry(100, 100, 1080, 720)
        self.setMinimumSize(1080, 720)

        # Fond d'écran
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_pixmap = QPixmap(os.path.join("assets", "background.jpg"))
        self.update_background()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.taskbar = TaskBar(self)
        self.taskbar.hide()  # Masque la barre des tâches au démarrage
        self.open_windows = []

        # Créer le formulaire de connexion
        self.init_login_form()

    def resizeEvent(self, event):
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        window_width = self.width()
        window_height = self.height()
        scaled_pixmap = self.background_pixmap.scaled(
            window_width, window_height,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(0, 0, window_width, window_height)

    def init_login_form(self):
        # Créer un widget pour le formulaire de connexion
        self.login_widget = QWidget(self.central_widget)
        self.login_widget.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); padding: 20px; border-radius: 10px;")
        self.login_widget.setGeometry(350, 200, 380, 240)  # Centrer le widget

        layout = QVBoxLayout(self.login_widget)

        self.username_label = QLabel("Nom d'utilisateur:")
        self.password_label = QLabel("Mot de passe:")

        # Styliser les labels avec un fond pour les rendre plus visibles
        self.username_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black; background-color: white; margin-bottom: 5px; padding: 5px; border-radius: 5px;")
        self.password_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black; background-color: white; margin-bottom: 5px; padding: 5px; border-radius: 5px;")

        self.username_input = QLineEdit(self)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Styliser les champs de saisie
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: black;
                background-color: white;
            }
        """)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                color: black;
                background-color: white;
            }
        """)

        self.login_button = QPushButton("Connexion", self)
        self.login_button.clicked.connect(self.handle_login)

        # Styliser le bouton
        self.login_button.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                font-size: 16px;
                background-color: #007BFF;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Vérifier les informations d'identification avec Django
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                self.taskbar.show()  # Affiche la barre des tâches après une connexion réussie
                self.login_widget.hide()  # Masque le widget de connexion
            else:
                QMessageBox.critical(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect.")
        except User.DoesNotExist:
            QMessageBox.critical(self, "Erreur", "Nom d'utilisateur ou mot de passe incorrect.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BureauVirtuel()
    window.show()
    sys.exit(app.exec())
