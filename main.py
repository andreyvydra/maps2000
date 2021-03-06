import os
import sys

import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtCore import Qt

from ui_design import Ui_MainWindow

SCREEN_SIZE = [600, 450]


def geocode(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        pass

    # Преобразуем ответ в json-объект
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    return toponym


def get_coordinates(address):
    toponym = geocode(address)
    toponym_coodrinates = toponym["Point"]["pos"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")
    return float(toponym_longitude), float(toponym_lattitude)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.pos = '30.304899,59.918068'
        self.spn = '1,1'
        self.l = 'map'
        self.pt = ''
        self.step_for_pos_change = 0.1
        self.setupUi(self)
        self.getImage()
        self.search.clicked.connect(self.get_new_image_with_search)
        self.initUI()
        self.getImage()
        self.type.activated.connect(self.change_type)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.set_new_image()

    def getImage(self):
        url = 'http://static-maps.yandex.ru/1.x/'
        params = {
            'll': self.pos,
            'spn': self.spn,
            'l': self.l
        }

        if self.pt != '':
            params['pt'] = self.pt

        response = requests.get(url, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.set_new_image()

    def get_new_image_with_search(self):
        if self.searchEdit.text() != '':
            toponym_to_find = self.searchEdit.text()
            toponym_longitude, toponym_lattitude = get_coordinates(toponym_to_find)
            ll = ",".join([str(toponym_longitude), str(toponym_lattitude)])
            self.pos = ll
            self.pt = ll
            self.getImage()
            self.set_new_image()

    def set_new_image(self):
        self.pixmap = QPixmap(self.map_file)
        self.mapImage.setPixmap(self.pixmap)

    def resize_handler(self, button: str) -> None:
        '''Handle resizing of map'''
        spn = self.spn.split(',')
        if button == '+':
            spn = list(map(lambda x: str(round(float(x) / 2, 2)), spn))
        elif button == '-':
            spn = list(map(lambda x: str(round(float(x) * 2, 2)), spn))
        if float(spn[0]) < 0:
            spn[0] = '0.01'
        if float(spn[1]) < 0:
            spn[1] = '0.01'
        self.spn = ','.join(spn)
        self.update_main_image()

    def update_main_image(self):
        self.getImage()
        self.set_new_image()

    def change_type(self):
        if self.type.currentText() == 'Схема':
            self.l = 'map'
        elif self.type.currentText() == 'Спутник':
            self.l = 'sat'
        else:
            self.l = 'skl'
        self.getImage()

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event) -> None:
        if int(event.modifiers()) == Qt.ControlModifier:
            if event.key() in [Qt.Key_Plus, Qt.Key_Equal]:
                self.resize_handler('+')
            elif event.key() == Qt.Key_Minus:
                self.resize_handler('-')

        x, y = [float(i) for i in self.pos.split(',')]
        if event.key() == Qt.Key_Up:
            y = max(y + self.step_for_pos_change, -90)
        elif event.key() == Qt.Key_Down:
            y = min(y - self.step_for_pos_change, 90)
        elif event.key() == Qt.Key_Left:
            x = max(x - self.step_for_pos_change, -90)
        elif event.key() == Qt.Key_Right:
            x = min(x + self.step_for_pos_change, 90)
        self.pos = f'{x},{y}'
        self.getImage()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
