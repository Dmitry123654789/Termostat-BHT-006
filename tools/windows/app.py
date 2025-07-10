from datetime import datetime

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow
from getmac import get_mac_address

from qt.main_wind import Ui_MainWindow
from tools.constants import DAY_WEEK, ON_OFF, HEAD_AUTO
from tools.func import *
from tools.windows.warning import WarningDiolog


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.slave = None
        self.slave_id = None
        self.count_read = 7

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
        self.pushButton_set_device.clicked.connect(self.set_device)
        self.pushButton_unset_device.clicked.connect(self.unset_device)
        self.pushButton_set_timer.clicked.connect(self.update_timer)

        self.pushButton_display.clicked.connect(self.set_display)
        self.pushButton_auto_hand.clicked.connect(self.auto_hand)
        self.pushButton_set_temp.clicked.connect(self.set_temp)
        self.pushButton_week_timer.clicked.connect(self.week_timer)
        self.pushButton_block_key.clicked.connect(self.block_key)
        self.pushButton_set_minute.clicked.connect(self.set_minute)
        self.pushButton_set_hour.clicked.connect(self.set_hour)
        self.pushButton_next_day_week.clicked.connect(self.next_day_week)
        self.pushButton_synchronize_date.clicked.connect(self.synchronize_date)

        self.pushButton_change_com_port.clicked.connect(self.change_com_port)
        self.pushButton_change_tcp_ip.clicked.connect(self.change_tcp_ip)

        self.checkBox_read_time.clicked.connect(self.read_time)

    def read_time(self):
        if self.checkBox_read_time.isChecked():
            self.count_read = 10
        else:
            self.count_read = 7

    def change_com_port(self):
        self.stackedWidget_connect_variants.setCurrentIndex(0)
        self.clean_value()

    def change_tcp_ip(self):
        self.stackedWidget_connect_variants.setCurrentIndex(1)
        self.clean_value()

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

        res_hour = set_value(self.slave, self.slave_id, 9, hour)
        res_minute = set_value(self.slave, self.slave_id, 8, minute)
        res_day_week = set_value(self.slave, self.slave_id, 10, day_week)
        self.update_labels()

    def set_minute(self):
        res = set_value(self.slave, self.slave_id, 8, int(self.lineEdit_set_minute.text()))
        self.update_labels()

    def set_hour(self):
        res = set_value(self.slave, self.slave_id, 9, int(self.lineEdit_set_hour.text()))
        self.update_labels()

    def next_day_week(self):
        res = change_value(self.slave, self.slave_id, 10, cycle=8, min_value=0)
        self.update_labels()

    def set_temp(self):
        temp = int(float(self.doubleSpinBox_set_temp.text().replace(',', '.')) * 10)
        res = set_value(self.slave, self.slave_id, 5, temp)
        self.update_labels()

    def week_timer(self):
        temp = int(float(self.doubleSpinBox_week_timer.text().replace(',', '.')) * 10)
        res = set_value(self.slave, self.slave_id, 6, temp)
        self.update_labels()

    def set_display(self):
        res = change_value(self.slave, self.slave_id, 1)
        self.update_labels()

    def auto_hand(self):
        res = change_value(self.slave, self.slave_id, 3, value=int(self.checkBox_auto_hand.isChecked()))
        self.update_labels()

    def block_key(self):
        res = change_value(self.slave, self.slave_id, 7)
        self.update_labels()

    def update_labels(self):
        if self.slave is None:
            return

        get_values = get_values_holding_register(self.slave, self.slave_id, self.count_read, 10 - self.count_read)
        if get_values is None:
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
        self.label_minut.setText(f'{get_values[7] if not get_values[7] is None else ""}')
        self.label_hour.setText(f'{get_values[8] if not get_values[8] is None else ""}')
        self.label_day_week.setText(f'{DAY_WEEK[get_values[9]]}')

    def update_timer(self):
        if self.slave is None:
            return
        self.timer.setInterval(int(self.lineEdit_update_ms.text()))

    def set_device(self):
        if self.stackedWidget_connect_variants.currentIndex() == 1:
            self.connect_device_tcp_ip()
        else:
            self.connect_device_com_port()

    def connect_device_com_port(self):
        com = f'COM{int(self.lineEdit_com_port.text())}'
        boundrate = int(self.comboBox_baunrate.currentText().split()[0])
        parity = self.comboBox_parity.currentText()[0]
        data_bit = int(self.comboBox_data_bit.currentText()[0])
        stop_bit = int(self.comboBox_stop_bit.currentText()[0])

        slave = connect_device_com_port(com, boundrate, parity, data_bit, stop_bit)
        if not slave is None:
            slave_id = int(self.lineEdit_slave_id_com.text())
            res = check_id_device(slave, slave_id)
            if res:
                self.clean_value()
                self.slave_id = slave_id
                self.slave = slave

            else:
                slave.close()
                dlg = WarningDiolog(f'Ошибка с подключением\nПроверьте правильность ID')
                dlg.exec()
        else:
            dlg = WarningDiolog(f'Ошибка с подключением\nПроверьте правильность входных данных')
            dlg.exec()

    def connect_device_tcp_ip(self):
        host = self.lineEdit_ip.text()
        port = int(self.lineEdit_port_tcp_ip.text())

        slave = connect_device_tcp_ip(host=host, port=port)
        if not slave is None:
            slave_id = int(self.lineEdit_slave_id_tcp_ip.text())
            res = check_id_device(slave, slave_id)
            if res:
                self.clean_value()
                self.slave_id = slave_id
                self.slave = slave

                host = self.slave.comm_params.host
                port = self.slave.comm_params.port
                ip_mac = get_mac_address(ip=host)
                self.label_mac_address.setText(f'MAC-адрес: {ip_mac}\tIP: {host}\tПорт: {port}')

            else:
                slave.close()
                dlg = WarningDiolog(f'Ошибка с подключением\nПроверьте правильность ID')
                dlg.exec()
        else:
            dlg = WarningDiolog(f'Ошибка с подключением\nПроверьте правильность IP и Порта')
            dlg.exec()

    def clean_value(self):
        all_fields = [self.label_display, self.label_temp, self.label_auto_hand, self.label_heat, self.label_set_temp,
                      self.label_week_timer, self.label_block_key, self.label_minut, self.label_hour,
                      self.label_day_week, self.label_mac_address]
        for field in all_fields:
            field.setText("")

        if not self.slave is None:
            self.slave.close()
        self.slave = None
        self.slave_id = None

    def closeEvent(self, event):
        self.clean_value()
        self.deleteLater()
