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
