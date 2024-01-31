import pygame
from pygame.locals import *


def calculate_zoom(level, speed):
    return (1 + speed) ** level


class Viewer:
    PAN_BUTTON = 2
    ZOOM_IN_BUTTON = 4
    ZOOM_OUT_BUTTON = 5
    ZOOM_SPEED = 0.1
    MAX_ZOOM = 10
    MIN_ZOOM = 0.1

    def __init__(self, screen):
        self.screen = screen
        self._posn = (0, 0)
        self._zoom_level = 0
        self._zoom = calculate_zoom(self._zoom_level, Viewer.ZOOM_SPEED)

        self.pan_active = False
        self.pan_origin = (0, 0)
        self.mouse_posn = (0, 0)

    def zoom_in(self):
        self._zoom_level += 1
        new = calculate_zoom(self._zoom_level, Viewer.ZOOM_SPEED)

        if new > Viewer.MAX_ZOOM:
            self._zoom_level -= 1
            return

        self.zoom(new)

    def zoom_out(self):
        self._zoom_level -= 1
        new = calculate_zoom(self._zoom_level, Viewer.ZOOM_SPEED)

        if new < Viewer.MIN_ZOOM:
            self._zoom_level += 1
            return

        self.zoom(new)

    def zoom(self, new):
        amount = new - self._zoom

        self._zoom = new

        dx = self.mouse_posn[0] * amount
        dy = self.mouse_posn[1] * amount

        self._posn = (self._posn[0] - dx, self._posn[1] - dy)

    def event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            if event.button == Viewer.PAN_BUTTON:
                self.pan_origin = event.pos
                self.pan_active = True

            if event.button == Viewer.ZOOM_IN_BUTTON:
                self.zoom_in()

            if event.button == Viewer.ZOOM_OUT_BUTTON:
                self.zoom_out()

        if event.type == MOUSEMOTION:
            self.mouse_posn = self.screen_to_world(event.pos)

            if self.pan_active:
                self._posn = (
                    self._posn[0] + event.pos[0] - self.pan_origin[0],
                    self._posn[1] + event.pos[1] - self.pan_origin[1],
                )
                self.pan_origin = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == Viewer.PAN_BUTTON:
                self.pan_active = False

    def screen_to_world(self, posn):
        return (
            (posn[0] - self._posn[0]) / self._zoom,
            (posn[1] - self._posn[1]) / self._zoom,
        )

    def resize_image(self, image):
        return pygame.transform.scale(
            image, (self.scale(image.get_width()), self.scale(image.get_height()))
        )

    def translate(self, posn):
        return (
            (posn[0] * self._zoom) + self._posn[0],
            (posn[1] * self._zoom) + self._posn[1],
        )

    def scale(self, value):
        return value * self._zoom
