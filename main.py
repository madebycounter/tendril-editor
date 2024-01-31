import sys
import pygame
from pygame.locals import *
from viewer import Viewer
from editor import Editor, distance_to_line
import draw
import load


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


while True:
    for event in pygame.event.get():
        viewer.event(event)

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_LALT or event.key == K_RALT:
                selecting = True

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
                veins[current] = editor.points
                veins.append([])
                current = len(veins) - 1
                editor.set_points(veins[current])

        if event.type == MOUSEBUTTONUP:
            if selecting:
                mouse = viewer.translate(viewer.mouse_posn)

                for cur, vein in enumerate(veins):
                    for idx, point in enumerate(vein):
                        if idx == 0:
                            continue

                        point1 = viewer.translate(point)
                        point2 = viewer.translate(vein[idx - 1])
                        if distance_to_line(point1, point2, mouse) < 10:
                            veins[current] = editor.points
                            current = cur
                            editor.set_points(veins[current])
                            selecting = False
                            break
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

    draw.draw_ui(screen, editor, veins, current, save_file)

    editor.update()

    pygame.display.flip()
    clock.tick(60)
