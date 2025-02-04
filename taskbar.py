from PyQt6.QtWidgets import QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
from src.start_button import StartButton
from src.clock import Clock

class TaskBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #222; color: white;")
        
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 10, 5)
        layout.setSpacing(10)

        # Bouton Démarrer
        self.start_button = StartButton()
        layout.addWidget(self.start_button)

        # Ajout d'un espace dynamique pour pousser l'horloge à droite
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)

        # Horloge
        self.clock = Clock()
        layout.addWidget(self.clock)

        self.setLayout(layout)
