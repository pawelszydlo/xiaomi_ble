# python3
"""Library for Bluetooth LE operations."""

import logging
from threading import Lock
from typing import Callable

from bluepy import btle

NotificationHandlerType = Callable[[int, bytes], None]

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)

_DATA_MODE_LISTEN = bytes([0x01, 0x00])
ADDR_TYPE_PUBLIC = btle.ADDR_TYPE_PUBLIC
ADDR_TYPE_RANDOM = btle.ADDR_TYPE_RANDOM


def _discovery_handler(dev, id_new_dev, is_new_data):
    """Handler of discovered devices."""
    if id_new_dev:
        LOGGER.info("Discovered device: %s (RSSI=%d dB, %s%s)",
                    dev.addr, dev.rssi, dev.addrType,
                    ", connectable" if dev.connectable else "")
    elif is_new_data:
        pass  # logger.info("Received new data from: %s", dev.addr)


def scan_for_devices(timeout: int = 10):
    """Scan for nearby Bluetooth LE devices. Might require root."""
    LOGGER.info("Scanning for devices...")
    # Create a scanner delegate and override the handler.
    delegate = btle.DefaultDelegate()
    delegate.handleNotification = _discovery_handler
    scanner = btle.Scanner().withDelegate(delegate)
    # Perform the scan.
    devices = scanner.scan(timeout)
    LOGGER.info("Found %d devices.", len(devices))
    return devices


class Device:
    """Class representing a BTLE device.


    Can be used as a context:

        with Device(mac) as device:
            ...

    or traditionally:

        device = Device(mac)
        device.connect()
        ...
        device.disconnect()
    """
    _lock = Lock()

    def __init__(self, mac: str, timeout: int = 30,
                 addr_type: int = ADDR_TYPE_PUBLIC):
        self._mac = mac
        self._timeout = timeout
        self._addr_type = addr_type
        self._peripheral = None

    def __enter__(self) -> "Device":
        self._lock.acquire()
        try:
            self.connect()
        except:
            self._lock.release()
            raise
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._lock.release()
        self.disconnect()

    def connect(self):
        """Connect to the device."""
        LOGGER.debug("Connecting to %s...", self._mac)
        self._peripheral = btle.Peripheral(self._mac, addrType=self._addr_type)

    def disconnect(self):
        """Disconnect from device."""
        if self._peripheral is None:
            return
        LOGGER.debug("Disconnecting from %s...", self._mac)
        self._peripheral.disconnect()
        self._peripheral = None

    def read_handle(self, handle: int) -> bytes:
        """Will read a characteristic described by the given handle."""
        return self._peripheral.readCharacteristic(handle)

    def write_handle(self, handle: int, value: bytes):
        """Will send the value as a characteristic described by handle."""
        return self._peripheral.writeCharacteristic(handle, value, True)

    def wait_for_notification(self,
                              handle: int,
                              handler_function: NotificationHandlerType
                              ) -> bool:
        """Will wait for a notification from the device to a given handle."""
        LOGGER.debug(
            "Will wait %d seconds for data from %s...", self._timeout,
            self._mac)

        delegate = btle.DefaultDelegate()
        delegate.handleNotification = handler_function
        self._peripheral.withDelegate(delegate)

        self.write_handle(handle, _DATA_MODE_LISTEN)
        try:
            return self._peripheral.waitForNotifications(self._timeout)
        except btle.BTLEException as exc:
            logging.error("Couldn't receive data: %s", exc)
            return False
