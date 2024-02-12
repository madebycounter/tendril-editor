import pygame
from pygame.locals import *
from .vector import Vector


class ImageViewer:
    PAN_BUTTON = 2
    ZOOM_IN_BUTTON = 4
    ZOOM_OUT_BUTTON = 5
    ZOOM_SPEED = 0.4
    MAX_ZOOM = 8
    MIN_ZOOM = -8
    IMAGE_HEIGHT = 1000

    def __init__(self, image):
        self.original = image
        self.image = image.convert(16)
        self.zoom_level = 0
        self.posn = Vector(0, 0)

        self.image_cache = {}
        self.populate_cache()

        self.pan_active = False
        self.pan_origin = Vector(0, 0)

    def populate_cache(self):
        ar = self.image.get_width() / self.image.get_height()

        for level in range(ImageViewer.MIN_ZOOM, ImageViewer.MAX_ZOOM + 1):
            self.image_cache[level] = pygame.transform.scale(
                self.image,
                Vector(
                    ImageViewer.IMAGE_HEIGHT * ar,
                    ImageViewer.IMAGE_HEIGHT,
                )
                * self.zoom_scale(level=level),
            )

    def zoom(self, delta, center):
        if self.zoom_level + delta > ImageViewer.MAX_ZOOM:
            return

        if self.zoom_level + delta < ImageViewer.MIN_ZOOM:
            return

        old_zoom = self.zoom_scale()
        self.zoom_level += delta

        amount = self.zoom_scale() - old_zoom
        delta = center * amount

        self.posn -= delta

    def zoom_scale(self, level=None):
        if level is not None:
            return (1 + ImageViewer.ZOOM_SPEED) ** level
        return (1 + ImageViewer.ZOOM_SPEED) ** self.zoom_level

    def screen_to_world(self, posn):
        return (posn - self.posn) / self.zoom_scale()

    def world_to_screen(self, posn):
        return posn * self.zoom_scale() + self.posn

    def event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            mouse_posn = Vector(*event.pos)

            if event.button == ImageViewer.PAN_BUTTON:
                self.pan_origin = mouse_posn
                self.pan_active = True

            if event.button == ImageViewer.ZOOM_IN_BUTTON:
                self.zoom(1, self.screen_to_world(mouse_posn))

            if event.button == ImageViewer.ZOOM_OUT_BUTTON:
                self.zoom(-1, self.screen_to_world(mouse_posn))

        if event.type == MOUSEMOTION:
            self.mouse_posn = self.screen_to_world(event.pos)

            if self.pan_active:
                self.posn += Vector(*event.pos) - self.pan_origin
                self.pan_origin = Vector(*event.pos)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == ImageViewer.PAN_BUTTON:
                self.pan_active = False

    def draw(self, screen):
        if self.zoom_level not in self.image_cache:
            self.image_cache[self.zoom_level] = pygame.transform.scale(
                self.image, Vector(*self.image.get_size()) * self.zoom_scale()
            )

        scaled_image = self.image_cache[self.zoom_level]
        screen.blit(scaled_image, self.posn)
