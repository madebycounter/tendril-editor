import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import sys
import pygame
import datetime
import pickle
import base64
import traceback
from pygame.locals import *
from viewer import Viewer
from editor import Editor, distance_to_line
import draw
import load


from tkinter import messagebox as mb


def save_on_exit():
    res = mb.askquestion(
        "Exit Application", "You have unsaved changes, save before exiting?"
    )
    if res == "yes":
        return True
    else:
        return False


pygame.init()
pygame.display.set_caption("William's Veiny Tendril Editor")


size = (800, 600)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size, RESIZABLE, vsync=True)
viewer = Viewer(screen)

image = load.load_image()
save_file = ""


editor = Editor(viewer)
veins = [editor.points]
current = 0


selecting = False


def select_closest_vein():
    mouse = viewer.translate(viewer.mouse_posn)

    for cur, vein in enumerate(veins):
        for idx, point in enumerate(vein):
            if idx == 0:
                continue

            point1 = viewer.translate(point)
            point2 = viewer.translate(vein[idx - 1])
            if distance_to_line(point1, point2, mouse) < 10:
                return cur


try:
    while True:
        for event in pygame.event.get():
            viewer.event(event)

            if event.type == QUIT:
                should_save = save_on_exit()

                if should_save:
                    if save_file == "":
                        fp = load.prompt_vein(save=True)
                        if fp is None:
                            continue
                        else:
                            save_file = fp

                    veins[current] = editor.points
                    load.save_vein(veins, save_file)

                print("Program exited without a crash. Woohoo!")

                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_LALT or event.key == K_RALT:
                    selecting = True

                if event.key == K_F12 and pygame.key.get_mods() & KMOD_CTRL:
                    1 / 0

                if event.key == K_s and pygame.key.get_mods() & KMOD_CTRL:
                    if save_file == "":
                        fp = load.prompt_vein(save=True)
                        if fp is None:
                            continue
                        else:
                            save_file = fp

                    veins[current] = editor.points
                    load.save_vein(veins, save_file)
                    editor.modified = False

                if event.key == K_o and pygame.key.get_mods() & KMOD_CTRL:
                    save_file = load.prompt_vein()

                    if save_file is not None:
                        veins = load.load_vein(save_file)
                        editor.set_points(veins[0])
                        editor.points = veins[0]
                        editor.modified = False

                        veins[0] = editor.points
                        current = 0

                if event.key == K_n and pygame.key.get_mods() & KMOD_CTRL:
                    if len(veins[current]) > 0:
                        veins[current] = editor.points
                        veins.append([])
                        current = len(veins) - 1
                        editor.set_points(veins[current])

            if event.type == MOUSEBUTTONUP:
                if selecting:
                    closest = select_closest_vein()

                    if closest is not None:
                        veins[current] = editor.points

                        current = closest
                        editor.set_points(veins[current])
                        selecting = False
                        continue

            if event.type == KEYUP:
                if event.key == K_LALT or event.key == K_RALT:
                    selecting = False

            viewer.event(event)

            if not selecting:
                editor.event(event)

        draw.draw_viewer(screen, image, viewer)

        if not selecting:
            for idx, vein in enumerate(veins):
                if idx != current:
                    draw.draw_vein(screen, editor, vein)

            draw.draw_active_vein(screen, editor, editor.points)
        else:
            closest = select_closest_vein()
            for idx, vein in enumerate(veins):
                if idx == closest:
                    draw.draw_selected_vein(screen, editor, vein)
                else:
                    draw.draw_vein(screen, editor, vein)

        draw.draw_ui(screen, editor, veins, current, save_file, clock.get_fps())

        editor.update()

        pygame.display.flip()
        clock.tick(60)
except Exception as e:
    print(veins)
    print(traceback.format_exc())

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    veins_file = f"crash_{timestamp}_veins"
    points_file = f"crash_{timestamp}_points"
    pickle_file = f"crash_{timestamp}_pickle.pickle"

    load.save_vein(veins, veins_file)
    print(f"Veins saved to {veins_file}.")

    load.save_vein([editor.points], points_file)
    print(f"Points saved to {points_file}.")

    try:
        save_data = {
            "veins": veins,
            "points": editor.points,
            "current": current,
            "save_file": save_file,
            "selecting": selecting,
            "editor": {
                "drag_active": editor.drag_active,
                "drag_idx": editor.drag_idx,
                "drag_frames": editor.drag_frames,
                "active_point": editor.active_point,
                "active_line": editor.active_line,
                "modified": editor.modified,
            },
            "viewer": {
                "zoom": viewer._zoom,
                "zoom_level": viewer._zoom_level,
                "posn": viewer._posn,
                "pan_active": viewer.pan_active,
                "pan_origin": viewer.pan_origin,
                "mouse_posn": viewer.mouse_posn,
            },
        }

        with open(pickle_file, "wb") as f:
            pickle.dump(save_data, f)
        print(f"Pickle data saved to {pickle_file}.")
    except Exception as e2:
        print(traceback.format_exc())
        print("Failed to save pickle data. Sorry.")

    print(
        "\n\nGood job, you broke it. Do not close this window. Notify William immediately and he can attempt to recover save data."
    )
