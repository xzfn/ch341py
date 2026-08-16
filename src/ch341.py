"""
CH341 binding module using ctypes.
"""

import ctypes
from ctypes import wintypes


INVALID_HANDLE_VALUE = wintypes.HANDLE(-1).value


def win32_check_handle(result, func, args):
    if result == INVALID_HANDLE_VALUE:
        raise ctypes.WinError()
    return args

def win32_check_bool(result, func, args):
    if not result:
        raise ctypes.WinError()
    return args

def check_int_sign(result, func, args):
    if result < 0:
        raise ctypes.WinError()
    return args

def create_ctypes_buffer(data):
    return ctypes.create_string_buffer(data, len(data))


ch341dll = ctypes.windll.LoadLibrary('CH341DLLA64.DLL')


CH341OpenDevice = ch341dll.CH341OpenDevice
CH341OpenDevice.argtypes = [wintypes.ULONG]
CH341OpenDevice.restype = wintypes.HANDLE
CH341OpenDevice.errcheck = win32_check_handle

CH341CloseDevice = ch341dll.CH341CloseDevice
CH341CloseDevice.argtypes = [wintypes.ULONG]
CH341CloseDevice.restype = None

CH341Set_D5_D0 = ch341dll.CH341Set_D5_D0
CH341Set_D5_D0.argtypes = [wintypes.ULONG, wintypes.ULONG, wintypes.ULONG]
CH341Set_D5_D0.restype = wintypes.BOOL
CH341Set_D5_D0.errcheck = win32_check_bool
CH341Set_D5_D0.__doc__ = """
Set D5-D0 pin dir and data
Args:
    iIndex: device index.
    iSetDirOut: D5-D0 pin direction. 0 for input, 1 for output.
    iSetDataOut: D5-D0 pin output value. If dir is output, 0 for low, 1 for high.
Returns:
    True for success.
"""

CH341SetStream = ch341dll.CH341SetStream
CH341SetStream.argtypes = [wintypes.ULONG, wintypes.ULONG]
CH341SetStream.restype = wintypes.BOOL
CH341SetStream.errcheck = win32_check_bool
CH341SetStream.__doc__ = """
Set I2C and SPI mode
Args:
    iIndex: device index.
    iMode: device mode. i2c bit1-0 00(20k) 01(100k) 10(400k) 11(750k), spi bit2 0(single) 1(double), spi bit7 0(LSB first) 1(MSB first)
Returns:
    True for success.
"""

CH341StreamSPI4 = ch341dll.CH341StreamSPI4
# device_index, chip_select 0x80 + 0bxx, length, io_buffer
CH341StreamSPI4.argtypes = [wintypes.ULONG, wintypes.ULONG, wintypes.ULONG, ctypes.c_void_p]
CH341StreamSPI4.restype = wintypes.BOOL
CH341StreamSPI4.errcheck = win32_check_bool
CH341StreamSPI4.__doc__ = """
Stream SPI data 4 wire
Args:
    iIndex: device index.
    iChipSelect: chip select. bit7 0(ignore) 1(valid). bit1-0 00/01/10 for CS0/CS1/CS2 (or D0/D1/D2)
    iLength: buffer length.
    ioBuffer: io buffer. Prepared data to write to DOUT. Filled with data from DIN after calling.
Returns:
    True for success.
"""


CH341StreamI2C = ch341dll.CH341StreamI2C
# index, write_length, write_buffer, read_length, read_buffer
CH341StreamI2C.argtypes = [wintypes.ULONG, wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG, ctypes.c_void_p]
CH341StreamI2C.restype = wintypes.BOOL
CH341StreamI2C.errcheck = win32_check_bool
CH341StreamI2C.__doc__ = """
Stream I2C data
Args:
    iIndex: device index.
    iWriteLength: write length.
    iWriteBuffer: buffer to write to device.
    iReadLength: read length.
    oReadBuffer: buffer to store read data from device.
Returns:
    True for success.
"""


mCH341_PACKET_LENGTH = 32

mCH341A_CMD_I2C_STREAM = 0xAA

mCH341A_CMD_I2C_STM_STA = 0x74
mCH341A_CMD_I2C_STM_STO = 0x75
mCH341A_CMD_I2C_STM_OUT	= 0x80
mCH341A_CMD_I2C_STM_END = 0x00

mCH341A_CMD_I2C_STM_MAX = min(0x3F, mCH341_PACKET_LENGTH)


CH341WriteRead = ch341dll.CH341WriteRead
CH341WriteRead.argtypes = [wintypes.ULONG, wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG, wintypes.ULONG, wintypes.PULONG, ctypes.c_void_p]
CH341WriteRead.restype = wintypes.BOOL
CH341WriteRead.errcheck = win32_check_bool
CH341WriteRead.__doc__ = """
Stream write and read data
Args:
    iIndex: device index.
    iWriteLength: write length.
    iWriteBuffer: buffer to write to device.
    iReadStep: read block size (total to read length is iReadStep * iReadTimes).
    iReadTimes: read times.
    oReadLength: output read length.
    oReadBuffer: buffer to store read data from device.
Returns:
    True for success.
"""



def i2c_write(device_index, data):
    return CH341StreamI2C(device_index, len(data), data, 0, None)


def i2c_check_addr_ack(device_index, addr_8bit):
    data = bytearray(mCH341_PACKET_LENGTH)
    data[0] = mCH341A_CMD_I2C_STREAM
    data[1] = mCH341A_CMD_I2C_STM_STA
    data[2] = mCH341A_CMD_I2C_STM_OUT
    data[3] = addr_8bit
    data[4] = mCH341A_CMD_I2C_STM_STO
    data[5] = mCH341A_CMD_I2C_STM_END
    length = 6
    in_length = wintypes.ULONG(0)

    c_buffer = create_ctypes_buffer(bytes(data))
    c_buffer_read = ctypes.create_string_buffer(mCH341_PACKET_LENGTH)
    CH341WriteRead(device_index, length, c_buffer, mCH341A_CMD_I2C_STM_MAX, 1, ctypes.byref(in_length), c_buffer_read)
    if in_length.value > 0:
        if c_buffer_read.raw[in_length.value - 1] & 0x80 == 0:
            return True
    return False
