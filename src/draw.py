from lib.aadraw import aaline, aacircle
from lib.vector import Vector
import pygame
import math


def draw_line(surface, points, width, color):
    for i in range(len(points) - 1):
        if callable(color):
            this_color = color(i)
        else:
            this_color = color

        if callable(width):
            this_width = width(i)
        else:
            this_width = width

        curr = points[i]
        next = points[i + 1]

        angle = Vector.Angle(curr, next)
        polygon = [
            curr + Vector.Polar(angle + math.pi / 2, this_width / 2),
            curr + Vector.Polar(angle - math.pi / 2, this_width / 2),
            next + Vector.Polar(angle - math.pi / 2, this_width / 2),
            next + Vector.Polar(angle + math.pi / 2, this_width / 2),
        ]

        pygame.draw.polygon(surface, this_color, polygon)

        pygame.draw.circle(
            surface, this_color, (int(points[i].x), int(points[i].y)), this_width / 2
        )

    pygame.draw.circle(
        surface,
        this_color,
        (int(points[-1].x), int(points[-1].y)),
        int(this_width / 2),
    )


def draw_line_fast(surface, points, width, color):
    for i in range(len(points) - 1):
        if callable(color):
            this_color = color(i)
        else:
            this_color = color

        if callable(width):
            this_width = width(i)
        else:
            this_width = width

        curr = points[i]
        next = points[i + 1]

        pygame.draw.line(
            surface,
            this_color,
            (int(curr.x), int(curr.y)),
            (int(next.x), int(next.y)),
            int(this_width),
        )

        pygame.draw.circle(
            surface, this_color, (int(points[i].x), int(points[i].y)), this_width / 2
        )

    pygame.draw.circle(
        surface,
        this_color,
        (int(points[-1].x), int(points[-1].y)),
        int(this_width / 2),
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
        if callable(color):
            this_color = color(i)
        else:
            this_color = color

        if callable(radius):
            this_radius = radius(i)
        else:
            this_radius = radius

        aacircle(screen, this_color, *map(int, p), this_radius)
