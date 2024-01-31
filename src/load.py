import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import tkinter as tk
from tkinter import filedialog


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
    veins = []

    with open(path, "r") as f:
        raw = f.read().split("\n")

    for vein in raw:
        if len(vein) == 0:
            continue

        this = []
        split = vein.split(",")
        if len(split) % 2 != 0:
            raise Exception("Invalid vein file")

        for i in range(0, len(split), 2):
            this.append((float(split[i]), float(split[i + 1])))

        veins.append(this)

    return veins


def save_vein(veins, path):
    if not path.endswith(".vein"):
        path += ".vein"

    with open(path, "w") as f:
        for vein in veins:
            for idx, point in enumerate(vein):
                f.write(f"{point[0]},{point[1]}")
                if idx < len(vein) - 1:
                    f.write(",")
            f.write("\n")
