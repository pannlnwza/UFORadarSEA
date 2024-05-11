import os
import tkinter as tk
from PIL import Image, ImageTk


class CreateButton:
    """A class to create buttons with hover effects using images."""
    def __init__(self, parent):
        """
        Initialize the CreateButton class with a parent widget.

        :param parent: The parent widget for the button.
        :type parent: tkinter.Tk or tkinter.Frame
        """
        self.parent = parent

    def button(self, img1: str, img2: str, bg: str, command):
        """
        Create a button with images and hover effects.

        :param img1: The filename of the first image for the button.
        :type img1: str
        :param img2: The filename of the second image for the button (for hover effect).
        :type img2: str
        :param bg: The background color of the button.
        :type bg: str
        :param command: The function to be called when the button is clicked.
        :type command: function
        :return: The created button widget.
        :rtype: tkinter.Button
        """
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
        """
        Change the button image to the original image when the mouse leaves the button.
        """
        button['image'] = button.image_1

    @staticmethod
    def on_enter(button):
        """
        Change the button image to the hover image when the mouse enters the button.
        """
        button['image'] = button.image_2
