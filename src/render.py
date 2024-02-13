import pygame
import numpy as np
import math

from lib.aadraw import aacircle


def render_frame(animations, time, size, samples=1000):
    surface = pygame.Surface(size)

    for v in np.linspace(0, time, math.floor(samples * time)):
        for a in animations:
            state = a[v]
            c = 255 * (v / time)

            if state.visible:
                aacircle(
                    surface,
                    (c, c, c),
                    *map(int, state.position),
                    10,
                )

    pygame.image.save(surface, "frame.png")


if __name__ == "__main__":
    from tendril import Tendril
    from animate import make_animations

    p = "A:\\projects\\nava onti\\music videos\\vfx + sfx\\tendrils\\veins\\image1.vein"
    tendril = Tendril.load(p)
    animations = make_animations(tendril)
    image = pygame.image.load("sample.png")

    print(tendril)
    print(animations)

    render_frame(animations, 0.5, image.get_size())
