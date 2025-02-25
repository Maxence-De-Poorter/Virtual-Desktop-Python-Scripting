import sys
from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QListWidget, QDialog,
    QLabel, QLineEdit, QDialogButtonBox, QWidget, QMainWindow
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSize, QPoint
import os

class NotesButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/notes.png")
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(40, 40))
        self.setStyleSheet("""
            QPushButton {
                background-color: #FFA500;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #e0ac0f;
            }
        """)
        self.clicked.connect(self.open_notes)

    def open_notes(self):
        """Ouvre une nouvelle instance de la fenêtre de notes ou ferme l'application si déjà ouverte."""
        parent_window = self.window()

        if hasattr(parent_window, 'note_window') and parent_window.note_window.isVisible():
            # Ferme uniquement la fenêtre de notes
            parent_window.note_window.close()
        else:
            # Crée une nouvelle instance si aucune n'est ouverte
            parent_window.note_window = NoteWindow(parent_window)
            parent_window.note_window.show()
            self.adjust_note_window_size(parent_window.note_window)

    def adjust_note_window_size(self, note_window):
        """Ajuste la taille de la fenêtre de notes en fonction de la taille de l'environnement parent."""
        parent_window = self.window()
        note_window.resize(parent_window.size() * 0.8)
        note_window.move(
            int(parent_window.x() + parent_window.width() * 0.1),
            int(parent_window.y() + parent_window.height() * 0.1)
        )

class NoteWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prise de Notes")
        self.setStyleSheet("background-color: #f0f0f0;")  # Fond gris pour la fenêtre de notes
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)  # Supprime les bordures de la fenêtre

        # Layout principal
        self.main_layout = QVBoxLayout(self)

        # Widget conteneur pour la barre de titre
        self.title_bar_container = QWidget(self)
        self.title_bar_container.setStyleSheet("background-color: #e0e0e0;")  # Rendre la barre de titre opaque
        self.title_bar_container.setLayout(QHBoxLayout())

        # Barre de titre avec bouton Fermer
        self.title_bar = self.title_bar_container.layout()
        self.title_label = QLabel("📝 Prise de Notes", self)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: black;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.close_button = QPushButton("❌")
        self.close_button.setFixedSize(40, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: black;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: red;
                color: white;
            }
        """)
        self.close_button.clicked.connect(self.close)
        self.title_bar.addWidget(self.title_label)
        self.title_bar.addStretch()
        self.title_bar.addWidget(self.close_button)

        self.main_layout.addWidget(self.title_bar_container)

        # Layout horizontal pour la liste des notes et le contenu de la note
        self.content_layout = QHBoxLayout()

        # Layout vertical pour la liste des notes et les boutons
        self.notes_list_widget = QWidget(self)
        self.notes_list_layout = QVBoxLayout(self.notes_list_widget)

        # Titre au-dessus de la liste des notes
        self.notes_title = QLabel("Liste des notes", self)
        self.notes_title.setStyleSheet("font-weight: bold; font-size: 16px; color: black;")
        self.notes_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.notes_list_layout.addWidget(self.notes_title)

        # Liste des notes à gauche
        self.notes_list = QListWidget(self)
        self.notes_list.setStyleSheet("""
            QListWidget {
                background: #ffffff;
                border: 1px solid #b0b0b0;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
                color: black;
            }
            QListWidget::item:selected {
                background: #0078D7;
                color: white;
                border-radius: 5px;
            }
        """)
        self.notes_list.itemClicked.connect(self.show_note_content)
        self.notes_list_layout.addWidget(self.notes_list)

        # Boutons pour ajouter et supprimer des notes
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter Note")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_button.clicked.connect(self.add_note)
        self.remove_button = QPushButton("Supprimer Note")
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.remove_button.clicked.connect(self.remove_note)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.remove_button)
        self.button_layout.addStretch()
        self.notes_list_layout.addLayout(self.button_layout)

        self.content_layout.addWidget(self.notes_list_widget)

        # Contenu de la note à droite
        self.note_content = QTextEdit(self)
        self.note_content.setReadOnly(True)  # Désactiver l'édition par défaut
        self.note_content.setStyleSheet("""
            QTextEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #b0b0b0;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
        """)
        self.note_content.textChanged.connect(self.save_note_content)
        self.content_layout.addWidget(self.note_content)

        # Ajustement de la largeur des colonnes
        self.content_layout.setStretch(0, 1)  # Liste des notes
        self.content_layout.setStretch(1, 9)  # Contenu de la note

        self.main_layout.addLayout(self.content_layout)

        # Dictionnaire pour stocker les notes
        self.notes = {}
        self.current_note = None

        self.setLayout(self.main_layout)
        self.center_in_bureau()

        # Variables pour le déplacement de la fenêtre
        self._drag_start_position = None
        self._drag_offset = None

    def center_in_bureau(self):
        """Centre la fenêtre dans le bureau virtuel."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def mousePressEvent(self, event):
        """Gère l'événement de pression de la souris pour déplacer la fenêtre."""
        if event.button() == Qt.MouseButton.LeftButton and self.title_bar_container.geometry().contains(event.pos()):
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

    def add_note(self):
        """Ajouter une nouvelle note avec une boîte de dialogue personnalisée."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une Note")
        dialog.setStyleSheet("background-color: #f0f0f0; color: black;")

        layout = QVBoxLayout(dialog)
        label = QLabel("Titre de la note:", dialog)
        label.setStyleSheet("color: black;")
        layout.addWidget(label)

        title_field = QLineEdit(dialog)
        title_field.setStyleSheet("background-color: #ffffff; color: black;")
        layout.addWidget(title_field)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        layout.addWidget(buttons)

        def on_accept():
            title = title_field.text()
            if title:
                self.notes[title] = ""
                self.notes_list.addItem(title)
            dialog.accept()

        def on_reject():
            dialog.reject()

        buttons.accepted.connect(on_accept)
        buttons.rejected.connect(on_reject)

        dialog.exec()

    def save_note_content(self):
        """Enregistrer le contenu de la note actuellement affichée."""
        if self.current_note:
            self.notes[self.current_note] = self.note_content.toPlainText()

    def remove_note(self):
        """Supprimer la note sélectionnée de la liste."""
        selected_items = self.notes_list.selectedItems()
        if selected_items:
            for item in selected_items:
                note_title = item.text()
                if note_title in self.notes:
                    del self.notes[note_title]
                self.notes_list.takeItem(self.notes_list.row(item))
                self.note_content.clear()
                self.note_content.setReadOnly(True)
                self.current_note = None

    def show_note_content(self, item):
        """Afficher le contenu de la note sélectionnée."""
        note_title = item.text()
        self.current_note = note_title
        self.note_content.setReadOnly(False)  # Activer l'édition
        self.note_content.setText(self.notes.get(note_title, ""))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Environnement Principal")
        self.resize(1000, 800)
        self.setStyleSheet("background-color: #f0f0f0;")  # Fond gris pour la fenêtre principale

        # Ajouter le bouton de notes à la fenêtre principale
        self.notes_button = NotesButton(self)
        self.setCentralWidget(self.notes_button)

    def resizeEvent(self, event):
        """Ajuste la taille de la fenêtre de notes lorsque la fenêtre principale est redimensionnée."""
        if hasattr(self, 'note_window'):
            self.notes_button.adjust_note_window_size(self.note_window)
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
