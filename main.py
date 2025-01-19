from collections import deque
from ocr import OCR
from speak import SpeechClient
from gui import App

def main():
    POLL_RATE = 0.025

    global_que = deque()
    speak_engine = SpeechClient(global_que, profile_time=True)
    ocr_engine = OCR(global_que, POLL_RATE, profile_time=True)
    ui = App(ocr_engine, speak_engine)
    ui.mainloop()

if __name__ == '__main__':
    main()
