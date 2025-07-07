from PyQt6 import QtGui
from PyQt6.QtWidgets import QApplication, QStyle, QDialog, QDialogButtonBox, QVBoxLayout, QLabel


class WarningDiolog(QDialog):
    def __init__(self, text='Что то пошло не так'):
        super().__init__()

        self.setWindowTitle("ERROR")
        warning_icon = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
        self.setWindowIcon(warning_icon)

        buttons = (
            QDialogButtonBox.StandardButton.Cancel
        )

        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(13)

        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        layout = QVBoxLayout()
        message = QLabel(text)
        message.setFont(font)
        layout.addWidget(message)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
