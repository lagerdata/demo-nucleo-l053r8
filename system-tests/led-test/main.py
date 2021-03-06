# pylint: disable=redefined-outer-name,missing-function-docstring

import sys
import time
import pytest
import serial
import pigpio
from lager import lager


LED_PIN = 0

@pytest.fixture
def serial_port():
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser:
        yield ser

@pytest.fixture(scope='module')
def gateway():
    gw = lager.Lager()
    gw.gpio.set_mode(LED_PIN, pigpio.INPUT)
    yield gw
    gw.close()

@pytest.fixture(scope='module')
def device(gateway):
    device = gateway.connect("stm32l0", interface="stlink", transport="hla_swd", speed="480", force=True)
    device.reset(halt=True)
    hexfiles = [lager.Hexfile("demo-nucleo-l053r8.hex")]
    device.flash(hexfiles=hexfiles)
    yield device
    device.close()

def test_led_on(gateway, device, serial_port):
    device.run()
    serial_port.write(b'l')
    time.sleep(0.1)
    data = serial_port.read(32)
    led_state = gateway.gpio.read(LED_PIN)
    assert led_state == 1

def test_led_off(gateway, device, serial_port):
    device.run()
    serial_port.write(b'k')
    time.sleep(0.1)
    data = serial_port.read(32)
    led_state = gateway.gpio.read(LED_PIN)
    assert led_state == 0

if __name__ == '__main__':
    sys.exit(pytest.main([__file__]))
