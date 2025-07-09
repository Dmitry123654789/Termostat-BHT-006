from datetime import datetime

import modbus_tk.defines as cst
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow
from getmac import get_mac_address
from modbus_tk import modbus_tcp

from qt.wind import Ui_MainWindow
from tools.constants import DAY_WEEK, ON_OFF, HEAD_AUTO
from tools.func import set_time, change_value, change_teperature_value
from tools.windows.warning import WarningDiolog


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.host = None
        self.port = None
        self.slave = None
        self.slave_id = None

        self.timer = QTimer(self)
        self.timer_bulb = QTimer(self)

        self.create_timers()

        self.buttons_connect()

    def create_timers(self):
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_labels)
        self.timer.start()

        self.timer_bulb.setInterval(150)
        self.timer_bulb.timeout.connect(self.update_bulb_gray)

    def buttons_connect(self):
        self.pushButton_set_timer.clicked.connect(self.update_timer)
        self.pushButton_set_device.clicked.connect(self.set_device)
        self.pushButton_display.clicked.connect(self.set_display)
        self.pushButton_auto_hand.clicked.connect(self.auto_hand)
        self.pushButton_set_temp.clicked.connect(self.set_temp)
        self.pushButton_week_timer.clicked.connect(self.week_timer)
        self.pushButton_block_key.clicked.connect(self.block_key)
        self.pushButton_set_minute.clicked.connect(self.set_minute)
        self.pushButton_set_hour.clicked.connect(self.set_hour)
        self.pushButton_next_day_week.clicked.connect(self.next_day_week)
        self.pushButton_synchronize_date.clicked.connect(self.synchronize_date)
        self.pushButton_unset_device.clicked.connect(self.unset_device)

    def update_bulb(self):
        self.pushButton_upload.setStyleSheet('''QPushButton{
            background-color: rgb(0, 255, 0);
            color: rgb(3, 3, 3);
            border: 2px solid rgb(126, 126, 126);
            border-radius: 8px
        }
        ''')
        self.timer_bulb.start()

    def update_bulb_gray(self):
        self.pushButton_upload.setStyleSheet('''QPushButton{
        	background-color: rgb(227, 227, 227);
        	color: rgb(3, 3, 3);
        	border: 2px solid rgb(126, 126, 126);
        	border-radius: 8px
        }
        ''')
        self.timer_bulb.stop()

    def unset_device(self):
        self.clean_value()

    def synchronize_date(self):
        now = datetime.now()
        hour, minute, day_week = now.hour, now.minute, now.weekday() + 1

        res_hour = set_time(self.slave, self.slave_id, 9, hour)
        if not res_hour is None:
            res_minute = set_time(self.slave, self.slave_id, 8, minute)
            res_day_week = set_time(self.slave, self.slave_id, 10, day_week)

            self.label_hour.setText(f'{res_hour if not res_hour is None else ""}')
            self.label_minut.setText(f'{res_minute if not res_minute is None else ""}')
            self.label_day_week.setText(f'{DAY_WEEK[res_day_week]}')

    def set_minute(self):
        res = set_time(self.slave, self.slave_id, 8, int(self.lineEdit_set_minute.text()))
        self.label_minut.setText(f'{res if not res is None else ""}')

    def set_hour(self):
        res = set_time(self.slave, self.slave_id, 9, int(self.lineEdit_set_hour.text()))
        self.label_hour.setText(f'{res if not res is None else ""}')

    def next_day_week(self):
        res = change_value(self.slave, self.slave_id, 10, cycle=8, del_zero=True)
        self.label_day_week.setText(f'{DAY_WEEK[res]}')

    def set_temp(self):
        temp = float(self.doubleSpinBox_set_temp.text().replace(',', '.'))
        res = change_teperature_value(self.slave, self.slave_id, 5, temp)
        self.label_set_temp.setText(f'{(res / 10) if not res is None else ""} °C')

    def week_timer(self):
        temp = float(self.doubleSpinBox_week_timer.text().replace(',', '.'))
        res = change_teperature_value(self.slave, self.slave_id, 6, temp)
        self.label_week_timer.setText(f'{(res / 10) if not res is None else ""} °C')

    def set_display(self):
        res = change_value(self.slave, self.slave_id, 1)
        self.label_display.setText(f'{ON_OFF[res]}')

    def auto_hand(self):
        res = change_value(self.slave, self.slave_id, 3, value=0)
        self.label_auto_hand.setText(f'{HEAD_AUTO[res]}')

    def block_key(self):
        res = change_value(self.slave, self.slave_id, 7)
        self.label_block_key.setText(f'{ON_OFF[res]}')

    def update_labels(self):
        if self.slave is None:
            return
        try:
            get_values = self.slave.execute(self.slave_id, cst.READ_HOLDING_REGISTERS, 0, 10)
        except TimeoutError:
            dlg = WarningDiolog('Устройство не подключено')
            dlg.exec()
            self.clean_value()
            return
        except ConnectionResetError:
            dlg = WarningDiolog('Устройство не подключено\nУдаленный хост принудительно разорвал существующее подключение')
            dlg.exec()
            self.clean_value()
            return

        self.update_bulb()

        self.label_display.setText(f'{ON_OFF[get_values[0]]}')
        self.label_temp.setText(f'{get_values[1] / 10} °C')
        self.label_auto_hand.setText(f'{HEAD_AUTO[get_values[2]]}')
        self.label_heat.setText(f'{ON_OFF[get_values[3]]}')
        self.label_set_temp.setText(f'{get_values[4] / 10} °C')
        self.label_week_timer.setText(f'{get_values[5] / 10} °C')
        self.label_block_key.setText(f'{ON_OFF[get_values[6]]}')
        self.label_minut.setText(f'{get_values[7]}')
        self.label_hour.setText(f'{get_values[8]}')
        self.label_day_week.setText(f'{DAY_WEEK[get_values[9]]}')

    def update_timer(self):
        if self.slave is None:
            return
        self.timer.setInterval(int(self.lineEdit_update_ms.text()))
        self.slave.set_timeout(int(self.lineEdit_update_ms.text()))

    def set_device(self):
        host = self.lineEdit_ip.text()
        port = int(self.lineEdit_port.text())

        self.slave = modbus_tcp.TcpMaster(host=host, port=port)
        self.slave.set_timeout(int(self.lineEdit_update_ms.text()) / 1000)

        try:
            slave_id = int(self.lineEdit_slave_id.text())

            self.slave.execute(slave_id, cst.READ_HOLDING_REGISTERS, 0, 1)

            self.host = host
            self.port = port
            self.slave_id = slave_id

            ip_mac = get_mac_address(ip=self.host)
            self.label_mac_address.setText(f'MAC-адрес: {ip_mac}\tIP: {self.host}\tПорт: {self.port}')
        except Exception as e:
            if self.host and self.host:
                self.slave = modbus_tcp.TcpMaster(host=self.host, port=self.port)
                self.slave.set_timeout(int(self.lineEdit_update_ms.text()) / 1000)
            else:
                self.slave = None


            dlg = WarningDiolog(f'Ошибка с подключением\nПроверьте правильность IP и Порта')
            dlg.exec()

    def clean_value(self):
        self.label_display.setText('')
        self.label_temp.setText('')
        self.label_auto_hand.setText('')
        self.label_heat.setText('')
        self.label_set_temp.setText('')
        self.label_week_timer.setText('')
        self.label_block_key.setText('')
        self.label_minut.setText('')
        self.label_hour.setText('')
        self.label_day_week.setText('')

        self.host = None
        self.port = None
        self.slave = None
        self.slave_id = None

        self.label_mac_address.setText('MAC-адрес: ')

    def closeEvent(self, event):
        self.deleteLater()
