from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer, QTime
import sys

class BureauVirtuel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bureau Virtuel")
        self.setGeometry(100, 100, 800, 600)
        
        # Création du widget principal (le bureau)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Ajouter la barre des tâches
        self.init_taskbar()

    def init_taskbar(self):
        """Crée et ajoute une barre des tâches en bas de la fenêtre."""
        self.taskbar = QWidget(self)
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        self.taskbar.setStyleSheet("background-color: #222; color: white;")

        # Layout de la barre des tâches
        layout = QHBoxLayout(self.taskbar)
        layout.setContentsMargins(5, 5, 10, 5)  # Ajustement des marges
        layout.setSpacing(10)  # Espacement entre les éléments

        # Bouton Démarrer en carré
        self.start_button = QPushButton(" ")
        self.start_button.setFixedSize(40, 40)  # Bouton carré 40x40px
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7; /* Bleu Windows */
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #005A9E; /* Bleu foncé au survol */
            }
        """)
        layout.addWidget(self.start_button)

        # Horloge
        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Timer pour mettre à jour l'heure
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Mise à jour toutes les secondes
        self.update_time()  # Afficher l'heure dès le début

        layout.addWidget(self.clock_label)
        layout.addStretch()  # Permet d'aligner les éléments à gauche
        self.taskbar.setLayout(layout)

    def update_time(self):
        """Met à jour l'horloge de la barre des tâches."""
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.clock_label.setText(current_time)

    def resizeEvent(self, event):
        """Met à jour la barre des tâches lors du redimensionnement de la fenêtre."""
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BureauVirtuel()
    window.show()
    sys.exit(app.exec())
