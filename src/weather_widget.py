from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer
import requests
from io import BytesIO

def get_weather(city="Paris"):
    api_key = "3b5fa5e0bfd43e2194bc21fd65a364c6"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=fr"

    response = requests.get(url)

    # Logs pour le debug
    print(f"URL appelée : {url}")
    print(f"Status Code : {response.status_code}")
    print(f"Réponse complète : {response.text}")

    if response.status_code == 200:
        data = response.json()
        return {
            "temp": data['main']['temp'],
            "description": data['weather'][0]['description'],
            "icon": data['weather'][0]['icon']
        }
    return None


class WeatherWidget(QWidget):
    def __init__(self, city="Paris"):
        super().__init__()

        self.city = city
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.layout = QVBoxLayout()
        self.label_temp = QLabel("Température: --°C")
        self.label_desc = QLabel("Conditions: --")
        self.label_icon = QLabel()

        self.layout.addWidget(self.label_temp)
        self.layout.addWidget(self.label_desc)
        self.layout.addWidget(self.label_icon)

        self.setLayout(self.layout)
        self.update_weather()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(1800000)

    def update_weather(self):
        weather = get_weather(self.city)
        if weather:
            self.label_temp.setText(f"Température: {weather['temp']}°C")
            self.label_desc.setText(f"Conditions: {weather['description']}")

            icon_url = f"http://openweathermap.org/img/wn/{weather['icon']}@2x.png"
            icon_data = requests.get(icon_url).content
            pixmap = QPixmap()
            pixmap.loadFromData(BytesIO(icon_data).read())
            self.label_icon.setPixmap(pixmap)

            self.adjustSize()