import sys
import os
import django

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "/virtualfs"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "virtualfs.settings")
django.setup()

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QApplication, QFrame, QInputDialog, QMessageBox, QMenu, QInputDialog, QMessageBox
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Explorateur Virtuel")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Fond de la fenêtre
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setStyleSheet("""
            background-color: grey;  
            border-radius: 10px;
            border: 2px solid #b0b0b0;
        """)

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Barre de titre avec bouton Fermer
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

        # (Optionnel) Barre d'actions si vous souhaitez conserver les boutons en plus du clic droit
        self.action_bar = QHBoxLayout()
        self.create_button = QPushButton("Créer dossier")
        self.rename_button = QPushButton("Renommer")
        self.delete_button = QPushButton("Supprimer")
        self.create_button.clicked.connect(self.create_folder)
        self.rename_button.clicked.connect(self.rename_folder)
        self.delete_button.clicked.connect(self.delete_folder)
        self.action_bar.addWidget(self.create_button)
        self.action_bar.addWidget(self.rename_button)
        self.action_bar.addWidget(self.delete_button)
        self.main_layout.addLayout(self.action_bar)

        # Barre de séparation
        self.separator = QFrame(self)
        self.separator.setFixedHeight(2)
        self.separator.setStyleSheet("background-color: #b0b0b0;")
        self.main_layout.addWidget(self.separator)

        # Liste des fichiers et dossiers
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
        # Active le menu contextuel sur clic droit
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_context_menu)
        self.main_layout.addWidget(self.file_list)

        self.refresh_files()
        self.setLayout(self.main_layout)
        self.center_in_bureau()

    def refresh_files(self):
        """ Rafraîchir la liste des fichiers et dossiers depuis la BDD. """
        self.file_list.clear()
        root_folder, _ = Folder.objects.get_or_create(name="Root", parent=None)
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
        """ Centre la fenêtre dans le bureau virtuel. """
        if self.parent():
            parent_geometry = self.parent().geometry()
            window_geometry = self.frameGeometry()
            window_geometry.moveCenter(parent_geometry.center())
            self.move(window_geometry.topLeft())

    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    # --- Fonctions existantes utilisant des dialogs ---

    def create_folder(self):
        """ Créer un nouveau dossier dans le dossier courant. """
        folder_name, ok = QInputDialog.getText(self, "Créer un dossier", "Nom du nouveau dossier :")
        if ok and folder_name:
            Folder.objects.create(name=folder_name, parent=self.current_folder)
            self.refresh_files()

    def rename_folder(self):
        """ Renommer le dossier sélectionné via les boutons. """
        current_item = self.file_list.currentItem()
        if current_item and current_item.text().startswith("📁"):
            old_name = current_item.text().replace("📁 ", "")
            new_name, ok = QInputDialog.getText(self, "Renommer le dossier", "Nouveau nom :", text=old_name)
            if ok and new_name:
                folder = Folder.objects.filter(name=old_name, parent=self.current_folder).first()
                if folder:
                    folder.name = new_name
                    folder.save()
                    self.refresh_files()

    def delete_folder(self):
        """ Supprimer le dossier sélectionné via les boutons après confirmation. """
        current_item = self.file_list.currentItem()
        if current_item and current_item.text().startswith("📁"):
            folder_name = current_item.text().replace("📁 ", "")
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

    # --- Nouvelles méthodes pour le menu contextuel ---

    def open_context_menu(self, position):
        """ Ouvre un menu contextuel au clic droit sur la liste des fichiers/dossiers. """
        item = self.file_list.itemAt(position)
        menu = QMenu()
        # Si l'utilisateur clique sur un dossier, on propose de renommer ou supprimer
        if item and item.text().startswith("📁"):
            rename_action = menu.addAction("Renommer")
            delete_action = menu.addAction("Supprimer")
        # On propose toujours de créer un dossier, que le clic soit sur un élément ou sur le fond
        create_action = menu.addAction("Créer dossier")
        action = menu.exec(self.file_list.mapToGlobal(position))
        if action == create_action:
            self.create_folder()
        elif item and action.text() == "Renommer":
            self.rename_folder_context(item)
        elif item and action.text() == "Supprimer":
            self.delete_folder_context(item)

    def rename_folder_context(self, item):
        """ Renommer un dossier depuis le menu contextuel. """
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
        """ Supprimer un dossier depuis le menu contextuel après confirmation. """
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
