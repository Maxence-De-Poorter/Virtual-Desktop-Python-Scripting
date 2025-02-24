import sys
import os
import django

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/virtualfs"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virtualfs.settings")
django.setup()

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QApplication, QFrame
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt
from files.models import Folder, File

class FileExplorerButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/explorer_icon.png")
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.size())

        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)

        self.clicked.connect(self.open_explorer)

    def open_explorer(self):
        """Ouvre une nouvelle instance de l'explorateur de fichiers virtuels."""
        print("[DEBUG] Ouverture Explorateur Virtuel.")
        parent_window = self.window()

        if not hasattr(parent_window, "open_windows"):
            parent_window.open_windows = []

        explorer = FileExplorer(parent_window)
        parent_window.open_windows.append(explorer)
        explorer.show()

class FileExplorer(QWidget):
    """ Explorateur de fichiers avec un fond unique et bouton de fermeture en haut à droite. """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Explorateur Virtuel")
        self.setFixedSize(700, 500)  # Taille fixe
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Supprime les bordures

        # 📌 Ajout du **fond unique** en QLabel pour une apparence homogène
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setStyleSheet("""
            background-color: grey;  
            border-radius: 10px;
            border: 2px solid #b0b0b0;
        """)

        # 📌 Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # 🔹 **Barre de titre avec bouton Fermer**
        self.title_bar = QHBoxLayout()
        self.title_bar.setContentsMargins(10, 5, 10, 5)

        self.title_label = QLabel("📁 Explorateur de fichiers", self)

        self.title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: white;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        self.close_button = QPushButton("❌")
        self.close_button.setFixedSize(40, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                color: red;
            }
        """)
        self.close_button.clicked.connect(self.close)

        self.title_bar.addWidget(self.title_label)
        self.title_bar.addStretch()
        self.title_bar.addWidget(self.close_button)

        self.main_layout.addLayout(self.title_bar)

        # 🟥 **Ajout d'une barre de séparation**
        self.separator = QFrame(self)
        self.separator.setFixedHeight(2)  # Hauteur fine pour ne pas prendre trop de place
        self.separator.setStyleSheet("background-color: #b0b0b0;")  # Couleur de la séparation

        self.main_layout.addWidget(self.separator)  # Ajoute la séparation sous le titre

        # 🔹 **Liste des fichiers et dossiers**
        self.file_list = QListWidget(self)
        self.file_list.setStyleSheet("""
            QListWidget {
            
                background: grey;
                border: none;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background: #0078D7;
                color: white;
                border-radius: 5px;
            }
        """)
        self.file_list.itemDoubleClicked.connect(self.navigate)

        self.main_layout.addWidget(self.file_list)

        self.refresh_files()
        self.setLayout(self.main_layout)

        # 📌 Centre la fenêtre dans le bureau virtuel
        self.center_in_bureau()

    def refresh_files(self):
        """ Rafraîchir la liste des fichiers et dossiers depuis la BDD. """
        self.file_list.clear()

        root_folder, created = Folder.objects.get_or_create(name="Root", parent=None)
        self.current_folder = root_folder

        folders = Folder.objects.filter(parent=self.current_folder)
        for folder in folders:
            self.file_list.addItem(f"📁 {folder.name}")

        files = File.objects.filter(folder=self.current_folder)
        for file in files:
            self.file_list.addItem(f"📄 {file.name}")

    def navigate(self, item):
        """ Gérer la navigation dans les dossiers Django. """
        selected = item.text().replace("📁 ", "").replace("📄 ", "")

        folder = Folder.objects.filter(name=selected, parent=self.current_folder).first()
        if folder:
            self.current_folder = folder

        self.refresh_files()

    def center_in_bureau(self):
        """ 📌 Centre la fenêtre **dans le bureau virtuel** au lieu de l'écran principal. """
        if self.parent():
            parent_geometry = self.parent().geometry()  # Prendre la géométrie du bureau
            window_geometry = self.frameGeometry()
            window_geometry.moveCenter(parent_geometry.center())
            self.move(window_geometry.topLeft())

    def resizeEvent(self, event):
        """ 📌 Ajuste le **fond QLabel** pour qu'il couvre toute la fenêtre. """
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)