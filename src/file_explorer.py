import sys
import os
import django
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QFrame, QMenu, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Configuration Django pour la gestion des fichiers
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/virtualfs"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virtualfs.settings")
django.setup()

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
        """Ouvre ou ferme l'instance de l'explorateur de fichiers."""
        parent_window = self.window()

        if hasattr(parent_window, 'file_explorer_window') and parent_window.file_explorer_window.isVisible():
            parent_window.file_explorer_window.close()
        else:
            explorer = FileExplorer(parent_window)
            parent_window.file_explorer_window = explorer
            parent_window.open_windows.append(explorer)
            explorer.show()

class FileExplorer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Supprime la bordure native et définit la taille de la fenêtre
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)

        # Layout principal sans marges pour occuper tout l'espace
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- En-tête personnalisé ---
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #444444;")
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(5, 5, 5, 5)

        self.title_label = QLabel("Explorateur de fichiers", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)

        self.layout.addWidget(self.title_bar)

        # --- Zone de fichiers (affichage et interaction) ---
        self.file_list = QListWidget(self)
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #2e2e2e;
                border: none;
                padding: 10px;
                font-size: 14px;
                color: white;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background-color: #0078D7;
                color: white;
                border-radius: 5px;
            }
        """)
        self.file_list.itemDoubleClicked.connect(self.navigate)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_context_menu)
        self.layout.addWidget(self.file_list)

        # --- Fil d'Ariane (breadcrumb) ---
        self.breadcrumb_layout = QHBoxLayout()
        self.breadcrumb_layout.setContentsMargins(5, 5, 5, 5)
        self.breadcrumb_layout.setSpacing(5)
        self.layout.addLayout(self.breadcrumb_layout)

        # Initialisation du dossier courant (Root)
        self.current_folder, _ = Folder.objects.get_or_create(name="Root", parent=None)
        self.refresh_files()

        # Variables pour le déplacement de la fenêtre
        self._drag_start_position = None
        self._drag_offset = None

    def refresh_files(self):
        """Rafraîchir la liste des fichiers et dossiers et mettre à jour le breadcrumb."""
        self.file_list.clear()
        if self.current_folder.parent is not None:
            self.file_list.addItem("📁 ..")
        folders = Folder.objects.filter(parent=self.current_folder)
        for folder in folders:
            self.file_list.addItem(f"📁 {folder.name}")
        files = File.objects.filter(folder=self.current_folder)
        for file in files:
            self.file_list.addItem(f"📄 {file.name}")
        self.update_breadcrumb()

    def update_breadcrumb(self):
        """Met à jour le fil d'Ariane en bas."""
        while self.breadcrumb_layout.count():
            item = self.breadcrumb_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        chemin_label = QLabel("Chemin:", self)
        chemin_label.setStyleSheet("color: white; font-size: 14px;")
        self.breadcrumb_layout.addWidget(chemin_label)

        path_list = []
        folder = self.current_folder
        while folder:
            path_list.insert(0, folder)
            folder = folder.parent

        for index, folder in enumerate(path_list):
            btn = QPushButton(folder.name, self)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: white;
                    font-size: 14px;
                    border: none;
                }
                QPushButton:hover {
                    text-decoration: underline;
                }
            """)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, f=folder: self.navigate_to_folder(f))
            self.breadcrumb_layout.addWidget(btn)
            if index < len(path_list) - 1:
                sep = QLabel(">", self)
                sep.setStyleSheet("color: white; font-size: 14px;")
                self.breadcrumb_layout.addWidget(sep)

        self.breadcrumb_layout.addStretch()

    def navigate(self, item):
        """Naviguer dans les dossiers."""
        selected = item.text()
        if selected == "📁 ..":
            self.go_back()
            return
        selected = selected.replace("📁 ", "").replace("📄 ", "")
        folder = Folder.objects.filter(name=selected, parent=self.current_folder).first()
        if folder:
            self.current_folder = folder
            self.refresh_files()

    def navigate_to_folder(self, folder):
        """Naviguer directement vers un dossier via le breadcrumb."""
        self.current_folder = folder
        self.refresh_files()

    def go_back(self):
        """Retour au dossier parent."""
        if self.current_folder.parent is not None:
            self.current_folder = self.current_folder.parent
            self.refresh_files()

    def open_context_menu(self, position):
        """Ouvre un menu contextuel au clic droit sur la liste des fichiers/dossiers."""
        item = self.file_list.itemAt(position)
        menu = QMenu()
        create_action = menu.addAction("Créer dossier")
        if item:
            if item.text().startswith("📁"):
                rename_action = menu.addAction("Renommer dossier")
                delete_action = menu.addAction("Supprimer dossier")
            elif item.text().startswith("📄"):
                rename_action = menu.addAction("Renommer fichier")
                delete_action = menu.addAction("Supprimer fichier")
        action = menu.exec(self.file_list.mapToGlobal(position))
        if action == create_action:
            self.create_folder()
        elif item:
            if item.text().startswith("📁"):
                if action == rename_action:
                    self.rename_folder_context(item)
                elif action == delete_action:
                    self.delete_folder_context(item)
            elif item.text().startswith("📄"):
                if action == rename_action:
                    self.rename_file_context(item)
                elif action == delete_action:
                    self.delete_file_context(item)

    def mousePressEvent(self, event):
        """Gère l'événement de pression de la souris pour déplacer la fenêtre."""
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self._drag_start_position = event.globalPosition().toPoint()
            self._drag_offset = self.pos() - self._drag_start_position

    def mouseMoveEvent(self, event):
        """Gère l'événement de mouvement de la souris pour déplacer la fenêtre."""
        if self._drag_start_position and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() + self._drag_offset
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        """Gère l'événement de relâchement de la souris."""
        self._drag_start_position = None
        self._drag_offset = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    explorer = FileExplorer()
    explorer.show()
    sys.exit(app.exec())
