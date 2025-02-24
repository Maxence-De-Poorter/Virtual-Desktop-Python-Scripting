import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPlainTextEdit,
    QApplication, QPushButton, QLabel
)
from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QIcon

class TerminalButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        # Chemin vers l'icône du terminal
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/terminal_icon.png")
        self.setIcon(QIcon(icon_path))
        self.setIconSize(self.size())
        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        self.clicked.connect(self.open_terminal)
    
    def open_terminal(self):
        """Ouvre une nouvelle instance du terminal."""
        print("[DEBUG] Ouverture du Terminal.")
        parent_window = self.window()
        if not hasattr(parent_window, "open_windows"):
            parent_window.open_windows = []
        terminal = TerminalWidget(parent_window)
        parent_window.open_windows.append(terminal)
        terminal.show()

class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Supprimer la bordure native pour implémenter notre propre en-tête
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)
        
        # Layout principal
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # En-tête personnalisé
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #444444;")
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(5, 5, 5, 5)
        
        # Titre de la fenêtre
        self.title_label = QLabel("Invite de commande", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()
        
        # Bouton de fermeture (croix)
        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)
        
        # Ajout de l'en-tête dans le layout principal
        self.layout.addWidget(self.title_bar)
        
        # Layout pour la zone terminal (sortie et saisie)
        self.terminal_layout = QVBoxLayout()
        self.terminal_layout.setContentsMargins(10, 10, 10, 10)
        
        # Zone d'affichage de la sortie (lecture seule)
        self.output_area = QPlainTextEdit(self)
        self.output_area.setReadOnly(True)
        self.terminal_layout.addWidget(self.output_area)
        
        # Ligne de saisie pour entrer les commandes
        self.input_line = QLineEdit(self)
        self.input_line.returnPressed.connect(self.execute_command)
        self.terminal_layout.addWidget(self.input_line)
        
        # Ajout du layout terminal dans le layout principal
        self.layout.addLayout(self.terminal_layout)
        
        # Initialisation de QProcess pour lancer l'invite de commande Windows
        self.process = QProcess(self)
        # Fusionner stdout et stderr pour une lecture simplifiée
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.start("cmd.exe")
        
    def execute_command(self):
        """Exécute la commande saisie dans la ligne d'entrée."""
        command = self.input_line.text().strip()
        if command:
            # Affiche la commande dans la zone de sortie pour simuler l'invite
            self.output_area.appendPlainText(f"> {command}")
            # Si la commande est 'exit', on ferme le terminal
            if command.lower() == "exit":
                self.close()
                return
            # Traitement de la commande echo : affiche le texte directement
            elif command.lower().startswith("echo"):
                parts = command.split(" ", 1)
                echo_text = parts[1] if len(parts) > 1 else ""
                self.output_area.appendPlainText(echo_text)
                self.input_line.clear()
                return
            # Envoie la commande au process suivie d'un saut de ligne
            self.process.write((command + "\n").encode("utf-8"))
            self.input_line.clear()
            
    def handle_stdout(self):
        """Gère et affiche la sortie standard du process."""
        data = self.process.readAllStandardOutput()
        output = bytes(data).decode("utf-8", errors="replace")
        self.output_area.appendPlainText(output)
        
    def handle_stderr(self):
        """Gère et affiche la sortie d'erreur du process."""
        data = self.process.readAllStandardError()
        output = bytes(data).decode("utf-8", errors="replace")
        self.output_area.appendPlainText(output)
