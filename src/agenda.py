from PyQt6.QtWidgets import (
    QPushButton, QWidget, QVBoxLayout, QLabel, QHBoxLayout,
    QCalendarWidget, QListWidget, QInputDialog, QMessageBox,
    QDateTimeEdit, QDialog, QFormLayout, QLineEdit, QDialogButtonBox,
    QMenu, QTextEdit, QGridLayout, QApplication, QFrame, QToolTip
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QDateTime, QDate
import os
import django
from django.core.wsgi import get_wsgi_application
from django.utils import timezone
from agenda.models import Event, Task
import datetime

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'virtualfs.settings')
application = get_wsgi_application()

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
        parent_window = self.window()

        if not hasattr(parent_window, "open_windows"):
            parent_window.open_windows = []

        if hasattr(parent_window, 'agenda_window') and parent_window.agenda_window.isVisible():
            parent_window.agenda_window.close()
        else:
            agenda = AgendaWindow(parent_window)
            parent_window.agenda_window = agenda
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
        self.close_button.setStyleSheet("""
            CloseButton {
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
        self.load_events_from_db()
        self.load_tasks_from_db()

        # Variables pour le déplacement de la fenêtre
        self._drag_start_position = None
        self._drag_offset = None

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

        # Champs pour le titre et la description
        title_field = QLineEdit(dialog)
        description_field = QTextEdit(dialog)

        # Champ pour la date et heure de début (uniquement pour les événements)
        start_datetime = QDateTimeEdit(dialog) if not is_task else None
        if start_datetime:
            start_datetime.setDateTime(QDateTime.currentDateTime())
            start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
            start_datetime.setCalendarPopup(True)
            dialog.layout().addRow("Date et heure de début:", start_datetime)

        # Champ pour la date et heure de fin (uniquement pour les événements)
        end_datetime = QDateTimeEdit(dialog) if not is_task else None
        if end_datetime:
            end_datetime.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # 1 heure après
            end_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
            end_datetime.setCalendarPopup(True)
            dialog.layout().addRow("Date et heure de fin:", end_datetime)

        dialog.layout().addRow("Titre:", title_field)
        dialog.layout().addRow("Description:", description_field)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, dialog)
        dialog.layout().addWidget(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if event_to_edit:
            title_field.setText(event_to_edit.title)
            description_field.setText(event_to_edit.description)
            if start_datetime:
                start_datetime.setDateTime(event_to_edit.start_time)
            if end_datetime:
                end_datetime.setDateTime(event_to_edit.end_time)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title = title_field.text()
            description = description_field.toPlainText()

            if is_task:
                due_date = self.calendar.selectedDate().toPyDate()
                if event_to_edit:
                    event_to_edit.title = title
                    event_to_edit.description = description
                    event_to_edit.due_date = timezone.make_aware(datetime.datetime.combine(due_date, datetime.time.min))
                else:
                    task = Task(title=title, description=description, due_date=timezone.make_aware(datetime.datetime.combine(due_date, datetime.time.min)), user=django.contrib.auth.models.User.objects.first())
                    task.save()
            else:
                start_time = timezone.make_aware(datetime.datetime(
                    start_datetime.date().year(),
                    start_datetime.date().month(),
                    start_datetime.date().day(),
                    start_datetime.time().hour(),
                    start_datetime.time().minute()
                ))

                end_time = timezone.make_aware(datetime.datetime(
                    end_datetime.date().year(),
                    end_datetime.date().month(),
                    end_datetime.date().day(),
                    end_datetime.time().hour(),
                    end_datetime.time().minute()
                ))

                if start_time >= timezone.now() and end_time > start_time:
                    if event_to_edit:
                        event_to_edit.title = title
                        event_to_edit.description = description
                        event_to_edit.start_time = start_time
                        event_to_edit.end_time = end_time
                    else:
                        event = Event(title=title, description=description, start_time=start_time, end_time=end_time, user=django.contrib.auth.models.User.objects.first())
                        event.save()
                    event_to_edit.save()

            self.show_events_for_date(self.calendar.selectedDate())

    def modify_event(self):
        """Modifier l'événement ou la tâche sélectionné(e)."""
        selected_items = self.event_list.selectedItems()
        if not selected_items:
            selected_items = self.task_list.selectedItems()
        if selected_items:
            event_text = selected_items[0].text()
            parts = event_text.split(" - ")
            if len(parts) == 3:
                # Extraction de l'identifiant numérique
                event_id = parts[0]  # Prendre la première partie de la chaîne comme identifiant
                is_task = bool(self.task_list.selectedItems())
                if is_task:
                    event_to_edit = Task.objects.get(id=event_id)
                else:
                    event_to_edit = Event.objects.get(id=event_id)
                self.open_event_dialog(is_task=is_task, event_to_edit=event_to_edit)

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
                if len(parts) == 3:
                    event_id = parts[0]  # Prendre la première partie de la chaîne comme identifiant
                    if bool(self.task_list.selectedItems()):
                        task = Task.objects.get(id=event_id)
                        task.delete()
                    else:
                        event = Event.objects.get(id=event_id)
                        event.delete()
                    # Supprimer l'élément de la liste
                    if self.event_list.selectedItems():
                        self.event_list.takeItem(self.event_list.row(item))
                    else:
                        self.task_list.takeItem(self.task_list.row(item))
                    # Supprimer l'indicateur d'événement ou de tâche
                    if event_id in self.event_indicators:
                        self.event_indicators[event_id].deleteLater()
                        del self.event_indicators[event_id]
                    elif event_id in self.task_indicators:
                        self.task_indicators[event_id].deleteLater()
                        del self.task_indicators[event_id]

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

        # Convertir QDate en datetime.date
        date = date.toPyDate()

        events = Event.objects.filter(start_time__date=date)
        for event in events:
            self.event_list.addItem(f"{event.id} - {event.title} - {event.start_time.strftime('%Y-%m-%d %H:%M')}")

        tasks = Task.objects.filter(due_date=date)
        for task in tasks:
            self.task_list.addItem(f"{task.id} - {task.title} - {task.due_date.strftime('%Y-%m-%d %H:%M')}")

    def show_event_details(self, item):
        """Afficher les détails de l'événement ou de la tâche dans une fenêtre popup."""
        event_text = item.text()
        parts = event_text.split(" - ")
        if len(parts) == 3:
            event_id = parts[0]  # Prendre la première partie de la chaîne comme identifiant
            if event_id in self.events:
                event = self.events[event_id]
                message = f"Événement: {event.title}\nDescription: {event.description}\nHeure de fin: {event.end_time.strftime('%H:%M')}"
            elif event_id in self.tasks:
                task = self.tasks[event_id]
                message = f"Tâche: {task.title}\nDescription: {task.description}"
            else:
                return

            QToolTip.showText(self.calendar.mapToGlobal(self.calendar.rect().topLeft()), message, self.calendar)

    def load_events_from_db(self):
        """Charge les événements depuis la base de données."""
        events = Event.objects.all()
        for event in events:
            self.events[event.id] = event  # Utiliser l'identifiant unique

    def load_tasks_from_db(self):
        """Charge les tâches depuis la base de données."""
        tasks = Task.objects.all()
        for task in tasks:
            self.tasks[task.id] = task  # Utiliser l'identifiant unique

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

    def closeEvent(self, event):
        """Ferme la connexion à la base de données lorsque la fenêtre est fermée."""
        django.db.connections.close_all()
        super().closeEvent(event)
