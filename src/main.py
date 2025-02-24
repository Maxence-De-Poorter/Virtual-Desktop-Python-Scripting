import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.taskbar import TaskBar

class BureauVirtuel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bureau Virtuel")
        self.setGeometry(100, 100, 1080, 720)

        self.setMinimumSize(1080, 720)  # 📌 Définit la taille minimale de la fenêtre


        # 📌 Ajouter un QLabel pour afficher le fond d'écran
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        # 📌 Charger l'image de fond
        self.background_pixmap = QPixmap(os.path.join("assets", "background.jpg"))
        self.update_background()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.taskbar = TaskBar(self)
        self.open_windows = []  # 📌 Stocker les fenêtres ouvertes

    def resizeEvent(self, event):
        """ Met à jour le fond et la barre des tâches lors du redimensionnement. """
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        """ Ajuste l’image de fond à la taille de la fenêtre. """
        window_width = self.width()
        window_height = self.height()

        scaled_pixmap = self.background_pixmap.scaled(
            window_width, window_height,  # 📌 Largeur et hauteur en INT
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # 📌 Garde les proportions et remplit l'écran
            Qt.TransformationMode.SmoothTransformation  # 📌 Transformation fluide pour une meilleure qualité
        )

        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(0, 0, window_width, window_height)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BureauVirtuel()
    window.show()
    sys.exit(app.exec())
