from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QCalendarWidget, QListWidget, QInputDialog, QMessageBox,
    QDateTimeEdit, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QMenu, QTextEdit, QGridLayout, QApplication, QFrame, QToolTip
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QDateTime, QDate
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
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Fond de la fenêtre avec un style plus esthétique
        self.setStyleSheet("""
            AgendaWindow {
                background-color: #2C3E50;
                border: 1px solid #34495E;
                border-radius: 10px;
            }
            QLabel {
                font-weight: bold;
                font-size: 18px;
                color: white;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                font-size: 16px;
                border: 1px solid #2980B9;
                border-radius: 5px;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QListWidget {
                background: #ECF0F1;
                border: 1px solid #BDC3C7;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
                color: #333;
            }
            QListWidget::item {
                padding: 8px;
                color: #333;
            }
            QListWidget::item:selected {
                background: #3498DB;
                color: white;
                border-radius: 5px;
            }
            CloseButton {
                background: transparent;
                color: white;
                font-size: 18px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
            }
            CloseButton:hover {
                background-color: red;
                color: white;
            }
        """)

        # Layout principal
        self.main_layout = QGridLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # Barre de titre avec bouton Fermer
        self.title_bar = QHBoxLayout()
        self.title_label = QLabel("📅 Agenda", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.close_button = QPushButton("❌")
        self.close_button.setFixedSize(40, 30)
        self.close_button.setObjectName("CloseButton")
        self.close_button.clicked.connect(self.close)
        self.title_bar.addWidget(self.title_label)
        self.title_bar.addStretch()
        self.title_bar.addWidget(self.close_button)
        self.main_layout.addLayout(self.title_bar, 0, 0, 1, 2)

        # Widget de calendrier
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(lambda: self.show_events_for_date(self.calendar.selectedDate()))
        self.main_layout.addWidget(self.calendar, 1, 0)

        # Layout pour les événements et tâches
        self.event_task_layout = QVBoxLayout()

        # Liste des événements
        self.event_list = QListWidget(self)
        self.event_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.event_list.customContextMenuRequested.connect(self.show_context_menu)
        self.event_list.itemClicked.connect(self.show_event_details)
        self.event_list.itemDoubleClicked.connect(self.modify_event)
        self.event_task_layout.addWidget(QLabel("Événements:"))
        self.event_task_layout.addWidget(self.event_list)

        # Liste des tâches
        self.task_list = QListWidget(self)
        self.task_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_context_menu)
        self.task_list.itemClicked.connect(self.show_event_details)
        self.task_list.itemDoubleClicked.connect(self.modify_event)
        self.event_task_layout.addWidget(QLabel("Tâches:"))
        self.event_task_layout.addWidget(self.task_list)
        self.event_task_layout.addStretch()

        self.main_layout.addLayout(self.event_task_layout, 1, 1)

        # Boutons pour ajouter et modifier des événements et tâches
        self.button_layout = QHBoxLayout()
        self.add_event_button = QPushButton("Ajouter Événement")
        self.add_event_button.clicked.connect(lambda: self.open_event_dialog(is_task=False))
        self.add_task_button = QPushButton("Ajouter Tâche")
        self.add_task_button.clicked.connect(lambda: self.open_event_dialog(is_task=True))
        self.modify_button = QPushButton("Modifier")
        self.modify_button.clicked.connect(self.modify_event)
        self.remove_button = QPushButton("Supprimer")
        self.remove_button.clicked.connect(self.remove_event)
        self.button_layout.addWidget(self.add_event_button)
        self.button_layout.addWidget(self.add_task_button)
        self.button_layout.addWidget(self.modify_button)
        self.button_layout.addWidget(self.remove_button)
        self.button_layout.addStretch()
        self.main_layout.addLayout(self.button_layout, 2, 0, 1, 2)

        # Dictionnaire pour stocker les événements et tâches
        self.events = {}
        self.tasks = {}

        # Indicateurs d'événements et tâches
        self.event_indicators = {}
        self.task_indicators = {}

        self.setLayout(self.main_layout)
        self.center_in_bureau()

    def center_in_bureau(self):
        """Centre la fenêtre dans le bureau virtuel."""
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.calendar.setFixedWidth(int(self.width() * 0.8))

    def open_event_dialog(self, is_task=False, event_to_edit=None):
        """Ouvre un dialogue pour ajouter ou modifier un événement ou une tâche."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter/Modifier un Événement/Tâche")
        dialog.setLayout(QFormLayout())

        # Champs pour le titre, la description, date de début et date de fin
        title_field = QLineEdit(dialog)
        description_field = QTextEdit(dialog)
        start_datetime = QDateTimeEdit(dialog)
        start_datetime.setDateTime(QDateTime.currentDateTime())
        start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        start_datetime.setCalendarPopup(True)
        end_datetime = QDateTimeEdit(dialog)
        end_datetime.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # 1 heure après
        end_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        end_datetime.setCalendarPopup(True)

        dialog.layout().addRow("Titre:", title_field)
        dialog.layout().addRow("Description:", description_field)
        dialog.layout().addRow("Date et heure de début:", start_datetime)
        dialog.layout().addRow("Date et heure de fin:", end_datetime)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        dialog.layout().addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if event_to_edit:
            title_field.setText(event_to_edit[0])
            description_field.setText(event_to_edit[1])
            start_datetime.setDateTime(QDateTime.fromString(f"{event_to_edit[2][0]} {event_to_edit[2][1]}", "yyyy-MM-dd HH:mm"))
            end_datetime.setDateTime(QDateTime.fromString(f"{event_to_edit[2][0]} {event_to_edit[3]}", "yyyy-MM-dd HH:mm"))

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = title_field.text()
            description = description_field.toPlainText()
            start_time = start_datetime.dateTime()
            end_time = end_datetime.dateTime()

            # Validation des dates
            if start_time >= QDateTime.currentDateTime() and end_time > start_time:
                event_key = (start_time.date(), start_time.time().toString("HH:mm"))
                if is_task:
                    self.tasks[event_key] = (title, description, end_time.toString("HH:mm"))
                else:
                    self.events[event_key] = (title, description, end_time.toString("HH:mm"))
                self.show_events_for_date(self.calendar.selectedDate())
            else:
                QMessageBox.warning(self, "Erreur", "La date de fin doit être après la date de début et les événements ne peuvent pas être dans le passé.")

    def modify_event(self):
        """Modifier l'événement ou la tâche sélectionné(e)."""
        selected_items = self.event_list.selectedItems()
        if not selected_items:
            selected_items = self.task_list.selectedItems()
        if selected_items:
            event_text = selected_items[0].text()
            parts = event_text.split(" - ")
            if len(parts) == 2:
                title = parts[0]
                description = parts[1]
                start_time = QDateTime.fromString(f"{parts[1][:10]} {parts[1][11:]}", "yyyy-MM-dd HH:mm")
                end_time = QDateTime.fromString(f"{parts[1][:10]} {parts[1][11:]}", "yyyy-MM-dd HH:mm")
                event_key = (start_time.date(), start_time.time().toString("HH:mm"))
                is_task = bool(self.task_list.selectedItems())
                self.open_event_dialog(is_task=is_task, event_to_edit=(title, description, event_key, end_time.toString("HH:mm")))

    def remove_event(self):
        """Supprimer l'événement ou la tâche sélectionné(e) de la liste."""
        selected_items = self.event_list.selectedItems()
        if not selected_items:
            selected_items = self.task_list.selectedItems()
        if selected_items:
            for item in selected_items:
                # Supprimer l'événement ou la tâche du dictionnaire
                event_text = item.text()
                parts = event_text.split(" - ")
                if len(parts) == 2:
                    event_key = (QDateTime.fromString(f"{parts[1][:10]} {parts[1][11:]}", "yyyy-MM-dd HH:mm").date(), parts[1][11:])
                    if event_key in self.events:
                        del self.events[event_key]
                    elif event_key in self.tasks:
                        del self.tasks[event_key]
                if self.event_list.selectedItems():
                    self.event_list.takeItem(self.event_list.row(item))
                else:
                    self.task_list.takeItem(self.task_list.row(item))
                # Supprimer l'indicateur d'événement ou de tâche
                if event_key in self.event_indicators:
                    self.event_indicators[event_key].deleteLater()
                    del self.event_indicators[event_key]
                elif event_key in self.task_indicators:
                    self.task_indicators[event_key].deleteLater()
                    del self.task_indicators[event_key]

    def show_context_menu(self, position):
        """Afficher le menu contextuel pour modifier ou supprimer un événement ou une tâche."""
        menu = QMenu(self)
        modify_action = QAction("Modifier", self)
        delete_action = QAction("Supprimer", self)
        menu.addAction(modify_action)
        menu.addAction(delete_action)

        action = menu.exec(self.event_list.mapToGlobal(position))
        if action == modify_action:
            self.modify_event()
        elif action == delete_action:
            self.remove_event()

    def show_events_for_date(self, date):
        """Afficher les événements et tâches pour la date sélectionnée."""
        self.event_list.clear()
        self.task_list.clear()
        for key, value in self.events.items():
            if key[0] == date:
                title, description, end_time = value
                self.event_list.addItem(f"{title} - {key[1]}")
                # Ajouter un indicateur d'événement
                if key not in self.event_indicators:
                    indicator = QFrame(self.calendar)
                    indicator.setStyleSheet("background: #2ECC71; border-radius: 5px; color: white; padding: 2px;")
                    indicator.setGeometry(self.calendar.rect())
                    indicator.move(self.calendar.x() + 5, self.calendar.y() + 5)
                    indicator.setToolTip(f"{title}\n{description}")
                    self.event_indicators[key] = indicator

        for key, value in self.tasks.items():
            if key[0] == date:
                title, description, end_time = value
                self.task_list.addItem(f"{title} - {key[1]}")
                # Ajouter un indicateur de tâche
                if key not in self.task_indicators:
                    indicator = QFrame(self.calendar)
                    indicator.setStyleSheet("background: #E74C3C; border-radius: 5px; color: white; padding: 2px;")
                    indicator.setGeometry(self.calendar.rect())
                    indicator.move(self.calendar.x() + 5, self.calendar.y() + 5)
                    indicator.setToolTip(f"{title}\n{description}")
                    self.task_indicators[key] = indicator

        # Supprimer les indicateurs pour les dates sans événements ou tâches
        keys_to_remove = [key for key in self.event_indicators if key[0] != date]
        for key in keys_to_remove:
            self.event_indicators[key].deleteLater()
            del self.event_indicators[key]

        keys_to_remove = [key for key in self.task_indicators if key[0] != date]
        for key in keys_to_remove:
            self.task_indicators[key].deleteLater()
            del self.task_indicators[key]

    def show_event_details(self, item):
        """Afficher les détails de l'événement ou de la tâche dans une fenêtre popup."""
        event_text = item.text()
        parts = event_text.split(" - ")
        if len(parts) == 2:
            event_key = (QDateTime.fromString(f"{parts[1][:10]} {parts[1][11:]}", "yyyy-MM-dd HH:mm").date(), parts[1][11:])
            if event_key in self.events:
                title, description, end_time = self.events[event_key]
                message = f"Événement: {title}\nDescription: {description}\nHeure de fin: {end_time}"
            elif event_key in self.tasks:
                title, description, end_time = self.tasks[event_key]
                message = f"Tâche: {title}\nDescription: {description}\nHeure de fin: {end_time}"
            else:
                return

            QToolTip.showText(self.calendar.mapToGlobal(self.calendar.rect().topLeft()), message, self.calendar)
