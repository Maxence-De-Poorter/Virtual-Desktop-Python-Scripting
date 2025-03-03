from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpacerItem,  QSizePolicy, QPushButton
from PyQt6.QtCore import Qt, QTimer, QTime
from src.start_menu import StartButton
from src.file_explorer import FileExplorerButton
from src.terminal import TerminalButton
from src.chatbot import ChatbotButton
from src.browser import BrowserButton
from src.flux_rss import FluxRSSButton
from src.realtime_graph import RealTimeGraphButton
from src.agenda import AgendaButton
from src.notes import NotesButton
from src.galery import GalleryButton  # Importe le bouton de la galerie
from src.video import VideoPlayerButton  # Importe le bouton du lecteur vidéo


class TaskBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Ajouter un fond opaque à la barre des tâches
        self.setStyleSheet("""
            TaskBar {
                background-color: rgba(34, 34, 34, 0.85); /* Fond unifié avec opacité */
                color: white; /* Couleur du texte */
                font-size: 14px; /* Taille de la police */
            }
        """)

        self.setGeometry(0, parent.height() - 50, parent.width(), 50)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 10, 5)
        layout.setSpacing(15)

        self.start_button = StartButton()
        self.start_button.clicked.connect(self.close_all_applications)  # Connecte au bouton pour fermer toutes les applications
        layout.addWidget(self.start_button)

        self.file_explorer_button = FileExplorerButton(self)
        layout.addWidget(self.file_explorer_button)

        self.terminal_button = TerminalButton(self)
        layout.addWidget(self.terminal_button)

        self.chatbot_button = ChatbotButton(self)
        layout.addWidget(self.chatbot_button)

        self.browser_button = BrowserButton(self)
        layout.addWidget(self.browser_button)

        self.fluxRSS_button = FluxRSSButton(self)
        layout.addWidget(self.fluxRSS_button)

        self.realTimeGraph_button = RealTimeGraphButton(self)
        layout.addWidget(self.realTimeGraph_button)

        self.agenda_button = AgendaButton(self)
        layout.addWidget(self.agenda_button)

        self.notes_button = NotesButton(self)  # Ajoute le bouton des notes
        layout.addWidget(self.notes_button)

        self.gallery_button = GalleryButton(self)  # Ajoute le bouton de la galerie
        layout.addWidget(self.gallery_button)

        self.video_player_button = VideoPlayerButton(self)  # Ajoute le bouton du lecteur vidéo
        layout.addWidget(self.video_player_button)

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
        """Met à jour l'horloge de la barre des tâches en ajoutant 1 heure."""
        # Récupère l'heure actuelle et ajoute 3600 secondes (1 heure)
        current_time = QTime.currentTime().addSecs(3600)
        self.clock_label.setText(current_time.toString("HH:mm:ss"))

    def resizeEvent(self, event):
        """ Ajuste la largeur de la barre des tâches lors du redimensionnement de la fenêtre. """
        self.setGeometry(0, self.parent().height() - 50, self.parent().width(), 50)
        super().resizeEvent(event)

    def close_all_applications(self):
        """Ferme toutes les applications ouvertes."""
        for window in self.parent().open_windows:
            window.close()
