import os
import tkinter as tk
from PIL import Image, ImageTk


class CreateButton:
    def __init__(self, parent):
        self.parent = parent
        self.buttons = []

    def button(self, img1, img2, bg, command):
        current_dir = os.getcwd()
        image_1 = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, 'images', img1)))
        image_2 = ImageTk.PhotoImage(Image.open(os.path.join(current_dir, 'images', img2)))

        btn = tk.Button(self.parent, image=image_1,
                        borderwidth=0,
                        cursor='hand2',
                        command=command,
                        relief='flat',
                        background=bg)
        btn.image_1 = image_1
        btn.image_2 = image_2
        btn.bind("<Enter>", lambda event, button=btn: self.on_enter(button))
        btn.bind("<Leave>", lambda event, button=btn: self.on_leave(button))

        self.buttons.append(btn)
        return btn

    def on_leave(self, button):
        button['image'] = button.image_1

    def on_enter(self, button):
        button['image'] = button.image_2