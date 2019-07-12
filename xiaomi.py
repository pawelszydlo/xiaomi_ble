# python3
"""Library for operating on Xiaomi smart home devices data."""

import ble

_HANDLE_SENSOR_DATA = 0x0010
_HANDLE_BATTERY_LEVEL = 0x0018


def _temp_sensor_parse_data(data: str) -> (float, float):
    """Extracts information from the data returned by the sensor."""
    temperature = float(data[2:6])
    humidity = float(data[9:13])
    return temperature, humidity


class TemperatureHumiditySensor:
    """Xiaomi bluetooth temperature and humidity sensor."""

    def __init__(self, mac: str, timeout: int = 30):
        self._mac = mac
        self._timeout = timeout
        self._temperature = 0.0
        self._humidity = 0.0
        self._battery = 0
        self._read_data()

    def _temp_sensor_data_handler(self, handle: int, data: bytes):
        """Handler for temp sensor notifications."""
        del handle
        self._temperature, self._humidity = _temp_sensor_parse_data(data)

    def _read_data(self):
        with ble.Device(self._mac, self._timeout) as device:
            battery_data = device.read_handle(_HANDLE_BATTERY_LEVEL)
            if battery_data:
                self._battery = int(ord(battery_data))
            device.wait_for_notification(
                _HANDLE_SENSOR_DATA, self._temp_sensor_data_handler)

    @property
    def battery(self) -> int:
        """Batter state, 0-100."""
        return self._battery

    @property
    def temperature(self) -> float:
        """Temperature."""
        return self._temperature

    @property
    def humidity(self):
        """Humidity (percent)."""
        return self._humidity
