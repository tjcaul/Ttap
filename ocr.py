from PIL import ImageGrab, Image
from pytesseract import pytesseract
from random import randint
from collections import deque
import asyncio
import time
from threading import Thread, Event

"""
Class that runs an OCR process in the background, adding each unique string it finds to the queue.
"""
class OCR:
    SCROLLBAR_COLOURS = [(234, 51, 35), (212, 212, 212), (128, 128, 128)]
    BACKGROUND_COLOUR = (0, 0, 0)

    _thread: Thread
    _queue: deque
    _poll_time: float
    _kill_flag: Event

    def __init__(self, queue, poll_time) -> None:
        """
        Initialize the OCR system to write into the given queue. The screen will be captured every
        poll_time seconds; too slow and it'll miss subtitles, too fast and it'll lag the system.
        """
        self._queue = queue
        self._poll_time = poll_time
        self._thread = None
        self._kill_flag = Event()

    def _colour_close(self, a: tuple[int, int, int], b: tuple[int, int, int], radius: int):
        """
        Return whether two colours are within the given radius when interpreted as 3D vectors.
        """
        actual_radius_squared = (a[0] - b[0])**2 + (a[1] - b[1])**2 + (a[2] - b[2])**2
        return actual_radius_squared <= radius ** 2

    def _smart_crop(self, image: Image) -> str:
        """
        Crop the image to contain only subtitles.
        """
        # first refinement: crop to a fixed box
        image = image.crop((500, 1300, 2880-500, 1800-150));

        # find scroll / progress bar if it exists
        x = image.width // 2
        for y in range(image.height - 4):
            colour_stripe = [image.getpixel((x, y + i)) for i in range(4)]
            if all(any(self._colour_close(colour, scrollbar_colour, 3) for scrollbar_colour in self.SCROLLBAR_COLOURS) for colour in colour_stripe):
                # crop out the scroll bar
                return image.crop((0, 0, image.width - 1, y - 1))
        return image  # no further cropping needed

    def _brightness(self, colour: tuple[int, int, int, int]) -> int:
        """
        Compute a simple notion of the brightness of a pixel: the average of its channels.
        """
        return sum(colour[:3]) // 3

    def _max_brightness(self, image: Image) -> int:
        """
        Return the maximum brightness of any pixel in the image.
        """
        return max(self._brightness(image.getpixel((x, y))) for x in range(0, image.width, 10) for y in range(0, image.height, 10))

    def _get_text(self, image: Image) -> str:
        """
        Extract text from a cropped image.
        """
        text = pytesseract.image_to_string(image).strip()
        path = f"ss/{randint(0, 1000000)}.png"
        image.save(path)
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

    def _cleanup_text(self, text: str) -> str:
        """
        Apply substitutions to text to correct common OCR mistakes.
        """
        return text.replace('|', 'I')

    def _thread_function(self):
        """
        Continuously OCR the screen. When the subtitles change, enqueue the new subtitle text.
        Terminates when self._kill_flag gets set to allow for graceful shutdown.
        """
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
                    self._queue.append(self._cleanup_text(text))
            else:
                lasttext = None

            time.sleep(self._poll_time)


    def start(self, force: bool = False) -> None:
        """
        If the main thread isn't running already, spawn a new thread to begin the OCR&queue process.
        If force=True is specified, start a new thread even if one already exists.
        """
        if (not self._thread) or force:
            self._kill_flag.clear()
            self._thread = Thread(target=self._thread_function)
            self._thread.start()

    def stop(self) -> None:
        """
        If the main thread is running, gracefully stop it.
        """
        if self._thread:
            self._kill_flag.set()
            self._thread.join()

    def restart(self) -> None:
        """
        Forcefully restart the thread in case of a crash.
        """
        self.stop()
        self.start(force=True)


if __name__ == '__main__':
    """
    Run a demo, printing text as it appears in the queue.
    """
    queue = deque()
    ocr = OCR(queue, poll_time=0.1)
    ocr.start()
    while True:
        if queue:
            print(queue.popleft())
        time.sleep(0.1)
    
