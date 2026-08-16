
from PIL import Image, ImageDraw, ImageFont


def generate_image(width, height):
    image = Image.new('L', (width, height))
    draw = ImageDraw.Draw(image)

    draw.line((0, 0, width, height), fill=255, width=3)

    draw.rectangle((30, 10, 60, 60), fill=0, outline=255, width=2)
    draw.circle((20, 20), 15, fill=None, outline=255, width=3)

    text = "Hello测试"

    try:
        font = ImageFont.truetype("arial.ttf", size=24)
        font = ImageFont.truetype("msyh.ttc", size=24)
    except IOError:
        font = ImageFont.load_default()

    draw.text((10, 30), text, fill=255, font=font)

    return image


if __name__ == '__main__':
    image = generate_image(128, 64)
    image.show()
