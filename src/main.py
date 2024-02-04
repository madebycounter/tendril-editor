import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import sys
import pygame
import traceback
import datetime
from pygame.locals import *
from lib.imageviewer import ImageViewer
from editor import Editor
from load import prompt_vein, prompt_image, load_vein, save_vein, save_on_exit
from hud import draw_hud

pygame.init()
pygame.font.init()

size = (800, 600)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size, RESIZABLE, vsync=True)
pygame.display.set_caption("William's Veiny Tendril Editor")

image = pygame.image.load("sample.png")
viewer = ImageViewer(image)
editor = Editor(viewer)
ms = 0

font = pygame.font.SysFont("Comic Sans MS", 16)
active_file = ""
show_help = True


def save_check():
    global active_file
    if editor.modified and save_on_exit():
        save()


def save():
    global active_file

    if active_file == "":
        active_file = prompt_vein(save=True)

    if active_file is not None:
        save_vein(editor.tendril, active_file)
        editor.modified = False


def main():
    global editor, viewer, active_file, show_help

    while True:
        for event in pygame.event.get():
            viewer.event(event)
            editor.event(event)

            if event.type == QUIT:
                save_check()
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_F12 and pygame.key.get_mods() & KMOD_CTRL:
                    save_check()
                    1 / 0

                if event.key == K_o and pygame.key.get_mods() & KMOD_CTRL:
                    load_file = prompt_vein()

                    if load_file:
                        active_file = load_file
                        editor = Editor(viewer, load_vein(load_file))

                if event.key == K_s and pygame.key.get_mods() & KMOD_CTRL:
                    save()

                if event.key == K_i and pygame.key.get_mods() & KMOD_CTRL:
                    load_image = prompt_image()
                    if load_image:
                        viewer = ImageViewer(pygame.image.load(load_image))
                        editor.viewer = viewer

                if event.key == K_h:
                    show_help = not show_help

        screen.fill((0, 0, 0))
        viewer.draw(screen)
        editor.draw(screen)

        draw_hud(
            screen,
            font,
            active_file,
            editor,
            viewer,
            int(clock.get_fps()),
            show_help=show_help,
        )

        pygame.display.flip()

        ms = clock.tick(120)
        editor.update(ms)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(editor.tendril)
        print(traceback.format_exc())

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        veins_file = f"crash_{timestamp}.vein"

        save_vein(editor.tendril, veins_file)
        print(f"Tendril saved to {veins_file}.")

        print(
            "\n\nGood job, you broke it. Do not close this window. Notify William immediately and he can attempt to recover save data."
        )
