import pygame
import numpy as np
import math
from lib.aadraw import aacircle
from options import Options
from perlin_noise import PerlinNoise

OPTIONS_FILE = "options.cfg"
options = Options()
options.load(OPTIONS_FILE)


# def render_frame(animations, time, image, samples=500):
#     surface = pygame.Surface(image.get_size())
#     offset = 0.05
#     scale = image.get_height() / options.IMAGE_HEIGHT

#     for v in np.linspace(0, time, math.floor(samples * time)):
#         for a in animations:
#             state = a[v]

#             c = 255
#             if v > time - offset:
#                 c = 255 * (time - v) / offset

#             if state.visible:
#                 ns = pygame.Surface(image.get_size())
#                 aacircle(
#                     ns,
#                     (c, c, c),
#                     *map(int, state.position * scale),
#                     int(state.scale / 2 * scale),
#                 )
#                 surface.blit(ns, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

#     surface.blit(image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

#     return surface


# def render_frames(animations, image, samples=500, frames=500):
#     for z in range(frames):
#         o = f"render/frame{z:03d}.png"
#         x = render_frame(animations, z / frames, image, samples)
#         pygame.image.save(x, o)
#         print(f"Rendered {o} ({round(z / frames * 100, 2)}%)")


def render_frames(animations, image, samples=500, frames=500, tail=0.05):
    surface = pygame.Surface(image.get_size())
    tails = pygame.Surface(image.get_size())
    scale = image.get_height() / options.IMAGE_HEIGHT
    noise = PerlinNoise(seed=1)

    frame = 0
    start = 0
    while start < 1:
        frame_out = f"render/frames/{frame:03d}.png"

        ns = pygame.Surface(image.get_size())
        for time in np.linspace(start, start - tail, math.floor(samples * tail)):
            for anim in animations:
                keyframe = anim[time]
                intensity = (time - start) / tail * -255

                if keyframe.visible:
                    aacircle(
                        ns,
                        ((intensity,) * 3),
                        *map(int, keyframe.position * scale),
                        int(keyframe.scale / 2 * scale),
                    )


        surface.blit(ns, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        this_frame = surface.copy()
        this_frame.blit(image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
        pygame.image.save(this_frame, frame_out)
        print(f"Rendered {frame}.png ({round(start * 100, 2)}%)")


        step = (noise(frame / frames) + 1)
        start += (1 / frames) * step * 1.5
        frame += 1



if __name__ == "__main__":
    from tendril import Tendril
    from animate import make_animations

    p = "A:\\projects\\nava onti\\music videos\\vfx + sfx\\tendrils\\veins\\image1.vein"
    tendril = Tendril.load(p)
    animations = make_animations(tendril)
    image = pygame.image.load("sample.png")

    render_frames(animations, image, frames=500)
