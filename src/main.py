import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import requests

from src.taskbar import TaskBar

# Remplace par ta vraie clé MétéoConcept
METEOCONCEPT_API_KEY = "6c0ee281f63a1d2e57da3f9ab4ddbdcf33122bbb915e5a8cf29f9b81799082c8"


def get_city_insee(city, api_key):
    """
    Recherche l'ID INSEE d'une ville via l'API MétéoConcept.
    Prend la ville exacte si possible, sinon la première correspondance.
    """
    location_url = f"https://api.meteo-concept.com/api/location/cities?token={api_key}&search={city}"
    response = requests.get(location_url)

    if response.status_code != 200:
        print(f"❌ Erreur localisation : {response.text}")
        return None

    cities = response.json().get('cities', [])
    if not cities:
        print(f"❌ Aucune ville trouvée pour '{city}'")
        return None

    for city_data in cities:
        if city_data['name'].lower() == city.lower():
            return city_data['insee']

    print(f"⚠️ Ville exacte non trouvée, utilisation de : {cities[0]['name']}")
    return cities[0]['insee']


def get_weather_from_meteoconcept(city="Paris"):
    """
    Récupère la météo actuelle (prévision jour 0) via MétéoConcept.
    """
    city_id = get_city_insee(city, METEOCONCEPT_API_KEY)
    if not city_id:
        return None

    # Utilisation de l'endpoint /forecast/daily (plus fiable sur le plan gratuit)
    weather_url = f"https://api.meteo-concept.com/api/forecast/daily?token={METEOCONCEPT_API_KEY}&insee={city_id}"
    response = requests.get(weather_url)

    if response.status_code != 200:
        print(f"❌ Erreur météo : {response.text}")
        return None

    data = response.json()['forecast'][0]  # Jour actuel (jour 0)

    return {
        "temp_min": data['tmin'],
        "temp_max": data['tmax'],
        "description": "Prévisions du jour"
    }


class BureauVirtuel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bureau Virtuel")
        self.setGeometry(100, 100, 1080, 720)
        self.setMinimumSize(1080, 720)

        # Fond d'écran
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_pixmap = QPixmap(os.path.join("assets", "background.jpg"))
        self.update_background()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.taskbar = TaskBar(self)
        self.open_windows = []

        # ✅ Ajouter le QLabel pour la météo
        self.weather_label = QLabel(self)
        self.weather_label.setStyleSheet("color: white; font-size: 14px;")
        self.weather_label.setGeometry(10, 50, 250, 100)

        # Mise à jour toutes les 30 minutes
        self.update_weather()
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(1800000)

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

    def update_weather(self):
        weather = get_weather_from_meteoconcept("Lille")
        if weather:
            self.weather_label.setText(
                f"🌡️ Min: {weather['temp_min']}°C / Max: {weather['temp_max']}°C\n{weather['description']}"
            )
        else:
            self.weather_label.setText("Météo indisponible")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BureauVirtuel()
    window.show()
    sys.exit(app.exec())