from lib.aadraw import aaline, aacircle
from lib.vector import Vector
import pygame
import math


def v(src, i):
    if callable(src):
        return src(i)
    else:
        return src


def draw_line(surface, points, width, color):
    if len(points) < 2:
        return

    for i in range(len(points) - 1):
        curr = points[i]
        next = points[i + 1]

        angle = Vector.Angle(curr, next)
        polygon = [
            curr + Vector.Polar(angle + math.pi / 2, v(width, i) / 2),
            curr + Vector.Polar(angle - math.pi / 2, v(width, i) / 2),
            next + Vector.Polar(angle - math.pi / 2, v(width, i) / 2),
            next + Vector.Polar(angle + math.pi / 2, v(width, i) / 2),
        ]

        pygame.draw.polygon(surface, v(color, i), polygon)

        pygame.draw.circle(
            surface, v(color, i), (int(points[i].x), int(points[i].y)), v(width, i) / 2
        )

    pygame.draw.circle(
        surface,
        v(color, len(points) - 1),
        (int(points[-1].x), int(points[-1].y)),
        int(v(width, len(points) - 1) / 2),
    )


def draw_line_fast(surface, points, width, color):
    if len(points) < 2:
        return

    for i in range(len(points) - 1):
        curr = points[i]
        next = points[i + 1]

        pygame.draw.line(
            surface,
            v(color, i),
            (int(curr.x), int(curr.y)),
            (int(next.x), int(next.y)),
            int(v(width, i)),
        )

        pygame.draw.circle(
            surface, v(color, i), (int(points[i].x), int(points[i].y)), v(width, i) / 2
        )

    pygame.draw.circle(
        surface,
        v(color, len(points) - 1),
        (int(points[-1].x), int(points[-1].y)),
        int(v(width, len(points) - 1) / 2),
    )

    #     aacircle(
    #         surface,
    #         this_color,
    #         *map(int, points[i]),
    #         int(this_width / 2),
    #     )

    # aacircle(
    #     surface,
    #     this_color,
    #     *map(int, points[-1]),
    #     int(this_width / 2),
    # )


def draw_handles(screen, points, color, radius):
    for i, p in enumerate(points):
        aacircle(screen, v(color, i), *map(int, p), v(radius, i))
