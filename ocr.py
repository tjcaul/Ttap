from PIL import ImageGrab, Image
from pytesseract import pytesseract
from random import randint
from collections import deque
import asyncio
import time
from threading import Thread, Event

class OCR:
    SCROLLBAR_COLOURS = [(234, 51, 35), (212, 212, 212), (128, 128, 128)]
    BACKGROUND_COLOUR = (0, 0, 0)

    _thread: Thread
    _queue: deque
    _poll_time: float
    _kill_flag: Event

    def __init__(self, queue, poll_time) -> None:
        self._queue = queue
        self._poll_time = poll_time
        self._thread = None

    def _colour_close(self, a: tuple[int, int, int], b: tuple[int, int, int], radius: int):
        actual_radius_squared = (a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2
        return actual_radius_squared <= radius ** 2

    def _smart_crop(self, image: Image) -> str:
        image = image.crop((500, 1300, 2880-500, 1800-150));

        # find scroll bar if it exists
        x = image.width // 2
        for y in range(image.height - 4):
            colour_stripe = [image.getpixel((x, y + i)) for i in range(4)]
            if all(any(self._colour_close(colour, scrollbar_colour, 3) for scrollbar_colour in self.SCROLLBAR_COLOURS) for colour in colour_stripe):
                return image.crop((0, 0, image.width - 1, y - 1))
        return image  # no cropping needed

    def _brightness(self, colour: tuple[int, int, int, int]):
        return sum(colour[:3]) // 3

    def _max_brightness(self, image: Image) -> int:
        return max(self._brightness(image.getpixel((x, y))) for x in range(0, image.width, 10) for y in range(0, image.height, 10))

    def _get_text(self, image: Image) -> str:
        text = pytesseract.image_to_string(image).strip()
        path = f"ss/{randint(0, 1000000)}.png"
        image.save(path)
        return text

    def _choose_best_image(self, images: list[Image]) -> Image:
        max_brightness = 0
        brightest_image = images[0]
        for image in images:
            brightness = self._max_brightness(image)
            if brightness > max_brightness:
                brightest_image = image
                max_brightness = brightness

        if max_brightness > 250:
            return brightest_image
        return None

    def _cleanup_text(self, text: str) -> str:
        return text.replace('|', 'I')

    def _thread_function(self):
        lasttext = ""

        while not self._kill_flag.is_set():
            # capture two images to allow for subtitles to fully appear / disappear
            image1 = ImageGrab.grab()
            time.sleep(0.05)
            image2 = ImageGrab.grab()

            image1 = self._smart_crop(image1)
            image2 = self._smart_crop(image2)

            image = self._choose_best_image([image1, image2])

            if image:
                text = self._get_text(image)

                if text != lasttext and text != "" and text is not None:
                    lasttext = text
                    print(f'"{text}"')

                    self._queue.append(self._cleanup_text(text))
            else:
                lasttext = None

            time.sleep(self._poll_time)


    def start(self) -> None:
        if not self._thread:
            self._kill_flag = Event()
            self._thread = Thread(target=self._thread_function)
            self._thread.start()

    def stop(self) -> None:
        if self._thread:
            self._kill_flag.set()
            self._thread.join()
