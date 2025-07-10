from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusIOException

from tools.windows.warning import WarningDiolog


def check_connect(func):
    def check(client, slave_id, *args, **kwargs):
        if not client is None:
            return func(client, slave_id, *args, **kwargs)

        dlg = WarningDiolog('Устройство не подключено')
        dlg.exec()
        return None

    return check


def connect_device_tcp_ip(host: str, port: int) -> ModbusTcpClient | None:
    """Подключение устройства по IP"""
    client = ModbusTcpClient(host, port=port)
    if client.connect():
        return client

    return None


def connect_device_com_port(com: str, boundrate: int, parity: str, data_bit: int,
                            stop_bit: int) -> ModbusSerialClient | None:
    """Подключение устройства по COM порту
    :param com: COM1
    :param parity: N/E/O"""
    client = ModbusSerialClient(
        port=com,
        baudrate=boundrate,
        parity=parity,
        stopbits=stop_bit,
        bytesize=data_bit
    )
    if client.connect():
        return client

    return None


def check_id_device(client: ModbusTcpClient | ModbusSerialClient, slave_id: int):
    """Проверка того, что устройство по переданому id существует"""
    try:
        result = client.read_holding_registers(address=0, count=1, slave=slave_id)
        if result.isError():
            return False
    except ModbusIOException:
        return False

    return True

@check_connect
def set_value(client: ModbusTcpClient | ModbusSerialClient, slave_id: int, address: int, value: int):
    """Установка значения любого значения"""
    try:
        set_state = client.write_register(address - 1, value, slave=slave_id)
    except ModbusIOException:
        return None
    return set_state

@check_connect
def change_value(client: ModbusTcpClient | ModbusSerialClient, slave_id: int, address: int, value: int = 1,
                 cycle: int = 2, min_value: int = 0):
    """Добавление значения к уже существующему
    :param value: сколько нужно преибавить
    :param cycle: максимальное значение(не включительно), после которого все начнется с min_value
    :param min_value: Минимальное значение"""
    try:
        get_state = client.read_holding_registers(address=address - 1, slave=slave_id, count=1).registers
        send_value = max(min_value, (get_state[0] + value) % cycle)

        set_state = client.write_register(address - 1, send_value, slave=slave_id)
    except ModbusIOException:
        return None

    return set_state

@check_connect
def get_values_holding_register(client: ModbusTcpClient | ModbusSerialClient, slave_id: int, count_address: int, all_count: int=0):
    """Получить значение по holding registr(4x)
    :param all_count: добавляет None """
    try:
        res = client.read_holding_registers(address=0, slave=slave_id, count=count_address)
    except ModbusIOException:
        return None
    return res.registers + [None] * 10
