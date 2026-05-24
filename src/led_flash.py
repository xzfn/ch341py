"""
Flash a LED.

Connection:
CS0 - LED
(D0 and SPI-CS0 is the same pin, so D0 is fine, too.)
LED connect to a 1k resistor then to ground.

Usage:
python led_flash.py
You should see the led flashing.
"""


import time
import ch341


if __name__ == '__main__':
    ch341.CH341OpenDevice(0)

    while True:
        # D0 dir output. D0 output 1
        ch341.CH341Set_D5_D0(0, 0x01, 0x01)
        time.sleep(0.5)
        # D0 dir output. D0 output 0
        ch341.CH341Set_D5_D0(0, 0x01, 0x00)
        time.sleep(0.5)

    # may need to reset the pins back to input
    ch341.CH341Set_D5_D0(0, 0x00, 0x00)
    ch341.CH341CloseDevice(0)
