"""
LCD1602
AIP31068L 1602 LCD driver

Connection:
SDL - SCK
SDA - SDA
GND - GND
5.0V - VCC  (May need external 5.0V power)
GND - 10k Variable Resistor - V0  (May start with GND and V0 connected directly)

"""


import time

import ch341

# Control Byte controlling Co bit and RS bit similar to ssd1306
# Control Byte RS bit
CONTROL_COMMAND = 0b00000000
CONTROL_DATA = 0b01000000


def cgram_build_bar(col):
    b = (0b11111 << (4 - col)) & 0b11111
    return b.to_bytes() * 8


CGRAM_BARS = [
    cgram_build_bar(col) for col in range(5)
]


def clear_display(addr):
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b00000001]))  # clear display


def display_string(addr, row, col, s):
    if row > 1:
        row = 1
    ddram_addr = 0b10000000 + (40 * row + col)
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, ddram_addr]))  # set DDRAM address
    max_count = 16 - col
    s_data = s.encode('ascii')
    if len(s_data) > max_count:
        s_data = s_data[0:max_count]
    ch341.i2c_write(0, bytes([addr, CONTROL_DATA]) + s_data)


if __name__ == '__main__':
    ch341.CH341OpenDevice(0)
    ch341.CH341SetStream(0, 0x00)  # I2C speed: bit1-0 00(20k) 01(100k) 10(400k) 11(750k)

    addr = 0b0111110 << 1  # addr left shift 1 (make room for r/w bit)

    print('i2c addr valid:', ch341.i2c_check_addr_ack(0, addr))

    # datasheet: INITIALIZING BY INSTRUCTION
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b00101000]))  # function set (2-line mode, display on)
    # delay 39us
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b00001100]))  # display on/off control (display on, cursor off, blink off)
    # delay 39us
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b00000001]))  # clear display
    # delay 1.53ms
    time.sleep(1.53e-3)
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b00000110]))  # entry mode set (moving right, screen shift off)

    # the CONTROL_COMMAND or CONTROL_DATA after addr is Control Byte

    # simple display
    # line1: !AB
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b10000000]))  # set DDRAM address
    ch341.i2c_write(0, bytes([addr, CONTROL_DATA, ord('!')]))  # write data
    ch341.i2c_write(0, bytes([addr, CONTROL_DATA, ord('A')]))  # write data
    ch341.i2c_write(0, bytes([addr, CONTROL_DATA, ord('B')]))  # write data
    # line2: %01
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b10000000 + 40]))  # set DDRAM address
    ch341.i2c_write(0, bytes([addr, CONTROL_DATA, ord('%')]))  # write data
    ch341.i2c_write(0, bytes([addr, CONTROL_DATA, ord('0')]))  # write data
    ch341.i2c_write(0, bytes([addr, CONTROL_DATA, ord('1')]))  # write data

    time.sleep(2.0)

    # line1: 0123...
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b10000000]))  # set DDRAM address
    for i in range(16):
        ch341.i2c_write(0, bytes([addr, CONTROL_DATA, ord('0') + i]))
    # line2: ABCD...
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b10000000 + 40]))  # set DDRAM address
    for i in range(16):
        ch341.i2c_write(0, bytes([addr, CONTROL_DATA, ord('A') + i]))

    time.sleep(2.0)

    # display off
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b00001000]))
    time.sleep(2.0)
    # display on
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b00001100]))

    # write CGRAM
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b01000000]))  # set CGRAM address
    for i in range(5):
        ch341.i2c_write(0, bytes([addr, CONTROL_DATA]) + CGRAM_BARS[i])

    # use CGRAM
    ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b10000000]))  # set DDRAM address
    for i in range(8):
        ch341.i2c_write(0, bytes([addr, CONTROL_DATA, i]))

    time.sleep(2.0)

    # progress bar using CGRAM
    for i in range(80 + 1):
        full = i // 5
        remain = i % 5
        blank = 16 - full - bool(remain)
        if not remain:
            data = b'\x04' * full + ord(' ').to_bytes() * blank
        else:
            data = b'\x04' * full + remain.to_bytes() + ord(' ').to_bytes() * blank

        ch341.i2c_write(0, bytes([addr, CONTROL_COMMAND, 0b10000000]))  # set DDRAM address
        ch341.i2c_write(0, bytes([addr, CONTROL_DATA]) + data)
        time.sleep(0.03)

    time.sleep(2.0)

    # display string
    clear_display(addr)
    display_string(addr, 0, 0, 'Hello LCD1602')
    display_string(addr, 1, 0, '  AIP30168L')

    ch341.CH341CloseDevice(0)
