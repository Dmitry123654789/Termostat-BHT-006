import modbus_tk.defines as cst

from tools.windows.warning import WarningDiolog


def check_connect(func):
    def check(slave, *args, **kwargs):
        try:
            slave.execute(1, cst.READ_HOLDING_REGISTERS, 0, 1)
            return func(slave, *args, **kwargs)
        except AttributeError as e:
            dlg = WarningDiolog('Устройство не подключено')
            dlg.exec()
            return None

    return check


@check_connect
def set_time(slave, address, value):
    set_state_display = slave.execute(1, cst.WRITE_SINGLE_REGISTER, address - 1, 1, output_value=value)
    return set_state_display[1]


@check_connect
def change_value(slave, address, value=1, cycle=2, del_zero=False):
    get_state = slave.execute(1, cst.READ_HOLDING_REGISTERS, address - 1, 1)[0]
    set_state = slave.execute(1, cst.WRITE_SINGLE_REGISTER, address - 1, 1,
                              output_value=((get_state + value) % cycle) if not del_zero else max(1, (
                                      get_state + value) % cycle))
    return set_state[1]


@check_connect
def change_teperature_value(slave, address, value):
    set_state = slave.execute(1, cst.WRITE_SINGLE_REGISTER, address - 1, 1,
                              output_value=int(value * 10))
    return set_state[1]
