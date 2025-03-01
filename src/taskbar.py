from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QPushButton
from PyQt6.QtCore import Qt, QTimer, QTime
from src.start_menu import StartButton
from src.file_explorer import FileExplorerButton
from src.terminal import TerminalButton
from src.chatbot import ChatbotButton
from src.browser import BrowserButton

class TaskBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

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
        layout.addWidget(self.start_button)

        self.file_explorer_button = FileExplorerButton(self)
        layout.addWidget(self.file_explorer_button)

        self.terminal_button = TerminalButton(self)
        layout.addWidget(self.terminal_button)

        self.chatbot_button = ChatbotButton(self)
        layout.addWidget(self.chatbot_button)

        self.browser_button = BrowserButton(self)
        layout.addWidget(self.browser_button)

        # 📌 Bouton Flux RSS
        self.flux_button = QPushButton("Flux RSS")
        self.flux_button.setStyleSheet("color: white; background-color: #555; padding: 5px;")
        self.flux_button.clicked.connect(parent.ouvrir_flux_rss)
        layout.addWidget(self.flux_button)

        # 📊 Bouton Graph Temps Réel
        self.graph_button = QPushButton("Graph Temps Réel")
        self.graph_button.setStyleSheet("color: white; background-color: #555; padding: 5px;")
        self.graph_button.clicked.connect(parent.ouvrir_graph_temps_reel)
        layout.addWidget(self.graph_button)

        # 🎥 Bouton Vidéo Player
        self.video_button = QPushButton("🎥 Vidéos")
        self.video_button.setStyleSheet("color: white; background-color: #555; padding: 5px;")
        self.video_button.clicked.connect(parent.ouvrir_video_player)
        layout.addWidget(self.video_button)

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
        current_time = QTime.currentTime().addSecs(3600)
        self.clock_label.setText(current_time.toString("HH:mm:ss"))

    def resizeEvent(self, event):
        self.setGeometry(0, self.parent().height() - 50, self.parent().width(), 50)
        super().resizeEvent(event)
