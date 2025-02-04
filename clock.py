from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer, QTime

class Clock(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.setStyleSheet("font-size: 16px; padding-right: 10px;")

        # Timer pour mettre à jour l'heure
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Mise à jour toutes les secondes
        self.update_time()

    def update_time(self):
        """Met à jour l'horloge de la barre des tâches."""
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.setText(current_time)
