from PIL import ImageGrab, Image
from pytesseract import pytesseract

SCROLLBAR_COLOURS = [(234, 51, 35), (212, 212, 212), (128, 128, 128)]

def colour_close(a: tuple[int, int, int], b: tuple[int, int, int], radius: int):
    actual_radius_squared = (a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2
    return actual_radius_squared <= radius ** 2

def smart_crop(image: Image) -> str:
    image = image.crop((500, 1300, 2880-500, 1800-150));

    # find scroll bar if it exists
    x = image.width // 2
    for y in range(image.height):
        colour = image.getpixel((x, y))
        if any(colour_close(colour, scrollbar_colour, 10) for scrollbar_colour in SCROLLBAR_COLOURS):
            return image.crop((0, 0, image.width - 1, y - 1))
    return image  # no cropping needed


def get_text(image: Image) -> str:
    image = smart_crop(image)
    text = pytesseract.image_to_string(image)
    path = "ss/" + text.replace('.', '_').replace('/', '_') + ".png"
    print(path)
    image.save(path)
