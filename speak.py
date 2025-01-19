from typing import Optional
from io import BytesIO

from collections import deque
import time
from threading import Thread, Event
from gtts import gTTS
from playsound3 import playsound

"""
Class that runs an OCR process in the background, adding each unique string it finds to the queue.
"""
class SpeechClient:
    _queue: deque

    _thread: Optional[Thread]
    _kill_flag: Event


    def __init__(self, queue: deque) -> None:
        """
        Initialize the OCR system to write into the given queue. The screen will be captured every
        poll_time seconds. Too slow, and it'll miss subtitles; too fast, and it'll lag the system.
        """
        self._queue = queue

        self._thread = None
        self._kill_flag = Event()

    def start(self, force: bool = False) -> None:
        """
        If the main thread isn't running already, spawn a new thread to begin the speech process.
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

    def _speak(self, txt, lang='en'):
        with open("tmp.mp3", "wb") as temp_file:
            gTTS(text=txt, lang=lang).write_to_fp(temp_io := BytesIO())
            temp_file.write(temp_io.getbuffer())
        playsound("tmp.mp3", True)

    def _thread_function(self):
        while not self._kill_flag.is_set():
            while not self._queue:
                time.sleep(0.1)
            self._speak(self._queue.popleft())
