import sys

from PyQt6.QtWidgets import QApplication

from tools.windows.app import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
