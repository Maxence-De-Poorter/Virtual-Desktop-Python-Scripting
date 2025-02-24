from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QTime
from src.start_menu import StartButton
from src.file_explorer import FileExplorerButton
from src.agenda import AgendaButton  # Importe le bouton de l'agenda

class TaskBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
            TaskBar {
                background-color: rgba(34, 34, 34, 0.85); /* Fond unifié */
            }
        """)

        self.setGeometry(0, parent.height() - 50, parent.width(), 50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 10, 5)
        layout.setSpacing(15)

        self.start_button = StartButton()
        layout.addWidget(self.start_button)

        self.file_explorer_button = FileExplorerButton(self)  # 📌 Assure-toi que le parent est bien `self`
        layout.addWidget(self.file_explorer_button)

        self.agenda_button = AgendaButton(self)  # Ajoute le bouton de l'agenda
        layout.addWidget(self.agenda_button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(spacer)

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock_label.setStyleSheet("font-size: 16px; padding-right: 10px; color: white;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()
        layout.addWidget(self.clock_label)

        self.setLayout(layout)

    def update_time(self):
        """ Met à jour l'horloge de la barre des tâches. """
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.clock_label.setText(current_time)

    def resizeEvent(self, event):
        """ Ajuste la largeur de la barre des tâches lors du redimensionnement de la fenêtre. """
        self.setGeometry(0, self.parent().height() - 50, self.parent().width(), 50)
        super().resizeEvent(event)
