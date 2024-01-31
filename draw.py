import pygame


PATH_COLOR = (255, 0, 0)
POINT_COLOR = (255, 0, 0)
ACTIVE_COLOR = (0, 0, 255)
INACTIVE_COLOR = (0, 255, 0)
BACKGROUND_COLOR = (0, 0, 0)

pygame.font.init()
font = pygame.font.SysFont("Comic Sans MS", 16)

scaled_cache = {}


def draw_viewer(screen, image, viewer):
    screen.fill(BACKGROUND_COLOR)

    if viewer._zoom in scaled_cache:
        scaled_image = scaled_cache[viewer._zoom]
    else:
        scaled_image = viewer.resize_image(image)
        scaled_cache[viewer._zoom] = scaled_image

    screen.blit(scaled_image, viewer.translate((0, 0)))


def draw_active_vein(screen, editor, points):
    viewer = editor.viewer

    if len(points) > 1:
        pygame.draw.lines(
            screen,
            PATH_COLOR,
            False,
            [viewer.translate(point) for point in points],
            2,
        )

    if editor.active_line is not None:
        pygame.draw.line(
            screen,
            ACTIVE_COLOR,
            viewer.translate(points[editor.active_line]),
            viewer.translate(points[editor.active_line + 1]),
            2,
        )

    for idx, point in enumerate(points):
        if idx == editor.active_point:
            pygame.draw.circle(screen, ACTIVE_COLOR, viewer.translate(point), 4)
        else:
            pygame.draw.circle(screen, POINT_COLOR, viewer.translate(point), 4)


def draw_vein(screen, editor, points):
    if len(points) > 1:
        pygame.draw.lines(
            screen,
            INACTIVE_COLOR,
            False,
            [editor.viewer.translate(point) for point in points],
            2,
        )


def draw_selected_vein(screen, editor, points):
    if len(points) > 1:
        pygame.draw.lines(
            screen,
            INACTIVE_COLOR,
            False,
            [editor.viewer.translate(point) for point in points],
            4,
        )


def draw_ui(screen, editor, veins, current, save_file):
    if save_file:
        if editor.modified:
            text = font.render(f"{save_file}*", True, (255, 255, 255))
        else:
            text = font.render(f"{save_file}", True, (255, 255, 255))
    else:
        text = font.render("untitled.vein*", True, (255, 255, 255))

    pygame.draw.rect(screen, (0, 0, 0), (0, 0, text.get_width(), text.get_height()))
    screen.blit(text, (0, 0))

    status = f"vein {current+1}/{len(veins)}, nodes {len(veins[current])}/{sum([ len(a) for a in veins ])}"
    status_text = font.render(
        status,
        True,
        (255, 255, 255),
    )

    # blit the text to the screen underneath one another
    pygame.draw.rect(
        screen,
        (0, 0, 0),
        (0, text.get_height(), status_text.get_width(), status_text.get_height()),
    )
    screen.blit(status_text, (0, text.get_height()))
