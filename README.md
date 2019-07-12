# xiaomi_ble
Python library for reading data from Xiaomi temperature and humidity sensor, through Bluetooth LE.

#### Supported devices:
- Xiaomi Mi bluetooth temperature and humidity sensor (duh)


#### Example usage:
```Python
from xiaomi_ble import TemperatureHumiditySensor

sensor = xiaomi.TemperatureHumiditySensor("58:2D:34:31:XX:XX")
print(sensor.temperature, sensor.humidity, sensor.battery)
```