import sys
import os
import django
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QMenu,
    QInputDialog, QMessageBox, QFileDialog, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QImage
import fitz  # PyMuPDF pour lire les PDFs

# --- Configuration Django (à externaliser dans un setup global si possible) ---
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
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
        """)
        self.clicked.connect(self.open_explorer)

    def open_explorer(self):
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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)

        self.main_layout = QHBoxLayout(self)

        # --- Partie gauche : liste de fichiers
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self._init_title_bar()
        self._init_file_list()
        self._init_breadcrumb()

        self.current_folder, _ = Folder.objects.get_or_create(name="Root", parent=None)
        self.refresh_files()

        self._drag_start_position = None
        self._drag_offset = None

        # --- Partie droite : aperçu
        self.preview = QLabel(self)
        self.preview.setStyleSheet("background-color: #333; color: white; padding: 10px;")
        self.preview.setWordWrap(True)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.preview.setText("Sélectionnez un fichier pour voir un aperçu.")

        self.main_layout.addLayout(self.layout, 2)
        self.main_layout.addWidget(self.preview, 1)

    def _init_title_bar(self):
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #444444;")
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(5, 5, 5, 5)

        self.title_label = QLabel("Explorateur de fichiers", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")

        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.close_button.clicked.connect(self.close)

        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()
        self.title_layout.addWidget(self.close_button)

        self.layout.addWidget(self.title_bar)

    def _init_file_list(self):
        self.file_list = QListWidget(self)
        self.file_list.setStyleSheet("""
            QListWidget { background-color: #2e2e2e; border: none; padding: 10px; font-size: 14px; color: white; }
            QListWidget::item { padding: 8px; }
            QListWidget::item:selected { background-color: #0078D7; color: white; border-radius: 5px; }
        """)
        self.file_list.itemClicked.connect(self.preview_file)
        self.file_list.itemDoubleClicked.connect(self.navigate)
        self.file_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_list.customContextMenuRequested.connect(self.open_context_menu)

        self.layout.addWidget(self.file_list)

    def _init_breadcrumb(self):
        self.breadcrumb_layout = QHBoxLayout()
        self.layout.addLayout(self.breadcrumb_layout)

    def refresh_files(self):
        self.file_list.clear()
        if self.current_folder.parent:
            self.file_list.addItem("📁 ..")

        for folder in Folder.objects.filter(parent=self.current_folder):
            self.file_list.addItem(f"📁 {folder.name}")

        for file in File.objects.filter(folder=self.current_folder):
            self.file_list.addItem(f"📄 {file.name}")

        self.update_breadcrumb()

    def update_breadcrumb(self):
        while self.breadcrumb_layout.count():
            item = self.breadcrumb_layout.takeAt(0)
            if widget := item.widget():
                widget.deleteLater()

        path = []
        folder = self.current_folder
        while folder:
            path.insert(0, folder)
            folder = folder.parent

        for index, folder in enumerate(path):
            btn = QPushButton(folder.name)
            btn.setStyleSheet("background: transparent; color: white; border: none;")
            btn.clicked.connect(lambda checked, f=folder: self.navigate_to_folder(f))
            self.breadcrumb_layout.addWidget(btn)

            if index < len(path) - 1:
                self.breadcrumb_layout.addWidget(QLabel(">"))

        self.breadcrumb_layout.addStretch()

    def navigate(self, item):
        name = item.text()[2:].strip()
        if item.text() == "📁 ..":
            self.go_back()
            return

        if folder := Folder.objects.filter(name=name, parent=self.current_folder).first():
            self.current_folder = folder
            self.refresh_files()

    def navigate_to_folder(self, folder):
        self.current_folder = folder
        self.refresh_files()

    def go_back(self):
        if self.current_folder.parent:
            self.current_folder = self.current_folder.parent
            self.refresh_files()

    def open_context_menu(self, position):
        menu = QMenu()
        menu.addAction("Créer dossier", self.create_folder)
        menu.addAction("Importer fichier", self.upload_file)

        item = self.file_list.itemAt(position)
        if item and item.text().startswith("📁"):
            menu.addAction("Renommer dossier", lambda: self.rename_item(item, Folder))
            menu.addAction("Supprimer dossier", lambda: self.delete_item(item, Folder))

        if item and item.text().startswith("📄"):
            menu.addAction("Renommer fichier", lambda: self.rename_item(item, File))
            menu.addAction("Supprimer fichier", lambda: self.delete_item(item, File))

        menu.exec(self.file_list.mapToGlobal(position))

    def create_folder(self):
        name, ok = QInputDialog.getText(self, "Nouveau dossier", "Nom du dossier:")
        if ok and name:
            Folder.objects.create(name=name, parent=self.current_folder)
            self.refresh_files()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Importer fichier", "", "All Files (*)")
        if file_path:
            name = os.path.basename(file_path)
            with open(file_path, 'rb') as f:
                file = File(name=name, folder=self.current_folder)
                file.file.save(name, f, save=True)
            self.refresh_files()

    def rename_item(self, item, model):
        old_name = item.text()[2:].strip()
        new_name, ok = QInputDialog.getText(self, "Renommer", "Nouveau nom:", text=old_name)
        if ok:
            model.objects.filter(name=old_name, folder=self.current_folder).update(name=new_name)
            self.refresh_files()

    def delete_item(self, item, model):
        model.objects.filter(name=item.text()[2:].strip(), folder=self.current_folder).delete()
        self.refresh_files()

    def preview_file(self, item):
        name = item.text()[2:].strip()
        file = File.objects.filter(name=name, folder=self.current_folder).first()
        if file:
            if file.file.name.endswith(".txt") or file.file.name.endswith(".md"):
                self.preview.setText(open(file.file.path).read())
            elif file.file.name.endswith(".pdf"):
                self.preview_pdf(file.file.path)

    def preview_pdf(self, path):
        page = fitz.open(path)[0].get_pixmap()
        img = QImage(page.samples, page.width, page.height, page.stride, QImage.Format.Format_RGBA8888)
        self.preview.setPixmap(QPixmap.fromImage(img).scaledToWidth(300))
