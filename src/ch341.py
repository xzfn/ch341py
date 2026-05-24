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
