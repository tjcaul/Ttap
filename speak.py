import asyncio
import time
from collections import deque
from threading import Thread

import pyttsx3


class SpeechClient:
    engine: pyttsx3.Engine
    _speech_queue: deque[str]
    _speech_task = None
    _current_speaking_thread = None

    def __init__(self, speech_queue: deque[str]):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 130)
        self._speech_queue = speech_queue

        process = Thread(target=self._process_queue)
        process.start()

    def queue_text(self, text: str):
        self._speech_queue.append(text)

    def _speak(self, text: str) -> None:
        print(text)
        self.engine.say(text)
        self.engine.runAndWait()

    def _process_queue(self):
        while True:
            print(self.engine.isBusy(), self._speech_queue)
            if self._speech_queue:
                self._speak(self._speech_queue.popleft())
            time.sleep(0.5)

async def main():
    my_engine = SpeechClient(deque())
    my_engine.queue_text('fuck this shit im out')
    my_engine.queue_text('thats whats up')
    my_engine.queue_text('the only way is through')

if __name__ == '__main__':
    asyncio.run(main())