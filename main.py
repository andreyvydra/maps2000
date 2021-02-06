import os
import sys

from PyQt5.QtCore import Qt
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from ui_design import Ui_MainWindow

SCREEN_SIZE = [600, 450]

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.pos = '30.304899,59.918068'
        self.spn = '1,1'
        self.l = 'map'
        self.step_for_pos_change = 0.1
        self.initUI()
        self.getImage()

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.pos}&spn={self.spn}&l={self.l}"
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
        self.set_image()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')

        ## Изображение
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)

    def set_image(self):
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)

    def keyPressEvent(self, event):
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