import tkinter as tk

from ocr import OCR


class ScreenCaptureApp(tk.Tk):
    ocr_engine: OCR

    def __init__(self, ocr_engine : OCR):
        self.ocr_engine = ocr_engine

        super().__init__()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set window size to screen size but keep title bar
        self.geometry(f"{screen_width}x{screen_height}")
        self.attributes("-alpha", 0.5)  # Make the window transparent
        self.configure(bg='black')
        # self.overrideredirect(True)

        self.start_x = None
        self.start_y = None
        self.rect_id = None

        self.canvas = tk.Canvas(self, cursor="cross", bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline='red', width=2)

    def on_drag(self, event):
        self.canvas.coords(self.rect_id, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        self.withdraw()  # Hide UI before capturing
        x1, y1, x2, y2 = self.start_x, self.start_y, event.x, event.y
        if x1 > x2: x1, x2 = x2, x1
        if y1 > y2: y1, y2 = y2, y1

        #screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
        # main and gui and instructions
        #self.save_screenshot(screenshot)
        self.ocr_engine.set_bounding_box(x1, y1, x2, y2)
        self.ocr_engine.start()
        self.destroy()
        print("hello")
        return

    # def save_screenshot(self, image):
    #     file_path = filedialog.asksaveasfilename(defaultextension=".png",
    #                                              filetypes=[("PNG files", "*.png"),
    #                                                         ("JPEG files", "*.jpg"),
    #                                                         ("All Files", "*.*")])
    #     if file_path:
    #         image.save(file_path)



if __name__ == "__main__":

    app = ScreenCaptureApp()
    app.mainloop()
