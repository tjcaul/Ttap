from typing import Optional

from PIL import ImageGrab, Image
from pytesseract import pytesseract
from collections import deque
import time
from threading import Thread, Event
from random import randint
import os

"""
Class that runs an OCR process in the background, adding each unique string it finds to the queue.
"""
class OCR:
    SCROLLBAR_COLOURS = [(234, 51, 35), (212, 212, 212), (128, 128, 128)]
    SCROLLBAR_THICKNESS = 17
    BACKGROUND_COLOUR = (0, 0, 0)

    _queue: deque
    _poll_time: float
    _save_screenshots: bool
    _profile_time: bool

    _thread: Optional[Thread]
    _kill_flag: Event

    _bounding_box: tuple[int, int, int, int]

    def __init__(self, queue: deque, poll_time: float, save_screenshots: bool = False, profile_time: bool = False) -> None:
        """
        Initialize the OCR system to write into the given queue. The screen will be captured every
        poll_time seconds. Too slow, and it'll miss subtitles; too fast, and it'll lag the system.
        """
        self._queue = queue
        self._poll_time = poll_time
        self._save_screenshots = save_screenshots
        self._profile_time = profile_time

        self._thread = None
        self._kill_flag = Event()
        self._bounding_box = (500, 300, 2880-500, 1800-150)

    def set_bounding_box(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """
        Set the bounding box for capturing subtitles.
        Preconditions:
        - 0 <= x1 < x2
        - 0 <= y1 < y2
        """
        assert 0 <= x1 < x2 and 0 <= y1 < y2, "Invalid bounding box"
        self._bounding_box = (x1, y1, x2, y2)

    def start(self, force: bool = False) -> None:
        """
        If the main thread isn't running already, spawn a new thread to begin the OCR&queue process.
        If force=True is specified, start a new thread even if one already exists.
        """
        if self._thread:
            if force:
                print('\033[32;1mOCR was already running; \033[33mforced to start again.\033[0m')
            else:
                print('\033[32;1mOCR started but was already running.\033[0m')
        else:
            print('\033[32;1mOCR started.\033[0m')

        if (not self._thread) or force:
            self._kill_flag.clear()
            self._thread = Thread(target=self._thread_function)
            self._thread.start()

    def stop(self) -> None:
        """
        If the main thread is running, gracefully stop it.
        """
        if self._thread:
            print('\033[31;1mOCR stopped.\033[0m')
            self._kill_flag.set()
            self._thread.join()
            self._thread = None
        else:
            print('\033[31;1mOCR stopped but it wasn\'t running.\033[0m')

    def restart(self) -> None:
        """
        Forcefully restart the thread in case of a crash.
        """
        print('\033[33;1mOCR restarted.\033[0m')
        self.stop()
        self.start(force=True)


    ### PRIVATE METHODS ###

    @staticmethod
    def _colour_close(a: tuple[int, int, int], b: tuple[int, int, int], radius: int) -> bool:
        """
        Return whether two colours are within the given radius when interpreted as 3D vectors.
        """
        actual_radius_squared = (a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2
        return actual_radius_squared <= radius ** 2

    def _find_scrollbar(self, image: Image) -> str:
        """
        Return the y-coordinate of the top of the scroll bar within the image.
        """
        x_coords = [x for x in range(0, image.width, image.width // 5)]
        y_coords = []
        for x in x_coords:
            found_scrollbar = False
            for y in range(image.height - 1, -1, -1):
                colour = image.getpixel((x, y))
                if any(self._colour_close(colour, scrollbar_colour, 3) for scrollbar_colour in self.SCROLLBAR_COLOURS):
                    y_coords.append(y)
                    found_scrollbar = True
                    break
            if not found_scrollbar:
                # no scrollbar found at this x coordinate; scrollbar likely doesn't exist
                return image.height
        return max(max(y_coords, key=y_coords.count) - self.SCROLLBAR_THICKNESS, 0)

    def _smart_crop(self, image: Image) -> str:
        """
        Crop the image to contain only subtitles.
        """
        # first refinement: crop to a fixed box
        image = image.crop(self._bounding_box)

        # crop out the scroll bar
        scrollbar_y = self._find_scrollbar(image)
        return image.crop((0, 0, image.width - 1, scrollbar_y))

    @staticmethod
    def _brightness(colour: tuple[int, ...]) -> int:
        """
        Compute a simple notion of the brightness of a pixel: the average of its channels.
        """
        return sum(colour[:3]) // 3

    def _max_brightness(self, image: Image) -> int:
        """
        Return the maximum brightness of any pixel in the image.
        """
        extrema = image.getextrema()
        return self._brightness(tuple(int(band[1]) for band in extrema))

    def _get_text(self, image: Image) -> str:
        """
        Extract text from a cropped image.
        """
        start = time.time()

        # scale image down to speed up tesseract
        image.thumbnail((image.width // 2, image.height // 2))

        # process with tesseract OCR
        text = pytesseract.image_to_string(image).strip()

        if self._save_screenshots:
            # save image to file for debugging
            os.makedirs("screenshots", exist_ok=True)
            path = f"screenshots/{randint(0, 1000000)}.png"
            image.save(path)

        end = time.time()
        if self._profile_time:
            print(f'\033[35m_get_text()\t\ttook \033[1m{end-start:.3f}s\033[0m')

        return text

    def _choose_best_image(self, images: list[Image]) -> Image:
        """
        Given a list of images, return the one with the brightest maximum pixel, but only if
        its brightness is > 250. If no image satisfies this constraint, return None.
        This helps us avoid grey, blurred text that appears while subtitles change, and also
        avoid trying to find text in a black image.
        """
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

    @staticmethod
    def _cleanup_text(text: str) -> str:
        """
        Apply substitutions to text to correct common OCR mistakes.
        """
        return text.replace('|', 'I')

    def _thread_function(self) -> None:
        """
        Continuously OCR the screen. When the subtitles change, enqueue the new subtitle text.
        Terminates when self._kill_flag gets set to allow for graceful shutdown.
        """
        last_text = ""

        while not self._kill_flag.is_set():
            # capture two images to allow for subtitles to fully appear / disappear
            image1 = ImageGrab.grab()
            time.sleep(0.05)
            image2 = ImageGrab.grab()

            start = time.time()
            image1 = self._smart_crop(image1)
            image2 = self._smart_crop(image2)
            end = time.time()

            if self._profile_time:
                print(f'\033[36m_smart_crop()\ttook \033[1m{end-start:.3f}s\033[0m')

            image = self._choose_best_image([image1, image2])

            if image:
                text = self._get_text(image)

                if text != last_text and text != "" and text is not None:
                    last_text = text
                    self._queue.append(self._cleanup_text(text))
            else:
                last_text = None

            time.sleep(self._poll_time)


def demo(max_lines: int = 0) -> None:
    """
    Run a demo, printing text as it appears in the queue.
    Can optionally stop after reading a certain number of lines of text.
    """
    queue = deque()
    ocr = OCR(queue, poll_time=0.1, save_screenshots=False, profile_time=False)
    ocr.start()

    lines = 0
    while max_lines <= 0 or lines < max_lines:
        if queue:
            print(f'\033[7;1m"{queue.popleft()}"\033[0m')
            lines += 1
        time.sleep(0.1)

if __name__ == '__main__':
    demo()
