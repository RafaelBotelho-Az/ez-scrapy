import sys
from PySide6 import QtWidgets
from app import MyWidget

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationName('Ez - Scrapy')

    try:
        with open("resources/styles.qss", "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        print("Arquivo styles.qss não encontrado. O layout será exibido sem estilos.")

    widget = MyWidget()
    widget.setFixedSize(700, 350)
    widget.show()

    sys.exit(app.exec())