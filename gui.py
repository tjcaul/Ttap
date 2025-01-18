import customtkinter

customtkinter.set_default_color_theme("dark-blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("TTSS")
        self.geometry("400x150")
        self.grid_columnconfigure((0, 1), weight=1)

        self.welcome_label = customtkinter.CTkLabel(self, text="Welcome" )
        self .welcome_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
        self.button = customtkinter.CTkButton(self, text="Start Reading", command=self.button_callback)
        self.button.grid(row=1, column=0, padx=20, pady=20, sticky="ew", columnspan=2)

        self.volume_slider_label = customtkinter.CTkLabel(self, text="Volume")
        self.volume_slider_label.grid(row=2, column=0, padx=20, pady=20, sticky="ew", columnspan=2)
        self.volume_slider = customtkinter.CTkSlider(self, from_=0, to=100)
        self.volume_slider.grid(row=3, column=0, padx=20, pady=20, sticky="ew", columnspan=2)


    def button_callback(self):
        print("button pressed")

app = App()
app.mainloop()

