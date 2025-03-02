import os
import sys
import feedparser
import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QPushButton, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class FluxRSSButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/fluxRSS_icon.png")
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

        self.clicked.connect(self.open_fluxRSS)

    def open_fluxRSS(self):
        """Ouvre une nouvelle instance de l'explorateur de fichiers."""
        print("[DEBUG] Ouverture Explorateur Virtuel.")
        parent_window = self.window()
        if not hasattr(parent_window, "open_windows"):
            parent_window.open_windows = []

        fluxRSS = FluxRSS(parent_window)
        parent_window.open_windows.append(fluxRSS)
        fluxRSS.show()

import os
import sys
import feedparser
import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QPushButton, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

class FluxRSS(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Suppression de la bordure native (frameless)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)

        # Layout principal sans marges pour occuper tout l'espace
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- Barre de titre personnalisée ---
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #444444;")
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(5, 5, 5, 5)

        self.title_label = QLabel("📰 Flux RSS - Actualités", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet(
            "border: none; background: transparent; color: white; font-size: 16px;"
        )
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)

        self.layout.addWidget(self.title_bar)
        # -------------------------------------

        # Zone de contenu (les marges internes sont définies ici)
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # --- Zone d'affichage des flux RSS ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)  # Espace entre les articles
        self.scroll_area.setWidget(self.scroll_content)
        content_layout.addWidget(self.scroll_area)
        # ----------------------------------------

        # Bouton de rafraîchissement
        self.refresh_button = QPushButton("Rafraîchir les flux")
        content_layout.addWidget(self.refresh_button)
        self.refresh_button.clicked.connect(self.charger_flux)

        self.layout.addWidget(content_widget)

        # Liste des flux RSS
        self.liste_flux = [
            "https://www.lemonde.fr/rss/une.xml",
            "http://feeds.bbci.co.uk/news/rss.xml"
        ]

        self.charger_flux()

    def charger_flux(self):
        # Nettoyer le contenu précédent
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Rechargement des flux
        for flux in self.liste_flux:
            feed = feedparser.parse(flux)
            for entry in feed.entries:
                self.ajouter_carte(entry)

    def ajouter_carte(self, entry):
        titre = entry.title
        lien = entry.link
        description = entry.get('summary', 'Pas de description disponible.')

        # Création de la "carte" pour afficher l'article
        carte = QFrame()
        carte_layout = QVBoxLayout(carte)
        carte_layout.setContentsMargins(10, 10, 10, 10)

        titre_label = QLabel(titre)
        titre_label.setWordWrap(True)
        titre_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        description_label = QLabel(description)
        description_label.setWordWrap(True)
        description_label.setStyleSheet("font-size: 13px; color: #cccccc;")

        bouton_lire = QPushButton("Lire l’article")
        bouton_lire.clicked.connect(lambda checked=False, url=lien: self.ouvrir_lien(url))

        carte_layout.addWidget(titre_label)
        carte_layout.addWidget(description_label)

        bouton_layout = QHBoxLayout()
        bouton_layout.addStretch()
        bouton_layout.addWidget(bouton_lire)
        carte_layout.addLayout(bouton_layout)

        # Ajout de la carte et d'un séparateur dans le layout principal des articles
        self.scroll_layout.addWidget(carte)

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #444444;")
        self.scroll_layout.addWidget(separator)

    def ouvrir_lien(self, url):
        webbrowser.open(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FluxRSS()
    window.show()
    sys.exit(app.exec())
