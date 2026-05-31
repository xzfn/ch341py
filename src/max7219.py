
"""
MAX7219 SPI 8-Digit LED Display Driver. (Or as 8x8 LED grid)

Connection:
CS0 - CS
SCK - CLK
MOSI - DIN

address 0x1-0x8 for digits 0-7

BCD code (Code B)
0-9 for numbers 0-9
0xA -
0xB E
0xC H
0xD L
0xE P
0xF blank
0x80(bit-wise-or) decimal point
"""

import time

import ch341

MAX7219_BCD_MINUS = 0x0A
MAX7219_BCD_BLANK = 0x0F

MAX7219_DIGIT_0 = 0x01
MAX7219_DIGIT_BASE = MAX7219_DIGIT_0

MAX7219_DECODE_MODE = 0x09
MAX7219_INTENSITY = 0x0A
MAX7219_SCAN_LIMIT = 0x0B
MAX7219_SHUTDOWN = 0x0C
MAX7219_DISPLAY_TEST = 0x0F


def spi_write(device_index, data):
    buffer = ch341.create_ctypes_buffer(data)
    ch341.CH341StreamSPI4(device_index, 0x80 + 0b00, len(data), buffer)  # select CS0


if __name__ == '__main__':
    ch341.CH341OpenDevice(0)
    ch341.CH341SetStream(0, 0x80)  # SPI MSB first

    # NOTE all registers may be random bits at power-up, so must initialize every registers manually

    # Turn on
    spi_write(0, bytes([MAX7219_SHUTDOWN, 0x01]))  # Shutdown register, normal (turn on)

    # Set display intensity
    spi_write(0, bytes([MAX7219_INTENSITY, 0x04]))  # Intensity (0x00 - 0x0f)

    # Enable display test. All segments on
    spi_write(0, bytes([MAX7219_DISPLAY_TEST, 0x01]))  # Display Test register, on
    time.sleep(1.0)

    # Disable display test. Enter normal operation
    # NOTE Display Test must be manually cleared for normal operation (or may stuck at all-on when power up)
    spi_write(0, bytes([MAX7219_DISPLAY_TEST, 0x00]))  # Display Test register, off

    # Set scan limit
    spi_write(0, bytes([MAX7219_SCAN_LIMIT, 0xff]))  # Scan Limit (all on)
    # Set decode mode, use BCD here
    spi_write(0, bytes([MAX7219_DECODE_MODE, 0xff]))  # BCD code (all BCD)

    # Clear all 8 digits
    for i in range(8):
        spi_write(0, bytes([MAX7219_DIGIT_BASE + i, MAX7219_BCD_BLANK]))  # BCD 0x0F for blank
    time.sleep(1.0)

    # BCD minus
    for i in range(8):
        spi_write(0, bytes([MAX7219_DIGIT_BASE + i, MAX7219_BCD_MINUS]))  # BCD 0x0F for blank
    time.sleep(1.0)

    # Fill with digits
    for i in range(8):
        spi_write(0, bytes([MAX7219_DIGIT_BASE + i, i]))

    time.sleep(3.0)

    # Cycle through each digit, with flashing dot
    dot = False
    for tick in range(20):
        dot = not dot
        code = tick % 10
        if dot:
            code = (1 << 7) | code
        for i in range(8):
            spi_write(0, bytes([MAX7219_DIGIT_BASE + i, code]))

        time.sleep(0.5)

    time.sleep(1.0)

    # Shutdown
    spi_write(0, bytes([MAX7219_SHUTDOWN, 0x00]))  # Shutdown register, shutdown (turn off)

    ch341.CH341CloseDevice(0)
