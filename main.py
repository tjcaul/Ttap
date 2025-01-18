from collections import deque
from ocr import OCR
from speak import SpeechClient
from gui import App

def mainloop():
    POLL_RATE = 0.1

    global_que = deque()
    speak_engine = SpeechClient(global_que)
    ocr_engine = OCR(global_que, POLL_RATE)
    ui = App(ocr_engine, speak_engine)
    ui.mainloop()




if __name__ == '__main__':
    mainloop()
