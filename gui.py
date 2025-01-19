import customtkinter
from librosa.effects import pitch_shift

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

        self.title("TTAP")
        self.geometry("475x150")
        self.grid_columnconfigure((0, 1), weight=1)

        self.button = customtkinter.CTkButton(self, text="Start Reading", command=self.start_stop_button)
        self.button.grid(row=0, column=0, pady = 10)

        self.speaking_controls_frame = customtkinter.CTkFrame(self)
        self.speaking_controls_frame.grid(row=0, column=1, rowspan = 2, pady = 10)
        # self.volume_slider_label = customtkinter.CTkLabel(self.speaking_controls_frame, text="Volume")
        # self.volume_slider_label.grid(row=0, column=1)
        # self.volume_slider = customtkinter.CTkSlider(self.speaking_controls_frame, from_=0, to=100)
        # self.volume_slider.grid(row=1, column=1)

        self.pitch_slider_label = customtkinter.CTkLabel(self.speaking_controls_frame, text="Pitch")
        self.pitch_slider_label.grid(row=2, column=1)
        self.pitch_slider = customtkinter.CTkSlider(self.speaking_controls_frame, from_=-0.5, to=1.5, number_of_steps=20, command=self.pitch())
        self.pitch_slider.grid(row=3, column=1)
        self.pitch_slider.set(1.0)

        self.rate_slider_label = customtkinter.CTkLabel(self.speaking_controls_frame, text="Rate")
        self.rate_slider_label.grid(row=4, column=1)
        self.rate_slider = customtkinter.CTkSlider(self.speaking_controls_frame, from_=-1, to=1, number_of_steps=20, command=self.rate())
        self.rate_slider.grid(row=5, column=1)
        self.rate_slider.set(0.3)


        self.instruction_frame = customtkinter.CTkFrame(self)
        self.instruction_frame.grid(row=1, column=0)
        self.instructions_1 = customtkinter.CTkLabel(self.instruction_frame, text="1. Open Video with CC Turned On")
        self.instructions_1.grid(row=1, column=0)
        self.instructions_2 = customtkinter.CTkLabel(self.instruction_frame, text="2. Press Start Reading on this App")
        self.instructions_2.grid(row=2, column=0)
        self.instructions_3 = customtkinter.CTkLabel(self.instruction_frame, text="3. Wait and the App will Start Speaking")
        self.instructions_3.grid(row=3, column=0)



    # app takes time to load

    def start_stop_button(self):
        if self.reading_status:
            #self.ocr_engine.stop()
            #self.speech_engine.stop()
            self.reading_status = False
            self.button.configure(text="Start Reading")
        else:
            self.ocr_engine.start()
            self.speech_engine.start()
            #screen_shot_app = ScreenCaptureApp(self.ocr_engine)
            #screen_shot_app.mainloop()
            self.reading_status = True
            self.button.configure(text="Stop Reading")

    def pitch(self):
        self.speech_engine.set_pitch(self.pitch_slider.get())

    def rate(self):
        self.speech_engine.set_speed(self.rate_slider.get())



