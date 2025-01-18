from PIL import ImageGrab, Image
from pytesseract import pytesseract
from random import randint
from collections import deque
import asyncio
import time

class OCR:
    SCROLLBAR_COLOURS = [(234, 51, 35), (212, 212, 212), (128, 128, 128)]

    _queue: deque
    _poll_time: float

    def __init__(self, queue, poll_time) -> None:
        self._queue = queue
        self._poll_time = poll_time
        self._async_task = None

    def _colour_close(self, a: tuple[int, int, int], b: tuple[int, int, int], radius: int):
        actual_radius_squared = (a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2
        return actual_radius_squared <= radius ** 2

    def _smart_crop(self, image: Image) -> str:
        image = image.crop((500, 1300, 2880-500, 1800-150));

        # find scroll bar if it exists
        x = image.width // 2
        for y in range(image.height):
            colour = image.getpixel((x, y))
            if any(self._colour_close(colour, scrollbar_colour, 3) for scrollbar_colour in self.SCROLLBAR_COLOURS):
                return image.crop((0, 0, image.width - 1, y - 1))
        return image  # no cropping needed

    def _get_text(self, image: Image) -> str:
        image = self._smart_crop(image)
        text = pytesseract.image_to_string(image).strip()
        path = f"ss/{randint(0, 1000000)}.png"
        image.save(path)
        return text

    async def _loop(self):
        lasttext = ""

        while True:
            image = ImageGrab.grab()

            text = self._get_text(image)

            if text != lasttext:
                lasttext = text
                print(f'"{text}"')
                self._queue.append(text)

            time.sleep(self._poll_time)

    async def start(self) -> None:
        if not self._async_task:
            self._async_task = asyncio.create_task(self._loop())
            await self._async_task

    async def stop(self) -> None:
        if self._async_task:
            self._async_task.cancel()
            self._async_task = None

