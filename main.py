from collections import deque
from ocr import OCR
from speak import SpeechClient
from gui import App

def mainloop(delay: float):
    POLL_RATE = 0.1

    global_que = deque()
    speak_engine = SpeechClient(global_que)
    ocr_engine = OCR(global_que, POLL_RATE)
    gui = App(ocr_engine, speak_engine)



    if __name__ == '__main__':
        mainloop(0.1)
