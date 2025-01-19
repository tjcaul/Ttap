from typing import Optional
from io import BytesIO

from collections import deque
import time
from threading import Thread, Event
from gtts import gTTS
from playsound3 import playsound

"""
Class that runs a speech process in the background, speaking each string that appears in the queue.
"""
class SpeechClient:
    _queue: deque
    _profile_time: bool

    _thread: Optional[Thread]
    _kill_flag: Event


    def __init__(self, queue: deque, profile_time: bool = False) -> None:
        """
        Initialize the speech system to read from the given queue. The screen will be captured every
        poll_time seconds. Too slow, and it'll miss subtitles; too fast, and it'll lag the system.
        """
        self._queue = queue
        self._profile_time = profile_time

        self._thread = None
        self._kill_flag = Event()

    def start(self, force: bool = False) -> None:
        """
        If the main thread isn't running already, spawn a new thread to begin the speech process.
        If force=True is specified, start a new thread even if one already exists.
        """
        if self._thread:
            if force:
                print('\033[32;1mSpeechClient was already running; \033[33mforced to start again.\033[0m')
            else:
                print('\033[32;1mSpeechClient started but was already running.\033[0m')
        else:
            print('\033[32;1mSpeechClient started.\033[0m')

        if (not self._thread) or force:
            self._kill_flag.clear()
            self._thread = Thread(target=self._thread_function)
            self._thread.start()

    def stop(self) -> None:
        """
        If the main thread is running, gracefully stop it.
        """
        if self._thread:
            print('\033[31;1mSpeechClient stopped.\033[0m')
            self._kill_flag.set()
            self._thread.join()
            self._thread = None
        else:
            print('\033[31;1mSpeechClient stopped but it wasn\'t running.\033[0m')


    def restart(self) -> None:
        """
        Forcefully restart the thread in case of a crash.
        """
        print('\033[33;1mSpeechClient restarted.\033[0m')
        self.stop()
        self.start(force=True)

    def _speak(self, txt, lang='en'):
        start = time.time()
        with open("tmp.mp3", "wb") as temp_file:
            gTTS(text=txt, lang=lang).write_to_fp(temp_io := BytesIO())
            temp_file.write(temp_io.getbuffer())
        end1 = time.time()
        playsound("tmp.mp3", True)
        end2 = time.time()

        if self._profile_time:
            print(f'\033[36mgTTS()\t\ttook \033[1m{end1-start:.3f}s\033[0m')
            print(f'\033[36m_speak()\ttook \033[1m{end2-start:.3f}s\033[0m')

    def _thread_function(self):
        while not self._kill_flag.is_set():
            while not self._queue:
                time.sleep(0.1)
            self._speak(self._queue.popleft())
