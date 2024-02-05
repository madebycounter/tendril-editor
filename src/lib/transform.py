from .vector import Vector
from math import floor


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


def line_length(points):
    length = 0
    for i in range(len(points) - 1):
        length += Vector.Distance(points[i], points[i + 1])

    return length


def step_to(points, pct):
    dist = line_length(points) * pct

    current = 0
    for i in range(len(points) - 1):
        length = Vector.Distance(points[i], points[i + 1])

        if current + length > dist:
            return points[i] + (points[i + 1] - points[i]) * (dist - current) / length

        current += length

    return points[-1]


def step_to_time(points, pct):
    posn = (len(points) - 1) * pct
    idx = floor(posn)
    extra = posn - idx

    return points[idx] + (points[idx + 1] - points[idx]) * extra


def piecewise(points, modifier=lambda x: 1, N=120):
    # calculate length lines formed by array of points
    step = line_length(points) / N

    # calculate points along lines
    new_points = [points[0]]
    current = 0
    for i in range(len(points) - 1):
        length = Vector.Distance(points[i], points[i + 1])

        i_step = step * modifier(len(new_points) / N)

        while current + i_step < length:
            current += i_step
            new_points.append(
                points[i] + (points[i + 1] - points[i]) * current / length,
            )

        current -= length

    new_points.append(points[-1])

    return new_points
