import threading
import pygame
import numpy as np
import math
from lib.aadraw import aacircle
from options import Options

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
    scale = image.get_height() / options.IMAGE_HEIGHT

    for frame in range(frames):
        outfile = f"render/frame{frame:03d}.png"
        start = frame / frames

        for time in np.linspace(start - tail, start, math.floor(samples * tail)):
            ns = pygame.Surface(image.get_size())
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
        pygame.image.save(this_frame, outfile)
        print(f"Rendered {outfile} ({round((start + tail) * 100, 2)}%)")


if __name__ == "__main__":
    from tendril import Tendril
    from animate import make_animations

    p = "A:\\projects\\nava onti\\music videos\\vfx + sfx\\tendrils\\veins\\image1.vein"
    tendril = Tendril.load(p)
    animations = make_animations(tendril)
    image = pygame.image.load("sample.png")

    render_frames(animations, image, frames=500)
