import sys
import pygame
from pygame.locals import *
from viewer import Viewer
import load

NEAREST = 0
LINEAR = 1
MOVE = 2


PATH_COLOR = (255, 0, 0)
POINT_COLOR = (255, 0, 0)
ACTIVE_COLOR = (0, 0, 255)
BACKGROUND_COLOR = (0, 0, 0)


class Editor:
    def __init__(self, viewer):
        self.viewer = viewer
        self.points = []
        self.previous = []
        self.modified = False

        self.drag_active = False
        self.drag_idx = 0
        self.drag_frames = 0

        self.active_point = None
        self.active_line = None

    def nearest_point(self):
        mouse = self.viewer.translate(self.viewer.mouse_posn)

        for idx, point in enumerate(self.points):
            point = self.viewer.translate(point)

            if distance_between(mouse, point) < 10:
                return idx

    def nearest_line(self):
        if len(self.points) < 2:
            return None

        mouse = self.viewer.translate(self.viewer.mouse_posn)

        for i in range(len(self.points) - 1):
            curr = self.viewer.translate(self.points[i])
            next = self.viewer.translate(self.points[i + 1])

            if distance_to_line(curr, next, mouse) < 10:
                return i

    def update(self):
        if self.drag_active:
            self.drag_frames += 1

        self.active_point = self.nearest_point()

        if self.active_point is None:
            self.active_line = self.nearest_line()
        else:
            self.active_line = None

        if (
            self.active_point is None
            and self.active_line is None
            and len(self.points) > 1
        ):
            head_dist = distance_between(self.viewer.mouse_posn, self.points[0])
            tail_dist = distance_between(self.viewer.mouse_posn, self.points[-1])

            if head_dist < tail_dist:
                self.active_point = 0
            else:
                self.active_point = len(self.points) - 1

    def create_savepoint(self):
        self.previous.append(self.points[:])
        self.modified = True

        if len(self.previous) > 10:
            self.previous.pop(0)

    def event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                if len(self.points) > 0:
                    self.points.pop()

            if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                if len(self.previous) > 0:
                    self.points = self.previous.pop()

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.create_savepoint()
                idx = self.nearest_point()

                if idx is not None:
                    self.drag_active = True
                    self.drag_idx = idx
                    self.drag_frames = 0

        if event.type == MOUSEMOTION:
            if self.drag_active and (
                self.drag_frames > 10
                or distance_between(
                    self.viewer.translate(self.viewer.mouse_posn),
                    self.viewer.translate(self.points[self.drag_idx]),
                )
                > 10
            ):
                self.points[self.drag_idx] = self.viewer.mouse_posn

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                if self.drag_active and (
                    self.drag_frames > 10
                    or distance_between(
                        self.viewer.translate(self.viewer.mouse_posn),
                        self.viewer.translate(self.points[self.drag_idx]),
                    )
                    > 10
                ):
                    self.drag_active = False
                    return
                elif self.drag_active:
                    self.drag_active = False

                posn = self.viewer.screen_to_world(event.pos)
                self.create_savepoint()

                nearest_point = self.nearest_point()
                if nearest_point is not None:
                    self.points.pop(nearest_point)
                    return

                nearest_line = self.nearest_line()
                if nearest_line is not None:
                    self.points.insert(nearest_line + 1, posn)
                    return

                if len(self.points) == 0:
                    self.points.append(posn)
                    return

                head_dist = distance_between(posn, self.points[0])
                tail_dist = distance_between(posn, self.points[-1])

                if head_dist < tail_dist:
                    self.points.insert(0, posn)
                else:
                    self.points.append(posn)


def distance_to_line(a, b, c):
    x1, y1 = a
    x2, y2 = b
    x3, y3 = c

    try:
        m1 = (y2 - y1) / (x2 - x1)
    except ZeroDivisionError:
        m1 = 99999

    try:
        m2 = -1 / m1
    except ZeroDivisionError:
        m2 = 99999

    b1 = y1 - m1 * x1
    b2 = y3 - m2 * x3

    x = (b2 - b1) / (m1 - m2)
    y = m1 * x + b1

    if x < min(x1, x2) or x > max(x1, x2):
        return min(distance_between(a, c), distance_between(b, c))

    return distance_between((x, y), c)


def distance_between(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


pygame.init()
pygame.font.init()
pygame.display.set_caption("William's Veiny Tendril Editor")

font = pygame.font.SysFont("Comic Sans MS", 16)

size = (800, 600)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size, RESIZABLE, vsync=True)
viewer = Viewer(screen)

image = load.load_image()
save_file = ""


editor = Editor(viewer)

scaled_cache = {
    viewer._zoom: viewer.resize_image(image),
}

while True:
    for event in pygame.event.get():
        viewer.event(event)

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_CTRL:
                if save_file == "":
                    fp = load.prompt_vein(save=True)
                    if fp is None:
                        continue
                    else:
                        save_file = fp

                load.save_vein(editor.points, save_file)
                editor.modified = False

            if event.key == pygame.K_o and pygame.key.get_mods() & pygame.KMOD_CTRL:
                save_file = load.prompt_vein()

                if save_file is not None:
                    editor.points = load.load_vein(save_file)
                    editor.modified = False

        viewer.event(event)
        editor.event(event)

    editor.update()

    screen.fill(BACKGROUND_COLOR)

    if viewer._zoom in scaled_cache:
        scaled_image = scaled_cache[viewer._zoom]
    else:
        scaled_image = viewer.resize_image(image)
        scaled_cache[viewer._zoom] = scaled_image

    screen.blit(scaled_image, viewer.translate((0, 0)))

    if len(editor.points) > 1:
        pygame.draw.lines(
            screen,
            PATH_COLOR,
            False,
            [viewer.translate(point) for point in editor.points],
            2,
        )

    if editor.active_line is not None:
        pygame.draw.line(
            screen,
            ACTIVE_COLOR,
            viewer.translate(editor.points[editor.active_line]),
            viewer.translate(editor.points[editor.active_line + 1]),
            2,
        )

    for idx, point in enumerate(editor.points):
        if idx == editor.active_point:
            pygame.draw.circle(screen, ACTIVE_COLOR, viewer.translate(point), 4)
        else:
            pygame.draw.circle(screen, POINT_COLOR, viewer.translate(point), 4)

    if save_file:
        if editor.modified:
            text = font.render(f"{save_file}*", True, (255, 255, 255))
        else:
            text = font.render(f"{save_file}", True, (255, 255, 255))
    else:
        text = font.render("untitled.vein*", True, (255, 255, 255))

    pygame.draw.rect(screen, (0, 0, 0), (0, 0, text.get_width(), text.get_height()))
    screen.blit(text, (0, 0))

    pygame.display.flip()
    clock.tick(60)
