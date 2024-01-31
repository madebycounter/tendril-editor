import sys
import pygame
from pygame.locals import *


FILE = "image2.vein"


with open(FILE, "r") as f:
    veins = [
        list(zip(*(iter([float(v) for v in l.split(",")]),) * 2))
        for l in filter(lambda x: x != "", f.read().split("\n"))
    ]


def normalize(veins):
    flat = [p for v in veins for p in v]

    orig = veins[0][0]

    tl = (
        min(flat, key=lambda x: x[0])[0],
        min(flat, key=lambda x: x[1])[1],
    )

    br = (
        max(flat, key=lambda x: x[0])[0],
        max(flat, key=lambda x: x[1])[1],
    )

    size = (
        br[0] - tl[0],
        br[1] - tl[1],
    )

    sf = 1 / size[0]

    return [
        [
            (
                (p[0] - orig[0]) * sf,
                (p[1] - orig[1]) * sf,
            )
            for p in v
        ]
        for v in veins
    ]


def piecewise(points, N=120):
    # calculate length lines formed by array of points
    length = 0
    for i in range(1, len(points)):
        length += (
            (points[i][0] - points[i - 1][0]) ** 2
            + (points[i][1] - points[i - 1][1]) ** 2
        ) ** 0.5

    step = length / N

    # calculate points along lines
    new_points = []
    current = 0
    for i in range(1, len(points)):
        length = (
            (points[i][0] - points[i - 1][0]) ** 2
            + (points[i][1] - points[i - 1][1]) ** 2
        ) ** 0.5

        while current + step < length:
            current += step
            new_points.append(
                (
                    points[i - 1][0]
                    + (points[i][0] - points[i - 1][0]) * current / length,
                    points[i - 1][1]
                    + (points[i][1] - points[i - 1][1]) * current / length,
                )
            )

        current -= length

    return new_points


veins = normalize(veins)

POINTS = piecewise(veins[0], N=50)


pygame.init()
pygame.display.set_caption("Tendril Viewer")


size = (800, 600)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size, vsync=True)


while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

    for point in POINTS:
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (int(point[0] * size[0]), int(point[1] * size[1] + size[1] / 2)),
            2,
        )

    pygame.display.flip()
    clock.tick(60)
