# ch341py
Control CH341 module using Python on PC.

`ch341.py` is the main binding module using the builtin ctypes module.

## WCH Resources
CH341 product page: https://www.wch.cn/products/CH341.html

CH341 resource files: https://www.wch.cn/search.html and search "CH341"

CH341PAR.EXE: Parallel mode Windows driver. - *Must install this*

CH341SER.EXE: Serial mode Windows driver. - *Must not install this*

CH341DS1.PDF: Datasheet part 1.

CH341DS2.PDF: Datasheet part 2.

CH341EVT.ZIP: Reference C/C++ source code and GUI tool.

CH341PAR.ZIP: Parallel mode development libraries and headers.

Unzip CH341EVT.ZIP you can find the CH341DLL.h file. This is the C header for the driver interface. The ch341.py file bind functions in this file. The actual driver dll on 64bit Windows is CH341DLLA64.DLL.

## Quick Start
Download and install CH341PAR.exe parallel mode driver.

Connect a LED with a 1k resistor to the CS0 pin then to ground.

Open console.

```cmd
cd src
python led_flash.py
```

You should see the LED flashing.
