import sys
import os
import vlc
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QFileDialog, QLineEdit, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer


class VideoPlayerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎥 Lecteur Vidéo")
        self.resize(800, 600)

        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                color: white;
                font-family: Arial;
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
            QSlider {
                background-color: #444;
            }
            QLineEdit {
                background-color: #2e2e3e;
                color: white;
                padding: 5px;
                border: 1px solid #555;
                border-radius: 4px;
            }
        """)

        self.layout = QVBoxLayout(self)

        # 📥 Barre URL
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("URL de la vidéo (YouTube, flux...)")
        self.layout.addWidget(self.url_bar)

        self.load_url_button = QPushButton("Lire URL")
        self.load_url_button.clicked.connect(self.load_url)
        self.layout.addWidget(self.load_url_button)

        # 🎥 Zone vidéo
        self.video_frame = QLabel("Vidéo ici")
        self.video_frame.setStyleSheet("background-color: black;")
        self.video_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.video_frame)

        # 🎮 Contrôles lecture
        controls_layout = QHBoxLayout()

        self.play_button = QPushButton("▶️")
        self.play_button.clicked.connect(self.play_video)
        controls_layout.addWidget(self.play_button)

        self.pause_button = QPushButton("⏸️")
        self.pause_button.clicked.connect(self.pause_video)
        controls_layout.addWidget(self.pause_button)

        self.stop_button = QPushButton("⏹️")
        self.stop_button.clicked.connect(self.stop_video)
        controls_layout.addWidget(self.stop_button)

        self.layout.addLayout(controls_layout)

        # 📊 Barre de progression
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.sliderMoved.connect(self.set_position)
        self.layout.addWidget(self.slider)

        # 📂 Bouton pour ouvrir un fichier local
        self.open_file_button = QPushButton("📂 Ouvrir fichier")
        self.open_file_button.clicked.connect(self.open_file)
        self.layout.addWidget(self.open_file_button)

        # ⏱️ Timer pour mise à jour du slider
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_slider)

        # ✅ Vérification VLC et initialisation
        self.vlc_path = r"C:\Program Files\VideoLAN\VLC"  # À adapter si VLC est ailleurs
        self.ensure_vlc_in_path()

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

    def ensure_vlc_in_path(self):
        """ Vérifie que VLC est bien dans le PATH et chargeable """
        if self.vlc_path not in os.environ['PATH']:
            os.environ['PATH'] = self.vlc_path + os.pathsep + os.environ['PATH']

        # Vérification via Instance (au lieu de libvlc_new)
        try:
            test_instance = vlc.Instance()  # Test propre
        except Exception as e:
            QMessageBox.critical(self, "Erreur VLC", f"Impossible de charger VLC.\nVérifie que VLC est installé.\n\nDétails: {e}")
            sys.exit(1)

    def play_video(self):
        self.player.play()
        self.timer.start(100)

    def pause_video(self):
        self.player.pause()

    def stop_video(self):
        self.player.stop()
        self.timer.stop()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir une vidéo", "", "Fichiers Vidéo (*.mp4 *.avi *.mkv *.mov)")
        if file_path:
            self.play_media(file_path)

    def load_url(self):
        url = self.url_bar.text().strip()
        if url:
            self.play_media(url)

    def play_media(self, source):
        if not os.path.isabs(source):
            source = get_absolute_video_path(source)

        media = self.instance.media_new(source)
        self.player.set_media(media)
        self.player.set_hwnd(int(self.video_frame.winId()))
        self.player.play()
        self.timer.start(100)



    def set_position(self, position):
        self.player.set_position(position / 100.0)

    def update_slider(self):
        if self.player.is_playing():
            pos = int(self.player.get_position() * 100)
            self.slider.setValue(pos)
            
    def get_absolute_video_path(relative_path):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        return os.path.join(base_dir, relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayerWindow()
    window.show()
    sys.exit(app.exec())
