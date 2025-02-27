import sys
import os
import django

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/virtualfs"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virtualfs.settings")
django.setup()

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout,
    QApplication, QFrame, QMenu, QInputDialog, QMessageBox
)
from PyQt6.QtGui import QIcon
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)

        # Fond de la fenêtre avec style amélioré
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setStyleSheet("""
            background-color: #2e2e2e;  
            border-radius: 10px;
            border: 2px solid #4a4a4a;
        """)

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(5)

        # Barre de titre avec bouton Fermer
        self.title_bar = QHBoxLayout()
        self.title_bar.setContentsMargins(10, 5, 10, 5)
        self.title_label = QLabel("Explorateur de fichiers", self)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: white;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.close_button = QPushButton("❌", self)
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

        # Séparateur sous le titre
        self.separator = QFrame(self)
        self.separator.setFixedHeight(2)
        self.separator.setStyleSheet("background-color: #4a4a4a;")
        self.main_layout.addWidget(self.separator)

        # Liste des fichiers et dossiers (zone centrale)
        self.file_list = QListWidget(self)
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #2e2e2e;
                border: 1px solid #c0c0c0;
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
            }
        """)
        self.file_list.itemDoubleClicked.connect(self.navigate)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_context_menu)
        self.main_layout.addWidget(self.file_list)

        # Fil d’Ariane (breadcrumb) placé en bas sans encadré, texte en blanc
        self.breadcrumb_frame = QFrame(self)
        self.breadcrumb_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        self.breadcrumb_layout = QHBoxLayout(self.breadcrumb_frame)
        self.breadcrumb_layout.setContentsMargins(5, 5, 5, 5)
        self.breadcrumb_layout.setSpacing(5)
        self.main_layout.addWidget(self.breadcrumb_frame)

        # Initialisation du dossier courant (Root)
        self.current_folder, _ = Folder.objects.get_or_create(name="Root", parent=None)
        self.refresh_files()

        self.setLayout(self.main_layout)
        self.center_in_bureau()

    def update_breadcrumb(self):
        """Reconstruit le fil d’Ariane cliquable en bas, avec le texte 'Chemin:' et en blanc."""
        # Vider le layout actuel
        while self.breadcrumb_layout.count():
            item = self.breadcrumb_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Ajout du préfixe "Chemin:" en blanc
        chemin_label = QLabel("Chemin:", self)
        chemin_label.setStyleSheet("color: white; font-size: 14px;")
        self.breadcrumb_layout.addWidget(chemin_label)

        # Construction de la liste de dossiers de Root jusqu'au dossier courant
        path_list = []
        folder = self.current_folder
        while folder:
            path_list.insert(0, folder)
            folder = folder.parent

        # Pour chaque dossier, ajouter un bouton cliquable en blanc
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

    def refresh_files(self):
        """Rafraîchir la liste des fichiers et dossiers depuis la BDD et mettre à jour le breadcrumb."""
        self.file_list.clear()
        # Si on n'est pas dans Root, on ajoute en première position un élément spécial "dossier parent"
        if self.current_folder.parent is not None:
            self.file_list.addItem("📁 ..")
        folders = Folder.objects.filter(parent=self.current_folder)
        for folder in folders:
            self.file_list.addItem(f"📁 {folder.name}")
        files = File.objects.filter(folder=self.current_folder)
        for file in files:
            self.file_list.addItem(f"📄 {file.name}")
        self.update_breadcrumb()

    def navigate(self, item):
        """Gérer la navigation dans les dossiers via double-clic."""
        selected = item.text()
        # Si l'utilisateur clique sur l'élément spécial "dossier parent", revenir en arrière
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
        """Retourne au dossier parent."""
        if self.current_folder.parent is not None:
            self.current_folder = self.current_folder.parent
            self.refresh_files()

    def center_in_bureau(self):
        """Centre la fenêtre dans le bureau virtuel."""
        if self.parent():
            parent_geometry = self.parent().geometry()
            window_geometry = self.frameGeometry()
            window_geometry.moveCenter(parent_geometry.center())
            self.move(window_geometry.topLeft())

    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    # --- Fonctions pour le menu contextuel ---

    def create_folder(self):
        """Créer un nouveau dossier dans le dossier courant."""
        folder_name, ok = QInputDialog.getText(self, "Créer un dossier", "Nom du nouveau dossier :")
        if ok and folder_name:
            Folder.objects.create(name=folder_name, parent=self.current_folder)
            self.refresh_files()

    def rename_folder_context(self, item):
        """Renommer un dossier depuis le menu contextuel."""
        if item and item.text().startswith("📁"):
            old_name = item.text().replace("📁 ", "")
            new_name, ok = QInputDialog.getText(self, "Renommer le dossier", "Nouveau nom :", text=old_name)
            if ok and new_name:
                folder = Folder.objects.filter(name=old_name, parent=self.current_folder).first()
                if folder:
                    folder.name = new_name
                    folder.save()
                    self.refresh_files()

    def delete_folder_context(self, item):
        """Supprimer un dossier depuis le menu contextuel après confirmation."""
        if item and item.text().startswith("📁"):
            folder_name = item.text().replace("📁 ", "")
            reply = QMessageBox.question(
                self,
                "Confirmer la suppression",
                f"Voulez-vous vraiment supprimer le dossier '{folder_name}' ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                folder = Folder.objects.filter(name=folder_name, parent=self.current_folder).first()
                if folder:
                    folder.delete()
                    self.refresh_files()

    def rename_file_context(self, item):
        """Renommer un fichier depuis le menu contextuel."""
        if item and item.text().startswith("📄"):
            old_name = item.text().replace("📄 ", "")
            new_name, ok = QInputDialog.getText(self, "Renommer le fichier", "Nouveau nom :", text=old_name)
            if ok and new_name:
                file_obj = File.objects.filter(name=old_name, folder=self.current_folder).first()
                if file_obj:
                    file_obj.name = new_name
                    file_obj.save()
                    self.refresh_files()

    def delete_file_context(self, item):
        """Supprimer un fichier depuis le menu contextuel après confirmation."""
        if item and item.text().startswith("📄"):
            file_name = item.text().replace("📄 ", "")
            reply = QMessageBox.question(
                self,
                "Confirmer la suppression",
                f"Voulez-vous vraiment supprimer le fichier '{file_name}' ?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                file_obj = File.objects.filter(name=file_name, folder=self.current_folder).first()
                if file_obj:
                    file_obj.delete()
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
        if action is None:
            return
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    explorer = FileExplorer()
    explorer.show()
    sys.exit(app.exec())
