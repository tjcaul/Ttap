import time
from PIL import ImageGrab, Image
import ocr
import speak

def mainloop(delay: float):
    time.sleep(2)
    speak_engine = speak.init()

    lasttext = ""

    while True:
        image = ImageGrab.grab()

        text = ocr.get_text(image)

        if text != lasttext:
            lasttext = text
            print(f'"{text}"')
            #speak.speak(speak_engine, text)

        time.sleep(delay)

if __name__ == '__main__':
    mainloop(0.1)
