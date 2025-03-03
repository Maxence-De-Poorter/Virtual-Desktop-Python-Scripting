import os
import sys
import yfinance as yf
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QTimer, QDateTime, Qt
from PyQt6.QtGui import QIcon

class RealTimeGraphButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/bourse_icon.png")
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

        self.clicked.connect(self.open_realTimeGraph)

    def open_realTimeGraph(self):
        """Ouvre ou ferme l'instance du graphique temps réel."""
        parent_window = self.window()

        if hasattr(parent_window, 'real_time_graph') and parent_window.real_time_graph.isVisible():
            parent_window.real_time_graph.close()
        else:
            realTimeGraph = RealTimeGraph(parent_window)
            parent_window.real_time_graph = realTimeGraph
            parent_window.open_windows.append(realTimeGraph)
            realTimeGraph.show()

class RealTimeGraph(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Suppression de la bordure native (frameless)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 500)

        # Style général pour un look moderne et dark
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: #ffffff;
                font-family: Arial;
            }
            QLabel {
                font-size: 14px;
                color: #ffffff;
            }
            QComboBox {
                background-color: #2e1e3e;
                color: white;
                padding: 5px;
                border: 1px solid #555;
                border-radius: 4px;
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
            #footer {
                font-size: 11px;
                color: #aaaaaa;
                margin-top: 8px;
            }
        """)

        # Layout principal sans marges (pour séparer l'entête du contenu)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # --- Barre de titre personnalisée ---
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #444444;")
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(5, 5, 5, 5)

        self.title_label = QLabel("📊 Graphique Temps Réel - Bourse", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)

        self.layout.addWidget(self.title_bar)
        # -------------------------------------

        # Zone de contenu avec marges internes
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        content_layout.setSpacing(10)

        # --- Entête du contenu : sélection de l'actif et bouton démarrer ---
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📊 Actif suivi :"))

        self.symbol_box = QComboBox()
        self.symbol_box.addItems(["TSLA", "AAPL", "BTC-USD", "ETH-USD"])
        header_layout.addWidget(self.symbol_box)

        self.start_button = QPushButton("▶️ Démarrer")
        self.start_button.clicked.connect(self.start_update)
        header_layout.addWidget(self.start_button)

        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        content_layout.addLayout(header_layout)
        # -------------------------------------

        # --- Zone graphique ---
        self.plot_widget = pg.PlotWidget()
        content_layout.addWidget(self.plot_widget)

        self.plot_widget.setBackground("#1e1e2f")
        self.plot_widget.setLabel('left', 'Prix ($)', color='#ffffff', size='10pt')
        self.plot_widget.setLabel('bottom', 'Temps', color='#ffffff', size='10pt')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        # -----------------------

        # --- Footer avec la dernière mise à jour ---
        self.footer = QLabel("")
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        content_layout.addWidget(self.footer)
        # -----------------------------------------------

        self.layout.addWidget(content_widget)

        # Timer et initialisation des données
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.data_x = []
        self.data_y = []
        self.curve = self.plot_widget.plot([], [], pen=pg.mkPen('#00FFCC', width=3))

        # Variables pour le déplacement de la fenêtre
        self._drag_start_position = None
        self._drag_offset = None

    def start_update(self):
        self.data_x = []
        self.data_y = []
        self.curve.setData([], [])
        self.timer.start(2000)  # Mise à jour toutes les 2 secondes

    def update_data(self):
        try:
            symbol = self.symbol_box.currentText()
            data = yf.download(symbol, period="1d", interval="1m")
            if not data.empty:
                last_price = data["Close"].iloc[-1]
                self.data_x.append(len(self.data_x) + 1)
                self.data_y.append(last_price)
                if len(self.data_x) > 1 and len(self.data_y) > 1:
                    self.curve.setData(np.array(self.data_x).flatten(), np.array(self.data_y).flatten())
                self.footer.setText(f"Dernière mise à jour : {QDateTime.currentDateTime().toString('HH:mm:ss')}")
        except Exception as e:
            print(f"Erreur lors de la récupération ou mise à jour des données : {e}")

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

    def closeEvent(self, event):
        """Arrête la mise à jour des données et ferme la fenêtre."""
        self.timer.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealTimeGraph()
    window.show()
    sys.exit(app.exec())
