import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon

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
        """Ouvre une nouvelle instance du navigateur."""
        print("[DEBUG] Ouverture du Navigateur Web.")
        parent_window = self.window()
        if not hasattr(parent_window, "open_windows"):
            parent_window.open_windows = []

        browser = WebBrowser(parent_window)
        parent_window.open_windows.append(browser)
        browser.show()

class WebBrowser(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- En-tête du navigateur ---
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(40)  # ✅ Limite la hauteur de l'en-tête
        self.title_bar.setStyleSheet("background-color: #444444;")

        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(10, 5, 10, 5)

        # 🔹 Remplacement de QPushButton par QLabel pour éviter une hauteur trop grande
        self.title_label = QLabel("🔗 Navigateur Web", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)

        self.layout.addWidget(self.title_bar)

        # --- Vue Web (navigateur intégré) ---
        self.browser = QWebEngineView(self)
        self.browser.setUrl(QUrl("https://www.google.com"))

        self.layout.addWidget(self.browser)