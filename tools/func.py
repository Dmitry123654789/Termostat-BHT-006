import modbus_tk.defines as cst

from tools.windows.warning import WarningDiolog


def check_connect(func):
    def check(slave, slave_id, *args, **kwargs):
        try:
            slave.execute(slave_id, cst.READ_HOLDING_REGISTERS, 0, 1)
            return func(slave, slave_id, *args, **kwargs)
        except AttributeError as e:
            dlg = WarningDiolog('Устройство не подключено')
            dlg.exec()
            return None

    return check


@check_connect
def set_time(slave, slave_id, address, value):
    set_state_display = slave.execute(slave_id, cst.WRITE_SINGLE_REGISTER, address - 1, 1, output_value=value)
    return set_state_display[1]


@check_connect
def change_value(slave, slave_id, address, value=1, cycle=2, del_zero=False):
    get_state = slave.execute(slave_id, cst.READ_HOLDING_REGISTERS, address - 1, 1)
    set_state = slave.execute(slave_id, cst.WRITE_SINGLE_REGISTER, address - 1, 1,
                              output_value=((get_state[0] + value) % cycle) if not del_zero else max(1, (
                                      get_state[0] + value) % cycle))
    return set_state[1]


@check_connect
def change_teperature_value(slave, slave_id, address, value):
    set_state = slave.execute(slave_id, cst.WRITE_SINGLE_REGISTER, address - 1, 1,
                              output_value=int(value * 10))
    return set_state[1]
