import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk, JpegImagePlugin
from tkinter.messagebox import askyesno


class Window:

    def __init__(self, root=None, width=1280, height=720):
        self.root = root
        self.width = width
        self.height = height
        self.title = "Itay's Zoom Application"
        self.app_image = None

    def create_tk_window(self):
        """Creates tkinter window"""
        if self.root is None:
            self.root = tk.Tk()
        self.root.geometry(f"{self.width}x{self.height}")
        self.root.title(self.title)

        # Application logo
        self.app_image = tk.PhotoImage(file="zoom.png")
        self.root.iconphoto(False, self.app_image)
        return self.root

    def create_top_level_window(self):
        if self.root is None:
            self.root = self.create_tk_window()
        top_level = tk.Toplevel(self.root)
        top_level.geometry(f"{self.width}x{self.height}")
        top_level.title(f"{self.title} top level")

        # Application logo
        top_level.iconphoto(False, self.app_image)
        return top_level

    def create_label(self, master, img="black_screen.png", text="", x=0, y=0):
        """creates label to display image using tk"""
        if type(img) == str:
            img = Image.open(img)
        label = tk.Label(master, image=ImageTk.PhotoImage(img), text=text)
        label.pack(padx=x, pady=y)
        label.update()
        return label

    def update_label(self, label, img):
        """updating label with given image"""
        if type(img) == JpegImagePlugin.JpegImageFile:
            img = ImageTk.PhotoImage(img)

        label.configure(image=img)
        label.update()
        return

    def __confirm_closing(self):
        if askyesno(title='Exit', message='Close Window?'):
            return

    def confirm_closing_protocol(self):
        self.root.protocol("WM_DELETE_WINDOW", self.__confirm_closing)

    def mainloop(self):
        self.root.mainloop()

    def destroy(self):
        self.root.destroy()





