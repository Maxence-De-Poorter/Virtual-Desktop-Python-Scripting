import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QPushButton, QTextEdit, QListWidget, QDialog,
    QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QMenu, QFrame, QToolTip, QWidget, QLabel
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QDateTime, QDate, QSize
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
        """Ouvre une nouvelle instance de la fenêtre de notes."""
        print("[DEBUG] Ouverture de Notes.")
        parent_window = self.window()

        if not hasattr(parent_window, "open_windows"):
            parent_window.open_windows = []

        note = NoteWindow(parent_window)
        parent_window.open_windows.append(note)
        note.show()

class NoteWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prise de Notes")
        self.resize(800, 600)

        # Layout principal
        self.main_layout = QVBoxLayout(self)

        # Barre de titre avec bouton Fermer
        self.title_bar = QHBoxLayout()
        self.title_label = QLabel("📝 Prise de Notes", self)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 18px; color: white;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.close_button = QPushButton("❌")
        self.close_button.setFixedSize(40, 30)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
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
        self.main_layout.addLayout(self.title_bar)

        # Liste des notes
        self.notes_list = QListWidget(self)
        self.notes_list.setStyleSheet("""
            QListWidget {
                background: white;
                border: 1px solid #b0b0b0;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
            }
            QListWidget::item:selected {
                background: #0078D7;
                color: white;
                border-radius: 5px;
            }
        """)
        self.main_layout.addWidget(self.notes_list)

        # Boutons pour ajouter, modifier et supprimer des notes
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
        self.add_button.clicked.connect(self.open_note_dialog)
        self.modify_button = QPushButton("Modifier Note")
        self.modify_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        self.modify_button.clicked.connect(self.modify_note)
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
        self.button_layout.addWidget(self.modify_button)
        self.button_layout.addWidget(self.remove_button)
        self.button_layout.addStretch()
        self.main_layout.addLayout(self.button_layout)

        # Dictionnaire pour stocker les notes
        self.notes = {}

        # Menu contextuel pour les notes
        self.notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_context_menu)

        self.setLayout(self.main_layout)
        self.center_in_bureau()

    def center_in_bureau(self):
        """Centre la fenêtre dans le bureau virtuel."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def open_note_dialog(self):
        """Ouvre un dialogue pour ajouter ou modifier une note."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter/Modifier une Note")
        dialog.setLayout(QFormLayout())

        # Champs pour le titre et le contenu de la note
        title_field = QLineEdit(dialog)
        content_field = QTextEdit(dialog)

        dialog.layout().addRow("Titre:", title_field)
        dialog.layout().addRow("Contenu:", content_field)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        dialog.layout().addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = title_field.text()
            content = content_field.toPlainText()
            self.notes[title] = content
            self.show_notes()

    def modify_note(self):
        """Modifier la note sélectionnée."""
        selected_items = self.notes_list.selectedItems()
        if selected_items:
            note_text = selected_items[0].text()
            title = note_text
            self.open_note_dialog(title)

    def remove_note(self):
        """Supprimer la note sélectionnée de la liste."""
        selected_items = self.notes_list.selectedItems()
        if selected_items:
            for item in selected_items:
                note_text = item.text()
                if note_text in self.notes:
                    del self.notes[note_text]
                self.notes_list.takeItem(self.notes_list.row(item))

    def show_context_menu(self, position):
        """Afficher le menu contextuel pour modifier ou supprimer une note."""
        menu = QMenu(self)
        modify_action = QAction("Modifier", self)
        delete_action = QAction("Supprimer", self)
        menu.addAction(modify_action)
        menu.addAction(delete_action)

        action = menu.exec(self.notes_list.mapToGlobal(position))
        if action == modify_action:
            self.modify_note()
        elif action == delete_action:
            self.remove_note()

    def show_notes(self):
        """Afficher toutes les notes."""
        self.notes_list.clear()
        for title, content in self.notes.items():
            self.notes_list.addItem(title)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteWindow()
    window.show()
    sys.exit(app.exec())
