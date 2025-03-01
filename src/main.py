import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from src.taskbar import TaskBar
from src.flux_rss import FluxRSSWindow
from src.realtime_graph import RealTimeGraphWindow
from src.video_player import VideoPlayerWindow

class BureauVirtuel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bureau Virtuel")
        self.setGeometry(100, 100, 1080, 720)
        self.setMinimumSize(1080, 720)

        # 📌 Fond d'écran
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        self.background_pixmap = QPixmap(os.path.join("assets", "background.jpg"))
        self.update_background()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 📌 Barre des tâches
        self.taskbar = TaskBar(self)
        self.open_windows = []

        # 📌 Références pour les fenêtres
        self.flux_rss_window = None
        self.graph_window = None
        self.video_window = None

    def resizeEvent(self, event):
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        self.update_background()
        super().resizeEvent(event)

    def update_background(self):
        window_width = self.width()
        window_height = self.height()

        scaled_pixmap = self.background_pixmap.scaled(
            window_width, window_height,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )

        self.background_label.setPixmap(scaled_pixmap)
        self.background_label.setGeometry(0, 0, window_width, window_height)

    def ouvrir_flux_rss(self):
        if not self.flux_rss_window or not self.flux_rss_window.isVisible():
            self.flux_rss_window = FluxRSSWindow()
            self.flux_rss_window.show()
        else:
            self.flux_rss_window.raise_()
            self.flux_rss_window.activateWindow()

    def ouvrir_graph_temps_reel(self):
        if not self.graph_window or not self.graph_window.isVisible():
            self.graph_window = RealTimeGraphWindow()
            self.graph_window.show()
        else:
            self.graph_window.raise_()
            self.graph_window.activateWindow()

    def ouvrir_video_player(self, file_path=None):
        if not hasattr(self, 'video_window') or self.video_window is None:
            self.video_window = VideoPlayerWindow()

        if file_path:
            abs_path = get_absolute_video_path(file_path)
            self.video_window.play_media(abs_path)

        self.video_window.show()
        self.video_window.raise_()
        self.video_window.activateWindow()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BureauVirtuel()
    window.show()
    sys.exit(app.exec())
