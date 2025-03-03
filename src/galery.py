import sys
import os
import django
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu,
    QScrollArea, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap

# 1. Initialiser Django (idéalement dans un main.py, mais on le met ici pour l'exemple)
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/virtualfs"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virtualfs.settings")
django.setup()

# 2. Importer le modèle
from gallery.models import GalleryImage

class GalleryButton(QPushButton):
    """Bouton pour ouvrir la galerie d'images."""
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/gallery_icon.png")
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.size())
        self.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
        """)
        self.clicked.connect(self.open_explorer)

    def open_explorer(self):
        parent_window = self.window()
        # Si déjà ouvert, on ferme
        if hasattr(parent_window, 'file_explorer_window') and parent_window.file_explorer_window.isVisible():
            parent_window.file_explorer_window.close()
        else:
            # Sinon, on crée et on montre la galerie
            explorer = OnlinePhotoGallery()
            parent_window.file_explorer_window = explorer
            if hasattr(parent_window, 'open_windows'):
                parent_window.open_windows.append(explorer)
            explorer.show()

class OnlinePhotoGallery(QWidget):
    """Fenêtre principale de la galerie d'images (PyQt)."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Galerie d'Images")
        self.setGeometry(200, 200, 800, 600)

        # Layout principal
        self.layout = QVBoxLayout(self)
        # ScrollArea pour afficher un grand nombre d'images
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.grid_layout = QGridLayout(self.scroll_widget)

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.load_images()

    def load_images(self):
        """Charge toutes les GalleryImage depuis la DB et les affiche en grille."""
        images = GalleryImage.objects.all()
        for i, image_obj in enumerate(images):
            label = QLabel()
            label.setFixedSize(150, 150)
            label.setStyleSheet("border: 1px solid #444;")

            pixmap = QPixmap()
            # On charge depuis le chemin local de l'image
            if os.path.exists(image_obj.image.path):
                pixmap.load(image_obj.image.path)

            label.setPixmap(
                pixmap.scaled(
                    150, 150,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )
            # Au clic, on ouvre l'image en plein écran
            label.mousePressEvent = lambda event, path=image_obj.image.path: self.open_fullscreen(path)
            self.grid_layout.addWidget(label, i // 4, i % 4)

    def open_fullscreen(self, local_path):
        """Ouvre l'image en plein écran."""
        self.fullscreen = FullscreenImageViewer(local_path)
        self.fullscreen.show()

class FullscreenImageViewer(QWidget):
    """Affiche l'image en plein écran."""
    def __init__(self, local_path):
        super().__init__()
        self.setWindowTitle("Aperçu")
        self.setGeometry(100, 100, 900, 600)

        layout = QVBoxLayout(self)
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.image_label)

        pixmap = QPixmap()
        pixmap.load(local_path)
        self.image_label.setPixmap(
            pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )
