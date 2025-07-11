import sys

from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication

from tools.windows.app import MainWindow


class App(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.translator = QTranslator()

        # Загружаем перевод по умолчанию
        self.load_translation('en')

        self.main_window = MainWindow(self)
        self.main_window.show()

    def load_translation(self, lang):
        """Загружает перевод из файла"""
        if lang == 'ru':
            self.translator.load('')
        else:
            self.translator.load('translations/ru-eng.qm')

        self.installTranslator(self.translator)

if __name__ == '__main__':
    app = App(sys.argv)
    sys.exit(app.exec())
