import pygame
from pygame.locals import *
from lib.vector import Vector, distance_to_line
from lib.aadraw import aacircle, aaline
from lib.transform import piecewise, step_to, step_to_time
from math import sin, pi, floor
from playback import make_animations, interpolate


class Editor:
    HOVER_RANGE = 7
    HISTORY_SIZE = 100

    PRIMARY_COLOR = (255, 0, 0)
    HOVER_COLOR = (0, 0, 255)
    ALTERNATE_COLOR = (0, 255, 0)

    ANIMATE_COLOR = (0, 200, 255)

    def __init__(self, viewer, tendril=[[]]):
        self.viewer = viewer
        self.tendril = tendril
        self.history = []
        self.active = 0

        self.modified = False
        self.animating = False

        self.selecting = False
        self.drag_active = False
        self.drag_idx = 0
        self.drag_time = 0

        self.hovering_point = None
        self.hovering_line = None

        self.mouse_posn = Vector(0, 0)

        self.animating_pct = 0
        self.animations = []

        self.dimmer_surface = None

    def save(self):
        self.modified = True
        self.history.append([a[:] for a in self.tendril])

        if len(self.history) > Editor.HISTORY_SIZE:
            self.history.pop(0)

    def undo(self):
        if len(self.history) > 0:
            self.modified = True
            self.tendril = self.history.pop()

    def dragging(self):
        return self.drag_active and (
            self.drag_time > 100
            or Vector.Distance(self.mouse_posn, self.active_vein()[self.drag_idx])
            * self.viewer.zoom_scale()
            > Editor.HOVER_RANGE * 2
        )

    def active_vein(self):
        return self.tendril[self.active]

    def nearest_vein(self, posn):
        for curr, vein in enumerate(self.tendril):
            for idx in range(1, len(vein)):
                point1 = vein[idx]
                point2 = vein[idx - 1]

                if distance_to_line(point1, point2, posn) < Editor.HOVER_RANGE * 2:
                    return curr

    def nearest_point(self, posn):
        smallest = 0
        smallest_dist = 99999999

        for idx, point in enumerate(self.active_vein()):
            dist = Vector.Distance(posn, point)
            if dist < smallest_dist:
                smallest = idx
                smallest_dist = dist

        return smallest, smallest_dist

    def nearest_line(self, posn):
        if len(self.active_vein()) < 2:
            return None, None

        smallest = 0
        smallest_dist = distance_to_line(
            self.active_vein()[0], self.active_vein()[1], posn
        )

        for i in range(1, len(self.active_vein()) - 1):
            curr = self.active_vein()[i]
            next = self.active_vein()[i + 1]
            dist = distance_to_line(curr, next, posn)

            if dist < smallest_dist:
                smallest = i
                smallest_dist = dist

        return smallest, smallest_dist

    def draw(self, screen):
        if self.animating:
            self.animating_draw(screen)
        else:
            self.editing_draw(screen)

    def animating_draw(self, screen):
        longest_anim = max([len(a) for a in self.animations])
        idx = floor(self.animating_pct * longest_anim)

        if (
            self.dimmer_surface is None
            or self.dimmer_surface.get_size() != screen.get_size()
        ):
            self.dimmer_surface = pygame.Surface(screen.get_size())
            self.dimmer_surface.set_alpha(128)
            self.dimmer_surface.fill((0, 0, 0))

        screen.blit(self.dimmer_surface, (0, 0))

        for animation in self.animations:
            # # circle at each frame
            # for i in range(len(animation)):
            #     aacircle(
            #         screen,
            #         Editor.ANIMATE_COLOR,
            #         *map(int, self.viewer.world_to_screen(animation.get_frame(i))),
            #         3,
            #     )

            if idx >= animation.start:
                for i in range(idx - 1):
                    curr = animation.get_frame(i)
                    next = animation.get_frame(i + 1)

                    aaline(
                        screen,
                        Editor.ANIMATE_COLOR,
                        map(int, self.viewer.world_to_screen(curr)),
                        map(int, self.viewer.world_to_screen(next)),
                        width=3,
                    )

    def editing_draw(self, screen):
        for idx, vein in enumerate(self.tendril):
            if idx == self.active and not self.selecting:
                continue

            for i in range(len(vein) - 1):
                aaline(
                    screen,
                    Editor.ALTERNATE_COLOR,
                    map(int, self.viewer.world_to_screen(vein[i])),
                    map(int, self.viewer.world_to_screen(vein[i + 1])),
                    width=1,
                )

        if self.selecting:
            nearest = self.nearest_vein(self.mouse_posn)
            if nearest is not None:
                for i in range(len(self.tendril[nearest]) - 1):
                    aaline(
                        screen,
                        Editor.HOVER_COLOR,
                        map(int, self.viewer.world_to_screen(self.tendril[nearest][i])),
                        map(
                            int,
                            self.viewer.world_to_screen(self.tendril[nearest][i + 1]),
                        ),
                        width=1,
                    )

        if not self.selecting:
            for i in range(len(self.active_vein()) - 1):
                aaline(
                    screen,
                    (
                        Editor.HOVER_COLOR
                        if i == self.hovering_line
                        else Editor.PRIMARY_COLOR
                    ),
                    map(int, self.viewer.world_to_screen(self.active_vein()[i])),
                    map(int, self.viewer.world_to_screen(self.active_vein()[i + 1])),
                    width=1,
                )

            for i, point in enumerate(self.active_vein()):
                aacircle(
                    screen,
                    (
                        Editor.HOVER_COLOR
                        if i == self.hovering_point
                        else Editor.PRIMARY_COLOR
                    ),
                    *map(int, self.viewer.world_to_screen(point)),
                    3,
                )

    def event(self, event):
        if event.type == KEYDOWN and event.key == K_TAB:
            if self.animating:
                self.animating = False
            else:
                self.animations = make_animations(interpolate(self.tendril, scale=1), 0)
                self.animating_pct = 0
                self.animating = True

        if self.animating:
            self.animating_event(event)
        else:
            self.editing_event(event)

    def animating_event(self, event):
        pass

    def editing_event(self, event):
        if event.type == KEYDOWN:
            if event.key == K_LALT or event.key == K_RALT:
                self.selecting = True

            if event.key == K_BACKSPACE:
                if len(self.active_vein()) > 0:
                    self.save()
                    self.active_vein().pop()
                    self.hovering_point = None
                    self.hovering_line = None

            if event.key == K_z and pygame.key.get_mods() & KMOD_CTRL:
                self.undo()

            if event.key == K_n:
                self.save()
                self.tendril.append([])
                self.active = len(self.tendril) - 1

        if event.type == KEYUP:
            if event.key == K_LALT or event.key == K_RALT:
                self.selecting = False

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                idx, dist = self.nearest_point(self.viewer.screen_to_world(event.pos))

                if dist * self.viewer.zoom_scale() < Editor.HOVER_RANGE:
                    self.save()
                    self.drag_active = True
                    self.drag_idx = idx
                    self.drag_time = 0

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                if self.selecting:
                    nearest = self.nearest_vein(self.mouse_posn)
                    if nearest is not None:
                        self.active = nearest
                        self.selecting = False

                    return

                if not self.dragging():
                    self.save()
                    if self.hovering_line is not None:
                        self.active_vein().insert(
                            self.hovering_line + 1, self.mouse_posn
                        )
                    elif self.hovering_point is not None:
                        self.active_vein().pop(self.hovering_point)

                    else:
                        self.active_vein().append(self.mouse_posn)

                self.drag_active = False

        if event.type == MOUSEMOTION:
            self.mouse_posn = self.viewer.screen_to_world(event.pos)

            if self.dragging():
                self.active_vein()[self.drag_idx] = self.mouse_posn

            self.hovering_point = None
            self.hovering_line = None

            np_idx, np_dist = self.nearest_point(self.mouse_posn)
            if (
                np_idx is not None
                and np_dist * self.viewer.zoom_scale() < Editor.HOVER_RANGE
            ):
                self.hovering_point = np_idx
            else:
                nl_idx, nl_dist = self.nearest_line(self.mouse_posn)
                if (
                    nl_idx is not None
                    and nl_dist * self.viewer.zoom_scale() < Editor.HOVER_RANGE
                ):
                    self.hovering_line = nl_idx

    def update(self, ms):
        if self.animating:
            self.animating_update(ms)
        else:
            self.editing_update(ms)

    def animating_update(self, ms):
        self.animating_pct += ms / 1000
        if self.animating_pct > 1:
            self.animating_pct = 0

    def editing_update(self, ms):
        if self.drag_active:
            self.drag_time += ms
