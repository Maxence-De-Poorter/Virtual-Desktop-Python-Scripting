import sys
import os
import openai
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Configure ton API Key OpenAI
API_KEY = "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"  # Remplace par ta clé
client = openai.OpenAI(api_key=API_KEY)  # Utilisation du client OpenAI

class ChatbotButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/chatbot_icon.png")
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

        self.clicked.connect(self.open_chatbot)

    def open_chatbot(self):
        """Ouvre ou ferme l'instance du chatbot."""
        parent_window = self.window()

        if hasattr(parent_window, 'chatbot_window') and parent_window.chatbot_window.isVisible():
            parent_window.chatbot_window.close()
        else:
            chatbot = ChatbotWidget(parent_window)
            parent_window.chatbot_window = chatbot
            parent_window.open_windows.append(chatbot)
            chatbot.show()

class ChatbotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Supprime la bordure de la fenêtre pour appliquer un style personnalisé
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.resize(800, 600)

        # Layout principal sans marges pour occuper tout l'espace
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        # --- En-tête personnalisé ---
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: #444444;")
        self.title_layout = QHBoxLayout(self.title_bar)
        self.title_layout.setContentsMargins(5, 5, 5, 5)

        self.title_label = QLabel("Chatbot AI", self.title_bar)
        self.title_label.setStyleSheet("color: white; font-size: 16px;")
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()

        self.close_button = QPushButton("❌", self.title_bar)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("border: none; background: transparent; color: white; font-size: 16px;")
        self.close_button.clicked.connect(self.close)
        self.title_layout.addWidget(self.close_button)

        self.layout.addWidget(self.title_bar)

        # --- Zone de chat (affichage et saisie) ---
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setContentsMargins(10, 10, 10, 10)

        # Zone d'affichage des messages (lecture seule)
        self.chat_display = QTextEdit(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("border: none; background-color: #2e2e2e; color: white; font-size: 14px;")
        self.chat_layout.addWidget(self.chat_display)

        # Zone de saisie utilisateur
        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("Tapez votre message ici...")
        self.input_line.setStyleSheet("border: none; background-color: #3a3a3a; color: white; padding: 8px;")
        self.input_line.returnPressed.connect(self.send_message)  # Envoi sur Entrée
        self.chat_layout.addWidget(self.input_line)

        self.layout.addLayout(self.chat_layout)

        # Historique des conversations
        self.conversation_history = [{"role": "system", "content": "Tu es un assistant utile."}]

        # Variables pour le déplacement de la fenêtre
        self._drag_start_position = None
        self._drag_offset = None

    def send_message(self):
        """Gère l'envoi des messages et l'affichage des réponses du chatbot."""
        user_message = self.input_line.text().strip()
        if not user_message:
            return

        # Affiche le message utilisateur dans l'interface
        self.chat_display.append(f"<b>Vous:</b> {user_message}")
        self.input_line.clear()

        # Ajouter le message utilisateur à l'historique
        self.conversation_history.append({"role": "user", "content": user_message})

        # Appel à l'API OpenAI
        response = self.get_bot_response()

        # Affichage de la réponse du bot
        self.chat_display.append(f"<b>Bot:</b> {response}")
        self.chat_display.append("")  # Saut de ligne

    def get_bot_response(self):
        """Envoie le contexte à OpenAI et retourne la réponse."""
        try:
            response = client.chat.completions.create(
                model="gpt-4",  # Ou "gpt-3.5-turbo"
                messages=self.conversation_history
            )

            bot_reply = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": bot_reply})
            return bot_reply
        except Exception as e:
            return f"Erreur: {str(e)}"

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatbotWidget()
    window.show()
    sys.exit(app.exec())
