from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException

from tools.windows.warning import WarningDiolog


def check_connect(func):
    def check(client, slave_id, *args, **kwargs):
        try:
            res = client.read_holding_registers(address=0, slave=slave_id, count=1)
            return func(client, slave_id, *args, **kwargs)
        except ModbusIOException:
            dlg = WarningDiolog('Устройство не подключено')
            dlg.exec()
            return None

    return check


def connect_device_tcp_ip(host: str, port: int) -> ModbusTcpClient | None:
    client = ModbusTcpClient(host, port=port)

    if client.connect():
        return client

    return None

def check_id_device(client: ModbusTcpClient, slave_id):
    try:
        result = client.read_holding_registers(address=0, count=1, slave=slave_id)
        if result.isError():
            return False
    except ModbusIOException:
        return False

    return True


@check_connect
def set_time(client: ModbusTcpClient, slave_id, address, value):
    set_state_display = client.write_register(address - 1, value, slave=slave_id)


@check_connect
def change_value(client: ModbusTcpClient, slave_id, address, value=1, cycle=2, del_zero=False):
    get_state = client.read_holding_registers(address=address - 1, slave=slave_id, count=1).registers
    send_value = ((get_state[0] + value) % cycle) if not del_zero else max(1, (get_state[0] + value) % cycle)

    set_state_display = client.write_register(address - 1, send_value, slave=slave_id)


@check_connect
def change_teperature_value(client: ModbusTcpClient, slave_id, address, value):
    set_state_display = client.write_register(address - 1, int(value * 10), slave=slave_id)

@check_connect
def get_values_holding_register(client: ModbusTcpClient, slave_id: int, count_address: int):
    res = client.read_holding_registers(address=0, slave=slave_id, count=count_address)

    return res.registers
