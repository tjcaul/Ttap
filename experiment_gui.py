import wx
import pywinctl

class FancyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='X')
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.SetTransparent(90)
        self.Show(True)
        window = pywinctl.getAllWindows()
        print(len(window))

    def on_close(self, event):
        """Handles the window close event."""

        self.Destroy()


app = wx.App()
f = FancyFrame()
app.MainLoop()
