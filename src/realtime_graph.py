import sys
import yfinance as yf
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QComboBox, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import QTimer, QDateTime, Qt

class RealTimeGraphWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📊 Graphique Temps Réel - Bourse")
        self.resize(800, 500)

        # 🎨 Style CSS pour un look moderne et dark
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
                background-color: #2e2e3e;
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

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # 🏷️ Titre et combo box pour choisir l’actif
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("📊 Actif suivi :"))

        self.symbol_box = QComboBox()
        self.symbol_box.addItems(["TSLA", "AAPL", "BTC-USD", "ETH-USD"])
        header_layout.addWidget(self.symbol_box)

        self.start_button = QPushButton("▶️ Démarrer")
        self.start_button.clicked.connect(self.start_update)
        header_layout.addWidget(self.start_button)

        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.layout.addLayout(header_layout)

        # 📈 Zone graphique
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        self.plot_widget.setBackground("#1e1e2f")
        self.plot_widget.setLabel('left', 'Prix ($)', color='#ffffff', size='10pt')
        self.plot_widget.setLabel('bottom', 'Temps', color='#ffffff', size='10pt')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)

        # Données et courbe
        self.data_x = []
        self.data_y = []
        self.curve = self.plot_widget.plot([], [], pen=pg.mkPen('#00FFCC', width=3))

        # 📅 Footer avec dernière mise à jour
        self.footer = QLabel("")
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.layout.addWidget(self.footer)

    def start_update(self):
        """ Démarre la mise à jour en temps réel. """
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RealTimeGraphWindow()
    window.show()
    sys.exit(app.exec())
