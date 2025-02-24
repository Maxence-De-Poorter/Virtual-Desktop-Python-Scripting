from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QCalendarWidget, QListWidget, QInputDialog, QMessageBox,
    QDateTimeEdit, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QMenu
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QDateTime, QDate, QRect
import os

class AgendaButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__("", parent)
        self.setFixedSize(40, 40)
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/agenda.png")
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

        self.clicked.connect(self.open_agenda)

    def open_agenda(self):
        """Ouvre une nouvelle instance de la fenêtre d'agenda."""
        print("[DEBUG] Ouverture de l'Agenda.")
        parent_window = self.window()

        if not hasattr(parent_window, "open_windows"):
            parent_window.open_windows = []

        agenda = AgendaWindow(parent_window)
        parent_window.open_windows.append(agenda)
        agenda.show()

class AgendaWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Agenda")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Fond de la fenêtre
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setStyleSheet("""
            background-color: grey;
            border-radius: 10px;
            border: 2px solid #b0b0b0;
        """)

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Barre de titre avec bouton Fermer
        self.title_bar = QHBoxLayout()
        self.title_bar.setContentsMargins(10, 5, 10, 5)
        self.title_label = QLabel("📅 Agenda", self)
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

        # Widget de calendrier
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(lambda: self.show_events_for_date(self.calendar.selectedDate()))
        self.main_layout.addWidget(self.calendar)

        # Liste des événements
        self.event_list = QListWidget(self)
        self.event_list.setStyleSheet("""
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
        self.event_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.event_list.customContextMenuRequested.connect(self.show_context_menu)
        self.main_layout.addWidget(self.event_list)

        # Boutons pour ajouter et modifier des événements
        self.button_layout = QHBoxLayout()
        self.add_button = QPushButton("Ajouter Événement")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_button.clicked.connect(self.open_event_dialog)
        self.modify_button = QPushButton("Modifier Événement")
        self.modify_button.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #e0ac0f;
            }
        """)
        self.modify_button.clicked.connect(self.modify_event)
        self.remove_button = QPushButton("Supprimer Événement")
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-size: 16px;
                border: none;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.remove_button.clicked.connect(self.remove_event)
        self.button_layout.addWidget(self.add_button)
        self.button_layout.addWidget(self.modify_button)
        self.button_layout.addWidget(self.remove_button)
        self.main_layout.addLayout(self.button_layout)

        # Dictionnaire pour stocker les événements
        self.events = {}

        # Indicateurs d'événements
        self.event_indicators = {}

        self.setLayout(self.main_layout)
        self.center_in_bureau()

    def center_in_bureau(self):
        """Centre la fenêtre dans le bureau virtuel."""
        if self.parent():
            parent_geometry = self.parent().geometry()
            window_geometry = self.frameGeometry()
            window_geometry.moveCenter(parent_geometry.center())
            self.move(window_geometry.topLeft())

    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    def open_event_dialog(self, event_to_edit=None):
        """Ouvre un dialogue pour ajouter ou modifier un événement."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter/Modifier un Événement")
        dialog.setLayout(QFormLayout())

        # Champs pour le nom, date de début et date de fin
        name_field = QLineEdit(dialog)
        start_datetime = QDateTimeEdit(dialog)
        start_datetime.setDateTime(QDateTime.currentDateTime())
        start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        start_datetime.setCalendarPopup(True)
        end_datetime = QDateTimeEdit(dialog)
        end_datetime.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # 1 heure après
        end_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        end_datetime.setCalendarPopup(True)

        dialog.layout().addRow("Nom de l'événement:", name_field)
        dialog.layout().addRow("Date et heure de début:", start_datetime)
        dialog.layout().addRow("Date et heure de fin:", end_datetime)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        dialog.layout().addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if event_to_edit:
            name_field.setText(event_to_edit[0])
            start_datetime.setDateTime(QDateTime.fromString(f"{event_to_edit[1][0]} {event_to_edit[1][1]}", "yyyy-MM-dd HH:mm"))
            end_datetime.setDateTime(QDateTime.fromString(f"{event_to_edit[1][0]} {event_to_edit[2]}", "yyyy-MM-dd HH:mm"))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            event_name = name_field.text()
            start_time = start_datetime.dateTime()
            end_time = end_datetime.dateTime()

            # Validation des dates
            if start_time >= QDateTime.currentDateTime() and end_time > start_time:
                event_key = (start_time.date(), start_time.time().toString("HH:mm"))
                if event_to_edit:
                    # Mettre à jour l'événement existant
                    old_event_key = event_to_edit[1]
                    if old_event_key in self.events:
                        del self.events[old_event_key]
                    if old_event_key in self.event_indicators:
                        self.event_indicators[old_event_key].deleteLater()
                        del self.event_indicators[old_event_key]
                self.events[event_key] = (event_name, end_time.toString("HH:mm"))
                self.show_events_for_date(self.calendar.selectedDate())
            else:
                QMessageBox.warning(self, "Erreur", "La date de fin doit être après la date de début et les événements ne peuvent pas être dans le passé.")

    def modify_event(self):
        """Modifier l'événement sélectionné."""
        selected_items = self.event_list.selectedItems()
        if selected_items:
            event_text = selected_items[0].text()
            parts = event_text.split(" - ")
            if len(parts) == 3:
                event_name = parts[0]
                start_time = QDateTime.fromString(f"{parts[1][:10]} {parts[1][11:]}", "yyyy-MM-dd HH:mm")
                end_time = QDateTime.fromString(f"{parts[2][:10]} {parts[2][11:]}", "yyyy-MM-dd HH:mm")
                event_key = (start_time.date(), start_time.time().toString("HH:mm"))
                self.open_event_dialog((event_name, event_key, end_time.toString("HH:mm")))

    def remove_event(self):
        """Supprimer l'événement sélectionné de la liste."""
        selected_items = self.event_list.selectedItems()
        if selected_items:
            for item in selected_items:
                # Supprimer l'événement du dictionnaire
                event_text = item.text()
                parts = event_text.split(" - ")
                if len(parts) == 3:
                    event_key = (QDateTime.fromString(f"{parts[1][:10]} {parts[1][11:]}", "yyyy-MM-dd HH:mm").date(), parts[1][11:])
                    if event_key in self.events:
                        del self.events[event_key]
                self.event_list.takeItem(self.event_list.row(item))
                # Supprimer l'indicateur d'événement
                if event_key in self.event_indicators:
                    self.event_indicators[event_key].deleteLater()
                    del self.event_indicators[event_key]

    def show_context_menu(self, position):
        """Afficher le menu contextuel pour modifier ou supprimer un événement."""
        menu = QMenu(self)
        modify_action = QAction("Modifier Événement", self)
        delete_action = QAction("Supprimer Événement", self)
        menu.addAction(modify_action)
        menu.addAction(delete_action)

        action = menu.exec(self.event_list.mapToGlobal(position))
        if action == modify_action:
            self.modify_event()
        elif action == delete_action:
            self.remove_event()

    def show_events_for_date(self, date):
        """Afficher les événements pour la date sélectionnée."""
        self.event_list.clear()
        for key, value in self.events.items():
            if key[0] == date:
                event_name, end_time = value
                self.event_list.addItem(f"{event_name} - {key[1]} - {end_time}")
                # Ajouter un indicateur d'événement
                if key not in self.event_indicators:
                    indicator = QLabel(self.calendar)
                    indicator.setStyleSheet("background: red; border-radius: 5px;")
                    indicator.setGeometry(self.calendar.rect())
                    indicator.move(self.calendar.x() + 5, self.calendar.y() + 5)
                    self.event_indicators[key] = indicator

        # Supprimer les indicateurs pour les dates sans événements
        keys_to_remove = [key for key in self.event_indicators if key[0] != date]
        for key in keys_to_remove:
            self.event_indicators[key].deleteLater()
            del self.event_indicators[key]
