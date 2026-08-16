
import math

import font_ascii_8x16


class Canvas:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.data = bytearray(width * height)

    def _is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def set_pixel(self, x: int, y: int, value: int = 1):
        if self._is_inside(x, y):
            index = y * self.width + x
            self.data[index] = 1 if value else 0

    def get_pixel(self, x: int, y: int) -> int:
        if self._is_inside(x, y):
            index = y * self.width + x
            return self.data[index]
        return 0

    def clear(self):
        self.data = bytearray(self.width * self.height)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, value: int = 1):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        
        err = dx - dy

        while True:
            self.set_pixel(x0, y0, value)

            if x0 == x1 and y0 == y1:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def draw_char(self, x, y, n):
        data = font_ascii_8x16.ALL_CHARS.get(n)
        if data:
            for row, b in enumerate(data):
                for i in range(8):
                    if b & (1 << (7 - i)):
                        self.set_pixel(x + i, y + row)
            return 8
        return 8

    def draw_text(self, x, y, text, spacing=0):
        current_x = x
        for c in text:
            n = ord(c)
            w = self.draw_char(current_x, y, n)
            current_x += w + spacing

    def display(self):
        for y in range(self.height):
            row_chars = []
            for x in range(self.width):
                pixel = self.get_pixel(x, y)
                row_chars.append("█" if pixel == 1 else "·")
            print("".join(row_chars))

    def draw_example(self, t=0.0):
        self.draw_line(0, 0, self.width, self.height)
        self.draw_line(0, 0, self.width - 1, 0)
        self.draw_line(0, 0, 0, self.height - 1)

        mid_x = self.width // 2
        mid_y = self.height // 2

        length = min(mid_x, mid_y) - 4

        dx = int(length * math.cos(t))
        dy = int(length * math.sin(t))

        self.draw_line(mid_x, mid_y, mid_x + dx, mid_y + dy)
        self.draw_text(0, 0, 'ABC123')

    def to_bytes(self):
        count = self.width * self.height // 8
        buffer = bytearray(count)
        for y in range(self.height):
            for x in range(self.width):
                index = self.width * (y // 8) + x
                p = self.get_pixel(x, y)
                if p:
                    buffer[index] |= 1 << (y % 8)
        return buffer


if __name__ == "__main__":
    canvas = Canvas(32, 16)

    canvas.draw_line(2, 2, 17, 2)
    canvas.draw_line(2, 7, 17, 7)
    canvas.draw_line(2, 2, 2, 7)
    canvas.draw_line(17, 2, 17, 7)

    canvas.draw_line(2, 2, 17, 7)

    canvas.set_pixel(10, 8, 1)
    canvas.draw_text(0, 0, 'ABC')

    canvas.display()
    print(canvas.to_bytes())
