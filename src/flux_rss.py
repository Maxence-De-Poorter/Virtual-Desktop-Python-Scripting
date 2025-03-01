import sys
import feedparser
import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QPushButton, QHBoxLayout, QApplication
)
from PyQt6.QtCore import Qt


class FluxRSSWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📰 Flux RSS - Actualités")
        self.resize(800, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 14px;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QScrollArea {
                background: #1e1e1e;
                border: none;
            }
            QFrame {
                background-color: #2e2e2e;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        self.liste_flux = [
            "https://www.lemonde.fr/rss/une.xml",
            "http://feeds.bbci.co.uk/news/rss.xml"
        ]

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.scroll_area.setWidget(self.scroll_content)

        self.layout.addWidget(QLabel("📰 Actualités RSS"))
        self.layout.addWidget(self.scroll_area)

        self.refresh_button = QPushButton("Rafraîchir les flux")
        self.layout.addWidget(self.refresh_button)

        self.refresh_button.clicked.connect(self.charger_flux)

        self.charger_flux()

    def charger_flux(self):
        # Nettoyage
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Rechargement des flux
        self.actualites = []
        for flux in self.liste_flux:
            feed = feedparser.parse(flux)
            for entry in feed.entries:
                self.ajouter_carte(entry)

    def ajouter_carte(self, entry):
        titre = entry.title
        lien = entry.link
        description = entry.get('summary', 'Pas de description disponible.')

        self.actualites.append((titre, lien))

        # Carte contenant le titre + description + bouton
        carte = QFrame()
        carte_layout = QVBoxLayout(carte)

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

        self.scroll_layout.addWidget(carte)

    def ouvrir_lien(self, url):
        webbrowser.open(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FluxRSSWindow()
    window.show()
    sys.exit(app.exec())
