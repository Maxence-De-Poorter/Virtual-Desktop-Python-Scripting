import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QFrame, QMenu, QInputDialog, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QIcon
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget

class VideoPlayerButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/video.png")
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.size())

        self.setStyleSheet("""
            QPushButton { border: none; background: transparent; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.1); }
        """)

        self.clicked.connect(self.open_video_player)

    def open_video_player(self):
        """Ouvre une nouvelle instance du lecteur vidéo."""
        parent_window = self.window()
        if not hasattr(parent_window, "open_windows"):
            parent_window.open_windows = []

        video_player = VideoPlayer(parent_window)
        parent_window.open_windows.append(video_player)
        video_player.show()

class VideoPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)

        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # En-tête personnalisé
        self.title_bar = QWidget(self)
        self.title_bar.setFixedHeight(int(self.height() * 0.04))  # 4% de la hauteur
        self.title_bar.setStyleSheet("""
            background-color: #444444;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        """)
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(5, 5, 5, 5)

        self.title_label = QLabel("Lecteur Vidéo", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(20, 20)  # Réduire la taille de la croix rouge
        self.close_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: white;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: rgba(255, 0, 0, 0.5);
                color: white;
            }
        """)
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)

        self.layout.addWidget(self.title_bar)

        # Widget pour la lecture vidéo
        self.video_widget = QVideoWidget(self)
        self.video_widget.setStyleSheet("background-color: black;")
        self.layout.addWidget(self.video_widget)

        # Contrôles de lecture
        self.control_layout = QHBoxLayout()
        self.play_button = QPushButton("▶️")
        self.play_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        self.play_button.clicked.connect(self.play_video)
        self.control_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("⏸️")
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        self.pause_button.clicked.connect(self.pause_video)
        self.control_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("⏹️")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        self.stop_button.clicked.connect(self.stop_video)
        self.control_layout.addWidget(self.stop_button)

        self.open_button = QPushButton("Ouvrir Vidéo")
        self.open_button.setStyleSheet("""
            QPushButton {
                background-color: #0078D7;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        self.open_button.clicked.connect(self.open_file)
        self.control_layout.addWidget(self.open_button)

        self.layout.addLayout(self.control_layout)

        # Initialisation du lecteur multimédia
        self.media_player = QMediaPlayer(self)
        self.media_player.setVideoOutput(self.video_widget)

        # Variables pour le déplacement de la fenêtre
        self._drag_start_position = None
        self._drag_offset = None

    def play_video(self):
        """Joue la vidéo."""
        self.media_player.play()

    def pause_video(self):
        """Met la vidéo en pause."""
        self.media_player.pause()

    def stop_video(self):
        """Arrête la vidéo."""
        self.media_player.stop()

    def open_file(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier vidéo."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir une vidéo", "", "Video Files (*.mp4 *.avi *.mkv)")
        if file_path:
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.play()

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
