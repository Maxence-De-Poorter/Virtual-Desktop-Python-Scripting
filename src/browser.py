import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QInputDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QPropertyAnimation, QRect
from PyQt6.QtGui import QIcon

from files.models import Bookmark  # Import du modèle Django

class BrowserButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/browser_icon.png")
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

        self.clicked.connect(self.open_browser)

    def open_browser(self):
        """Ouvre ou ferme l'instance du navigateur."""
        parent_window = self.window()

        if hasattr(parent_window, 'web_browser_window') and parent_window.web_browser_window.isVisible():
            parent_window.web_browser_window.close()
        else:
            web_browser = WebBrowser(parent_window)
            parent_window.web_browser_window = web_browser
            parent_window.open_windows.append(web_browser)
            web_browser.show()

class WebBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- Barre de navigation ---
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(40)
        self.title_bar.setStyleSheet("background-color: #444444;")
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(10, 5, 10, 5)

        self.title_label = QLabel("🔗 Navigateur Web", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")
        self.title_layout.addWidget(self.title_label)

        self.menu_button = QPushButton("📂", self.title_bar)
        self.menu_button.setFixedSize(30, 30)
        self.menu_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.menu_button.clicked.connect(self.toggle_bookmarks)
        self.title_layout.addWidget(self.menu_button)

        self.add_bookmark_button = QPushButton("⭐", self.title_bar)
        self.add_bookmark_button.setFixedSize(30, 30)
        self.add_bookmark_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.add_bookmark_button.clicked.connect(self.add_bookmark)
        self.title_layout.addWidget(self.add_bookmark_button)

        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)

        self.layout.addWidget(self.title_bar)

        # --- Vue Web (Navigateur intégré) ---
        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl("https://www.google.com"))
        self.layout.addWidget(self.browser)

        # --- Menu latéral pour les signets (caché par défaut) ---
        self.bookmark_panel = QWidget(self)
        self.bookmark_panel.setFixedWidth(250)
        self.bookmark_panel.setStyleSheet("background-color: #2e2e2e; border-right: 2px solid #555555;")

        self.bookmark_layout = QVBoxLayout(self.bookmark_panel)
        self.bookmark_layout.setContentsMargins(10, 10, 10, 10)

        self.bookmark_list = QListWidget(self.bookmark_panel)
        self.bookmark_list.setStyleSheet("""
            QListWidget {
                background-color: #2e2e2e;
                border: none;
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
        self.bookmark_list.itemClicked.connect(self.load_bookmark)
        self.bookmark_layout.addWidget(self.bookmark_list)

        self.bookmark_panel.setLayout(self.bookmark_layout)

        # --- Animation pour le menu latéral ---
        self.bookmark_panel.setGeometry(-250, 40, 250, 560)  # Caché en dehors de l'écran
        self.animation = QPropertyAnimation(self.bookmark_panel, b"geometry")
        self.is_menu_visible = False  # Menu fermé au démarrage

        self.load_bookmarks()

        # Variables pour le déplacement de la fenêtre
        self._drag_start_position = None
        self._drag_offset = None

    def add_bookmark(self):
        """Ajoute l'URL actuelle aux signets."""
        url = self.browser.url().toString()
        title, ok = QInputDialog.getText(self, "Ajouter un signet", "Nom du signet:")
        if ok and title:
            Bookmark.objects.create(title=title, url=url)
            self.load_bookmarks()

    def load_bookmarks(self):
        """Charge tous les signets enregistrés."""
        self.bookmark_list.clear()
        for bookmark in Bookmark.objects.all():
            self.bookmark_list.addItem(f"{bookmark.title} ({bookmark.url})")

    def load_bookmark(self, item):
        """Charge un signet sélectionné."""
        url = item.text().split(" (")[1][:-1]
        self.browser.setUrl(QUrl(url))

    def toggle_bookmarks(self):
        """Affiche ou cache le menu latéral avec une animation."""
        if self.is_menu_visible:
            self.animation.setDuration(300)
            self.animation.setStartValue(QRect(0, 40, 250, 560))
            self.animation.setEndValue(QRect(-250, 40, 250, 560))
        else:
            self.animation.setDuration(300)
            self.animation.setStartValue(QRect(-250, 40, 250, 560))
            self.animation.setEndValue(QRect(0, 40, 250, 560))

        self.animation.start()
        self.is_menu_visible = not self.is_menu_visible

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
    window = WebBrowser()
    window.show()
    sys.exit(app.exec())
