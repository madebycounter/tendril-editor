import os
import sys

from tendril import Tendril

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
from options import Options

OPTIONS_FILE = "options.cfg"
options = Options()
options.load(OPTIONS_FILE)

pygame.init()
pygame.font.init()

size = (800, 600)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size, RESIZABLE, vsync=True)
pygame.display.set_caption("William's Veiny Tendril Editor")

if len(sys.argv) > 1:
    image = pygame.image.load(sys.argv[1])
else:
    image = pygame.image.load("sample.png")

if len(sys.argv) > 2:
    tendril = Tendril.load(sys.argv[2])
else:
    tendril = Tendril()


viewer = ImageViewer(
    image,
    pan_button=options.PAN_BUTTON,
    zoom_in_button=options.ZOOM_IN_BUTTON,
    zoom_out_button=options.ZOOM_OUT_BUTTON,
    zoom_speed=options.ZOOM_SPEED,
    max_zoom=options.MAX_ZOOM,
    min_zoom=options.MIN_ZOOM,
    image_height=options.IMAGE_HEIGHT,
)

editor = Editor(
    viewer,
    tendril=tendril,
    hover_range=options.HOVER_RANGE,
    history_size=options.HISTORY_SIZE,
    primary_color=options.PRIMARY_COLOR,
    hover_color=options.HOVER_COLOR,
    alternate_color=options.ALTERNATE_COLOR,
    parent_color=options.PARENT_COLOR,
    animate_color=options.ANIMATE_COLOR,
    animate_samples=options.ANIMATE_SAMPLES,
    animate_speed=options.ANIMATE_SPEED,
)

ms = 0

font = pygame.font.SysFont(options.FONT_NAME, options.FONT_SIZE)
active_file = ""
show_help = True


def save_check():
    if editor.modified and save_on_exit():
        return save()
    return True


def save():
    global active_file

    if not active_file:
        active_file = prompt_vein(save=True)

    if active_file:
        save_vein(editor.tendril, active_file)
        editor.modified = False
        return True


def main():
    global editor, viewer, active_file, show_help

    while True:
        for event in pygame.event.get():
            viewer.event(event)
            editor.event(event)

            if event.type == QUIT:
                if save_check():
                    options.save(OPTIONS_FILE)
                    pygame.quit()
                    sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_F12 and pygame.key.get_mods() & KMOD_CTRL:
                    if save_check():
                        1 / 0

                if event.key == K_o and pygame.key.get_mods() & KMOD_CTRL:
                    load_file = prompt_vein()

                    if load_file:
                        active_file = load_file
                        editor = Editor(
                            viewer,
                            load_vein(load_file),
                            hover_range=options.HOVER_RANGE,
                            history_size=options.HISTORY_SIZE,
                            primary_color=options.PRIMARY_COLOR,
                            hover_color=options.HOVER_COLOR,
                            alternate_color=options.ALTERNATE_COLOR,
                            parent_color=options.PARENT_COLOR,
                            animate_color=options.ANIMATE_COLOR,
                            animate_samples=options.ANIMATE_SAMPLES,
                            animate_speed=options.ANIMATE_SPEED,
                        )

                if event.key == K_s and pygame.key.get_mods() & KMOD_CTRL:
                    save()

                if event.key == K_i and pygame.key.get_mods() & KMOD_CTRL:
                    load_image = prompt_image()
                    if load_image:
                        viewer = ImageViewer(pygame.image.load(load_image))
                        editor.viewer = viewer

                if event.key == K_h:
                    show_help = not show_help

        screen.fill(options.BACKGROUND_COLOR)
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
            text_color=options.TEXT_COLOR,
            bg_color=options.TEXT_BOX_COLOR,
        )

        pygame.display.flip()

        ms = clock.tick(60)
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
