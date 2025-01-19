import customtkinter
from ocr import OCR
from screen_capture_ui import ScreenCaptureApp
from speak import SpeechClient


class App(customtkinter.CTk):
    reading_status: bool
    ocr_engine: OCR
    speech_engine: SpeechClient


    def __init__(self, ocr_engine: OCR, speech_engine: SpeechClient) -> None:
        super().__init__()
        customtkinter.set_default_color_theme("dark-blue")

        self.ocr_engine = ocr_engine
        self.speech_engine = speech_engine
        self.reading_status = False


        self.title("TTSS")
        self.geometry("400x150")
        self.grid_columnconfigure((0, 1), weight=1)

        self.welcome_label = customtkinter.CTkLabel(self, text="Welcome" )
        self .welcome_label.grid(row=0, column=0, columnspan=1)
        self.button = customtkinter.CTkButton(self, text="Start Reading", command=self.start_stop_button)
        self.button.grid(row=1, column=0)

        self.speaking_controls_frame = customtkinter.CTkFrame(self)
        self.speaking_controls_frame.grid(row=0, column=1, rowspan=2)
        self.volume_slider_label = customtkinter.CTkLabel(self.speaking_controls_frame, text="Volume")
        self.volume_slider_label.grid(row=0, column=1, columnspan=1)
        self.volume_slider = customtkinter.CTkSlider(self.speaking_controls_frame, from_=0, to=100)
        self.volume_slider.grid(row=1, column=1)

    # app takes time to load

    def start_stop_button(self):
        if self.reading_status:
            self.ocr_engine.stop()
            self.reading_status = False
            self.button.configure(text="Start Reading")
        else:
            screen_shot_app = ScreenCaptureApp(self.ocr_engine)
            screen_shot_app.mainloop()
            print("hello")
            self.reading_status = True
            self.button.configure(text="Stop Reading")



