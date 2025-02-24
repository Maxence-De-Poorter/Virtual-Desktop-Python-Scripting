from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QTime
from src.start_menu import StartButton
from src.file_explorer import FileExplorerButton

class TaskBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Active la transparence de la fenêtre pour permettre un fond translucide
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Le style définit ici un fond sombre avec une opacité de 85%
        self.setStyleSheet("""
            TaskBar {
                background-color: rgba(34, 34, 34, 0.85);
            }
        """)

        self.setGeometry(0, parent.height() - 50, parent.width(), 50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 10, 5)
        layout.setSpacing(15)

        self.start_button = StartButton()
        layout.addWidget(self.start_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.file_explorer_button = FileExplorerButton(self)
        layout.addWidget(self.file_explorer_button, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addStretch()

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.clock_label.setStyleSheet("font-size: 16px; padding-right: 10px; color: white;")
        layout.addWidget(self.clock_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

        self.setLayout(layout)

    def update_time(self):
        """Met à jour l'horloge de la barre des tâches en ajoutant 1 heure."""
        # Récupère l'heure actuelle et ajoute 3600 secondes (1 heure)
        current_time = QTime.currentTime().addSecs(3600)
        self.clock_label.setText(current_time.toString("HH:mm:ss"))

    def resizeEvent(self, event):
        """Ajuste la largeur de la barre des tâches lors du redimensionnement de la fenêtre."""
        self.setGeometry(0, self.parent().height() - 50, self.parent().width(), 50)
        super().resizeEvent(event)
