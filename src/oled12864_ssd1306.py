
"""
OLED12864
SSD1306 128x64 Dot Matrix OLED Driver

Connection:
SCL - SCK
SDA - SDA

"""

import os
import time

import ch341

import canvas_helper
import pillow_helper


def pillow_image_to_bytes(image):
    width = image.width
    height = image.height
    count = width * height // 8
    buffer = bytearray(count)
    for big_row in range(height // 8):
        for col in range(width):
            b = 0
            for small_row in range(8):
                row = big_row * 8 + small_row
                p = image.getpixel((col, row))
                if p:
                    b |= 1 << small_row
            buffer[big_row * width + col] = b
    return buffer


def display_data(addr, data_bytes):
    use_combined = False
    if not use_combined:
        ch341.i2c_write(0, bytes([addr, 0x00, 0x21, 0x00, 0x7F, 0x22, 0x00, 0x07]))  # reset address
        ch341.i2c_write(0, bytes([addr, 0x40]) + data_bytes)  # display data
    else:
        # Usage of the Continuation bit in Control byte (send both D and C# in one i2c transaction)
        combined = (
            bytes([addr])
            + bytes([0x80, 0x21, 0x80, 0x00, 0x80, 0x7F])  # reset address column
            + bytes([0x80, 0x22, 0x80, 0x00, 0x80, 0x07])  # reset address page
            + bytes([0x40]) + data_bytes  # display data
        )
        ch341.i2c_write(0, combined)


def np_array_to_bytes(arr):
    width = arr.shape[1]
    height = arr.shape[0]
    count = width * height // 8
    buffer = bytearray(count)
    for big_row in range(height // 8):
        for col in range(width):
            b = 0
            for small_row in range(8):
                row = big_row * 8 + small_row
                p = arr[row, col][0]
                if p >= 127:
                    b |= 1 << small_row
            buffer[big_row * width + col] = b
    return buffer


def play_video(addr, video_file):
    import cv2
    cap = cv2.VideoCapture(video_file)
    if not cap.isOpened():
        print(f"video open error {video_file}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_time = 1.0 / fps

    last_time = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        shape = frame.shape
        assert shape[0] == 64 and shape[1] == 128

        data_bytes = np_array_to_bytes(frame)

        now = time.time()
        if now - last_time < frame_time:
            time.sleep(now - last_time)
        last_time = now

        display_data(addr, data_bytes)


if __name__ == '__main__':
    ch341.CH341OpenDevice(0)

    # I2C speed: bit1-0 00(20k) 01(100k) 10(400k) 11(750k)
    use_slow = False
    if use_slow:
        ch341.CH341SetStream(0, 0b00000000)  
    else:
        ch341.CH341SetStream(0, 0b00000011)

    addr = 0b01111000

    print('i2c addr valid:', ch341.i2c_check_addr_ack(0, addr))

    use_official_init = True
    if use_official_init:
        # the following init data is from bottom of the SSD1306 datasheet "Software Configuration"
        init_data = bytes([
            addr, 0x00,
            0xA8, 0x3F,  # Set MUX Ratio
            0xD3, 0x00,  # Set Display Offset
            0x40,        # Set Display Start Line
            0xA1,        # Set Segment re-map A0/A1 (flipped)
            0xC8,        # Set COM Output Scan Direction C0/C8 (flipped)
            0xDA, 0x12,  # Set COM Pins hardware configuration (the reset value is 0x12)
            0x81, 0x7F,  # Set Contrast Control (or brightness, 0x00-0xFF, default is 0x7F)
            0xA4,        # Disable Entire Display On
            0xA6,        # Set Normal Display
            0xD5, 0x80,  # Set Osc Frequency
            0x8D, 0x14,  # Enable charge pump regulator
            0xAF,        # Display On

            0x20, 0x00,  # Set Memory Addressing Mode (horizontal addressing mode)
        ])
    else:
        # the following init data is the bare minimum
        init_data = bytes([
            addr, 0x00,
            0x20, 0x00,  # addressing mode (horizontal addressing mode)
            0x8D, 0x14,  # charge pump enable
        ])

    ch341.i2c_write(0, init_data)

    # ladder like test screen
    screen = bytearray(128 * 8)
    for i in range(len(screen)):
        screen[i] = i % 256

    ch341.i2c_write(0, bytes([
        addr, 0x00,
        0x21, 0x00, 0x7F,  # set column address
        0x22, 0x00, 0x07,  # set page address
    ]))
    ch341.i2c_write(0, bytes([addr, 0x40]) + screen)

    time.sleep(2.0)

    # display off
    display_off_data = bytes([addr, 0x00, 0xAE])
    ch341.i2c_write(0, display_off_data)

    time.sleep(1.0)

    # display on
    display_on_data = bytes([addr, 0x00, 0xAF])
    ch341.i2c_write(0, display_on_data)

    # no rotation (Set Segment Re-map, Set COM Output Scan Direction)
    ch341.i2c_write(0, bytes([addr, 0x00, 0xA0, 0xC0]))
    time.sleep(1.0)
    # rotate 180 (horizontal flip and vertical flip)
    ch341.i2c_write(0, bytes([addr, 0x00, 0xA1, 0xC8]))
    time.sleep(1.0)

    # canvas with texts and lines
    canvas = canvas_helper.Canvas(128, 64)

    example_duration = 3.0

    last = time.perf_counter()
    t_start = time.time()
    while time.time() - t_start < example_duration:
        current = time.perf_counter()
        delta_time = current - last
        last = current

        canvas.clear()
        canvas.draw_example(time.time())
        # frames per second
        canvas.draw_text(0, 32, 'fps {:<6.1f}'.format(1.0 / delta_time if delta_time != 0.0 else 0))
        # delta time
        canvas.draw_text(0, 48, 'dt  {:<6.5f}'.format(delta_time))

        display_data(addr, canvas.to_bytes())

        t1 = time.perf_counter()


    # Pillow Image
    image = pillow_helper.generate_image(128, 64)
    display_data(addr, pillow_image_to_bytes(image))
    time.sleep(example_duration)

    # play mp4 video
    # NOTE place input.mp4 in misc/scripts, run misc/scripts/convert_video_dither.py to generate output.mp4
    video_file = os.path.join('../misc/scripts/output.mp4')
    if os.path.isfile(video_file):
        play_video(addr, video_file)
