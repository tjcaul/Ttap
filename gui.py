from termios import OCRNL

import customtkinter
import ocr

customtkinter.set_default_color_theme("dark-blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("TTSS")
        self.geometry("400x150")
        self.grid_columnconfigure((0, 1), weight=1)

        self.welcome_label = customtkinter.CTkLabel(self, text="Welcome" )
        self .welcome_label.grid(row=0, column=0, columnspan=1)
        self.button = customtkinter.CTkButton(self, text="Start Reading", command=self.start_button)
        self.button.grid(row=1, column=0)

        self.speaking_controls_frame = customtkinter.CTkFrame(self)
        self.speaking_controls_frame.grid(row=0, column=1, rowspan=2)
        self.volume_slider_label = customtkinter.CTkLabel(self.speaking_controls_frame, text="Volume")
        self.volume_slider_label.grid(row=0, column=1, columnspan=1)
        self.volume_slider = customtkinter.CTkSlider(self.speaking_controls_frame, from_=0, to=100)
        self.volume_slider.grid(row=1, column=1)


    def start_button(self):
        new_session = ocr.OCR()
        #TODO: how to start the OCR session
        ocr.OCR.start()

app = App()
app.mainloop()

