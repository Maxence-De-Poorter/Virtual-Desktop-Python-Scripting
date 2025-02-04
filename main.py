import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from src.taskbar import TaskBar

class BureauVirtuel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bureau Virtuel")
        self.setGeometry(100, 100, 800, 600)

        # Création du widget principal (le bureau)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Ajouter la barre des tâches
        self.taskbar = TaskBar(self)
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)

    def resizeEvent(self, event):
        """Met à jour la barre des tâches lors du redimensionnement de la fenêtre."""
        self.taskbar.setGeometry(0, self.height() - 50, self.width(), 50)
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BureauVirtuel()
    window.show()
    sys.exit(app.exec())
