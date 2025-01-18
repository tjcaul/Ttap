import asyncio
from collections import deque
from threading import Thread

import pyttsx3


class SpeechClient():
    engine: pyttsx3.Engine
    _speech_queue: deque[str] = deque()
    _speech_task = None
    _current_speaking_thread = None

    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 130)

    def queue_text(self, text: str):
        self._speech_queue.append(text)

    def _speak(self, text: str) -> None:
        self.engine.say(text)
        self._current_speaking_thread = Thread(target=self.engine.runAndWait)
        self._current_speaking_thread.run()

    async def start_speaking(self):
        if not self._speech_task:
            self._speech_task = asyncio.create_task(self._process_queue())
            await self._speech_task


    async def stop_speaking(self):
        if self._speech_task:
            self._speech_task.cancel()
        self._speech_task = None

    async def _process_queue(self):
        while True:
            if self._speech_queue and not (self._current_speaking_thread and self._current_speaking_thread.is_alive()):
                self._speak(self._speech_queue.popleft())
            await asyncio.sleep(0)

async def main():
    my_engine = SpeechClient()
    my_engine.queue_text('fuck this shit im out')
    my_engine.queue_text('thats whats up')
    my_engine.queue_text('the only way is through')
    await my_engine.start_speaking()


if __name__ == '__main__':
    asyncio.run(main())