import os
import tkinter as tk
from PIL import Image, ImageTk


class CreateButton:
    def __init__(self, parent):
        self.parent = parent

    def button(self, img1, img2, bg, command):
        current_dir = os.getcwd()
        image_1 = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, 'images', img1)))
        image_2 = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, 'images', img2)))

        btn = tk.Button(self.parent, image=image_1,
                        highlightthickness=0,
                        borderwidth=0,
                        cursor='hand2',
                        command=command,
                        relief='flat',
                        background=bg)
        btn.image_1 = image_1
        btn.image_2 = image_2
        btn.bind("<Enter>", lambda event, button=btn: self.on_enter(button))
        btn.bind("<Leave>", lambda event, button=btn: self.on_leave(button))
        return btn

    @staticmethod
    def on_leave(button):
        button['image'] = button.image_1

    @staticmethod
    def on_enter(button):
        button['image'] = button.image_2
