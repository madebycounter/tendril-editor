import pygame
from pygame.locals import *
from lib.vector import Vector, distance_to_line
from lib.aadraw import aacircle, aaline
from animate import make_animations
from tendril import Tendril


class Editor:
    def __init__(
        self,
        viewer,
        tendril=Tendril(),
        hover_range=7,
        history_size=100,
        primary_color=(255, 0, 0),
        hover_color=(0, 0, 255),
        alternate_color=(0, 255, 0),
        parent_color=(0, 170, 0),
        animate_color=(0, 200, 255),
        animate_samples=50,
        animate_speed=5000,
    ):
        self.hover_range = hover_range
        self.history_size = history_size
        self.primary_color = primary_color
        self.hover_color = hover_color
        self.alternate_color = alternate_color
        self.parent_color = parent_color
        self.animate_color = animate_color
        self.animate_samples = animate_samples
        self.animate_speed = animate_speed

        self.viewer = viewer
        self.tendril = tendril
        self.history = []
        self.active = self.tendril.id

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
        self.history.append((self.active, self.tendril.copy()))

        if len(self.history) > self.history_size:
            self.history.pop(0)

    def undo(self):
        if len(self.history) > 0:
            self.modified = True
            self.active, self.tendril = self.history.pop()

    def dragging(self):
        return self.drag_active and (
            self.drag_time > 100
            or Vector.Distance(self.mouse_posn, self.active_vein()[self.drag_idx])
            * self.viewer.zoom_scale()
            > self.hover_range * 2
        )

    def active_vein(self):
        return self.tendril.get_by_id(self.active)

    def nearest_tendril(self, posn):
        for vein in self.tendril.all():
            for idx in range(1, len(vein)):
                point1 = vein[idx]
                point2 = vein[idx - 1]

                if distance_to_line(point1, point2, posn) < self.hover_range * 2:
                    return vein

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
        step = 1.0 / self.animate_samples

        if (
            self.dimmer_surface is None
            or self.dimmer_surface.get_size() != screen.get_size()
        ):
            self.dimmer_surface = pygame.Surface(screen.get_size())
            self.dimmer_surface.set_alpha(128)
            self.dimmer_surface.fill((0, 0, 0))

        screen.blit(self.dimmer_surface, (0, 0))

        for animation in self.animations:
            i = 0
            while i < self.animating_pct:
                curr = animation[i].position
                next = animation[i + step].position

                i += step

                if animation[i].visible:
                    aaline(
                        screen,
                        self.animate_color,
                        map(int, self.viewer.world_to_screen(curr)),
                        map(int, self.viewer.world_to_screen(next)),
                        width=3,
                    )

                # aacircle(
                #     screen,
                #     self.animate_color,
                #     *map(int, self.viewer.world_to_screen(curr)),
                #     3,
                # )

    def editing_draw(self, screen):
        for vein in self.tendril.all():
            if vein.id == self.active and not self.selecting:
                continue

            if self.tendril.parent_of(self.active) == vein.id:
                color = self.parent_color
            else:
                color = self.alternate_color

            for i in range(len(vein) - 1):
                aaline(
                    screen,
                    color,
                    map(int, self.viewer.world_to_screen(vein[i])),
                    map(int, self.viewer.world_to_screen(vein[i + 1])),
                    width=1,
                )

        if self.selecting:
            nearest = self.nearest_tendril(self.mouse_posn)
            if nearest is not None:
                for i in range(len(nearest) - 1):
                    aaline(
                        screen,
                        self.hover_color,
                        map(int, self.viewer.world_to_screen(nearest[i])),
                        map(
                            int,
                            self.viewer.world_to_screen(nearest[i + 1]),
                        ),
                        width=1,
                    )

        if not self.selecting:
            for i in range(len(self.active_vein()) - 1):
                aaline(
                    screen,
                    (
                        self.hover_color
                        if i == self.hovering_line
                        else self.primary_color
                    ),
                    map(int, self.viewer.world_to_screen(self.active_vein()[i])),
                    map(int, self.viewer.world_to_screen(self.active_vein()[i + 1])),
                    width=1,
                )

            for i, point in enumerate(self.active_vein()):
                aacircle(
                    screen,
                    (
                        self.hover_color
                        if i == self.hovering_point
                        else self.primary_color
                    ),
                    *map(int, self.viewer.world_to_screen(point)),
                    3,
                )

    def event(self, event):
        if event.type == KEYDOWN and event.key == K_TAB:
            if self.animating:
                self.animating = False
            else:
                self.animations = make_animations(self.tendril)
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
                self.mouse_update()
                if len(self.active_vein()) > 0:
                    self.save()
                    self.active_vein().pop()
                    self.hovering_point = None
                    self.hovering_line = None

            if event.key == K_z and pygame.key.get_mods() & KMOD_CTRL:
                self.undo()

            if event.key == K_n:
                self.save()

                new = Tendril()
                self.active_vein().add_child(new)
                self.active = new.id

        if event.type == KEYUP:
            if event.key == K_LALT or event.key == K_RALT:
                self.selecting = False

        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.mouse_update()
                idx, dist = self.nearest_point(self.viewer.screen_to_world(event.pos))

                if dist * self.viewer.zoom_scale() < self.hover_range:
                    self.save()
                    self.drag_active = True
                    self.drag_idx = idx
                    self.drag_time = 0

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.mouse_update()
                if self.selecting:
                    nearest = self.nearest_tendril(self.mouse_posn)
                    if nearest is not None:
                        self.active = nearest.id
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
                        self.hovering_point = None
                        self.hovering_line = None
                    else:
                        self.active_vein().append(self.mouse_posn)

                self.drag_active = False
                self.mouse_update(event)

        if event.type == MOUSEMOTION:
            self.mouse_update(event=event)

    def mouse_update(self, event=None):
        if event:
            self.mouse_posn = self.viewer.screen_to_world(event.pos)

        if self.dragging():
            self.active_vein()[self.drag_idx] = self.mouse_posn

        self.hovering_point = None
        self.hovering_line = None

        np_idx, np_dist = self.nearest_point(self.mouse_posn)
        if np_idx is not None and np_dist * self.viewer.zoom_scale() < self.hover_range:
            self.hovering_point = np_idx
        else:
            nl_idx, nl_dist = self.nearest_line(self.mouse_posn)
            if (
                nl_idx is not None
                and nl_dist * self.viewer.zoom_scale() < self.hover_range
            ):
                self.hovering_line = nl_idx

    def update(self, ms):
        if self.animating:
            self.animating_update(ms)
        else:
            self.editing_update(ms)

    def animating_update(self, ms):
        self.animating_pct += ms / self.animate_speed
        if self.animating_pct > 1:
            self.animating_pct = 0

    def editing_update(self, ms):
        if self.drag_active:
            self.drag_time += ms
