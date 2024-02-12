import pygame
from pygame.locals import *
from .vector import Vector


class ImageViewer:
    def __init__(
        self,
        image,
        pan_button=2,
        zoom_in_button=4,
        zoom_out_button=5,
        zoom_speed=0.4,
        max_zoom=8,
        min_zoom=-8,
        image_height=1000,
    ):
        self.pan_button = pan_button
        self.zoom_in_button = zoom_in_button
        self.zoom_out_button = zoom_out_button
        self.zoom_speed = zoom_speed
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom
        self.image_height = image_height

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

        for level in range(self.min_zoom, self.max_zoom + 1):
            self.image_cache[level] = pygame.transform.scale(
                self.image,
                Vector(
                    self.image_height * ar,
                    self.image_height,
                )
                * self.zoom_scale(level=level),
            )

    def zoom(self, delta, center):
        if self.zoom_level + delta > self.max_zoom:
            return

        if self.zoom_level + delta < self.min_zoom:
            return

        old_zoom = self.zoom_scale()
        self.zoom_level += delta

        amount = self.zoom_scale() - old_zoom
        delta = center * amount

        self.posn -= delta

    def zoom_scale(self, level=None):
        if level is not None:
            return (1 + self.zoom_speed) ** level
        return (1 + self.zoom_speed) ** self.zoom_level

    def screen_to_world(self, posn):
        return (posn - self.posn) / self.zoom_scale()

    def world_to_screen(self, posn):
        return posn * self.zoom_scale() + self.posn

    def event(self, event):
        if event.type == MOUSEBUTTONDOWN:
            mouse_posn = Vector(*event.pos)

            if event.button == self.pan_button:
                self.pan_origin = mouse_posn
                self.pan_active = True

            if event.button == self.zoom_in_button:
                self.zoom(1, self.screen_to_world(mouse_posn))

            if event.button == self.zoom_out_button:
                self.zoom(-1, self.screen_to_world(mouse_posn))

        if event.type == MOUSEMOTION:
            self.mouse_posn = self.screen_to_world(event.pos)

            if self.pan_active:
                self.posn += Vector(*event.pos) - self.pan_origin
                self.pan_origin = Vector(*event.pos)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == self.pan_button:
                self.pan_active = False

    def draw(self, screen):
        if self.zoom_level not in self.image_cache:
            self.image_cache[self.zoom_level] = pygame.transform.scale(
                self.image, Vector(*self.image.get_size()) * self.zoom_scale()
            )

        scaled_image = self.image_cache[self.zoom_level]
        screen.blit(scaled_image, self.posn)
