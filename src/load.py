import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox as mb
import pickle
from lib.vector import Vector, distance_to_line
from tendril import Tendril


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


def find_connections(tendril, vein_no, threshold=1):
    vein = tendril[vein_no]
    connections = {}

    for i in range(len(vein) - 1):
        curr = vein[i]
        next = vein[i + 1]

        for j in range(vein_no + 1, len(tendril)):
            dist = distance_to_line(curr, next, tendril[j][0])
            if dist < threshold:
                if j not in connections:
                    connections[j] = (dist, i)
                else:
                    if dist < connections[j][0]:
                        connections[j] = (dist, i)

    for k in connections:
        d1 = Vector.Distance(vein[connections[k][1]], tendril[k][0])
        d2 = Vector.Distance(vein[connections[k][1] + 1], tendril[k][0])
        if d2 < d1:
            connections[k] = (connections[k][0], connections[k][1] + 1)

    return {connections[k][1]: k for k in connections}


def legacy_to_tendril(legacy, current=0):
    vein = legacy[current]
    tendril = Tendril(data=vein)

    connections = find_connections(legacy, current)
    for c in connections:
        tendril.add_child(legacy_to_tendril(legacy, connections[c]))

    return tendril


def load_vein_legacy(path):
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
            this.append(Vector(float(split[i]), float(split[i + 1])))

        veins.append(this)

    return veins


def load_vein(path):
    try:
        vein = pickle.load(open(path, "rb"))
        for t in vein.all():
            if not hasattr(t, "width"):
                t.width = 1
        return vein
    except pickle.UnpicklingError:
        print("Error unpickling, trying to load legacy format")
        return legacy_to_tendril(load_vein_legacy(path))


def save_vein(veins, path):
    if not path.endswith(".vein"):
        path += ".vein"

    pickle.dump(veins, open(path, "wb"))
