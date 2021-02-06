import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.spn = '1,1'
        self.getImage()
        self.initUI()

    def keyPressEvent(self, event) -> None:
        if int(event.modifiers()) == Qt.ControlModifier:
            if event.key() in [Qt.Key_Plus, Qt.Key_Equal]:
                self.resize_handler('+')
            elif event.key() == Qt.Key_Minus:
                self.resize_handler('-')

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
        self.pixmap = QPixmap(self.map_file)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll=30.304899,59.918068&spn={self.spn}&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        # Изображение
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
