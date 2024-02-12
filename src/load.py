import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
import pickle


def save_on_exit():
    res = mb.askquestion(
        "Exit Application", "You have unsaved changes, save before exiting?"
    )
    if res == "yes":
        return True
    else:
        return False


def prompt_image():
    root = tk.Tk()
    root.withdraw()

    return filedialog.askopenfilename(
        title="Open File", filetypes=(("Images", "*.png *.jpg *.jpeg *.bmp"),)
    )


def prompt_vein(save=False):
    root = tk.Tk()
    root.withdraw()

    fp = None

    if save:
        fp = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".vein",
            filetypes=(("Vein File", "*.vein"),),
        )

    else:
        fp = filedialog.askopenfilename(
            title="Open File", filetypes=(("Vein File", "*.vein"),)
        )

    if fp == "" or fp == ".vein":
        return None
    else:
        return fp


def load_image():
    path = prompt_image()
    return pygame.image.load(path)


def load_vein(path):
    return pickle.load(open(path, "rb"))


def save_vein(veins, path):
    if not path.endswith(".vein"):
        path += ".vein"

    pickle.dump(veins, open(path, "wb"))
