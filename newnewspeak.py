from io import BytesIO

from gtts import gTTS
from playsound3 import playsound

def speak(txt, lang='en'):
    with open("tmp.mp3", "wb") as temp_file:
        gTTS(text=txt, lang=lang).write_to_fp(temp_io := BytesIO())
        temp_file.write(temp_io.getbuffer())
    playsound("tmp.mp3", False)

txt = "the only way is through"
speak(txt)