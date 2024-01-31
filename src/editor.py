import pygame
from pygame.locals import *


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

    def nearest_point(self, dist=6):
        mouse = self.viewer.translate(self.viewer.mouse_posn)

        for idx, point in enumerate(self.points):
            point = self.viewer.translate(point)

            if distance_between(mouse, point) < dist:
                return idx

    def nearest_line(self, dist=6):
        if len(self.points) < 2:
            return None

        mouse = self.viewer.translate(self.viewer.mouse_posn)

        for i in range(len(self.points) - 1):
            curr = self.viewer.translate(self.points[i])
            next = self.viewer.translate(self.points[i + 1])

            if distance_to_line(curr, next, mouse) < dist:
                return i

    def update(self):
        if self.drag_active:
            self.drag_frames += 1

        self.active_point = self.nearest_point()

        if self.active_point is None:
            self.active_line = self.nearest_line()
        else:
            self.active_line = None

    def set_points(self, points):
        self.points = points
        self.previous = []

        self.drag_active = False
        self.drag_idx = 0
        self.drag_frames = 0

        self.active_point = None
        self.active_line = None

    def create_savepoint(self):
        if len(self.previous) and self.previous[-1] == self.points:
            return

        self.previous.append(self.points[:])
        self.modified = True

        if len(self.previous) > 10:
            self.previous.pop(0)

    def event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                if len(self.points) > 0:
                    self.points.pop()
                    self.active_point = None
                    self.active_line = None

            if event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                if len(self.previous) > 0:
                    self.points = self.previous.pop()

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                idx = self.nearest_point()

                if idx is not None:
                    self.create_savepoint()
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

                nearest_point = self.nearest_point(dist=5)
                if nearest_point is not None:
                    self.points.pop(nearest_point)
                    return

                nearest_line = self.nearest_line()
                if nearest_line is not None:
                    self.points.insert(nearest_line + 1, posn)
                    return

                self.points.append(posn)
