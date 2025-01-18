import pyttsx3

def speak(engine, text: str) -> None:
    engine.say(text)
    engine.runAndWait()

def init():
    engine = pyttsx3.init()
    engine.setProperty('rate', 130)
    return engine
