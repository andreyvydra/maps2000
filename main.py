import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow
from PyQt5.QtCore import Qt
from ui_design import Ui_MainWindow

SCREEN_SIZE = [600, 450]


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.spn = '1,1'
        self.getImage()
        self.initUI()

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
        self.mapImage.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Up:
            self.resize_handler('+')
        elif event.key() == Qt.Key_Down:
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
        self.mapImage.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
