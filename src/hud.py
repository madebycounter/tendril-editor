import pygame


def draw_hud(
    screen,
    font,
    file,
    editor,
    viewer,
    fps,
    show_help=True,
    text_color=(255, 255, 255),
    bg_color=(0, 0, 0),
):
    vein_sizes = [len(vein) for vein in editor.tendril]

    if show_help:
        help_text1 = font.render(
            "Ctrl+O: open, Ctrl+S: save, Ctrl+I: set image, H: toggle help",
            True,
            text_color,
        )

        help_text2 = font.render(
            "N: new vein, ALT: select vein, BACK: delete node, TAB: toggle preview",
            True,
            text_color,
        )

        # render help text at bottom left of screen
        # draw boxes for text
        pygame.draw.rect(
            screen,
            bg_color,
            (
                0,
                screen.get_height() - help_text1.get_height() - help_text2.get_height(),
                help_text1.get_width(),
                help_text1.get_height(),
            ),
        )
        pygame.draw.rect(
            screen,
            bg_color,
            (
                0,
                screen.get_height() - help_text2.get_height(),
                help_text2.get_width(),
                help_text2.get_height(),
            ),
        )

        screen.blit(
            help_text1,
            (
                0,
                screen.get_height() - help_text1.get_height() - help_text2.get_height(),
            ),
        )
        screen.blit(
            help_text2,
            (0, screen.get_height() - help_text2.get_height()),
        )

    text1 = font.render(
        f"{file if file else 'untitled.vein'}{'*' if editor.modified else ''}",
        True,
        text_color,
    )
    text2 = font.render(
        f"vein {editor.active + 1}/{len(editor.tendril)}, nodes {vein_sizes[editor.active]}/{sum(vein_sizes)}",
        True,
        text_color,
    )
    text3 = font.render(
        f"zoom {viewer.zoom_level} ({round(viewer.zoom_scale(), 2)}x) {round(fps)} fps",
        True,
        text_color,
    )

    # draw box for text1 and text2 and text3
    pygame.draw.rect(screen, bg_color, (0, 0, text1.get_width(), text1.get_height()))
    pygame.draw.rect(
        screen,
        bg_color,
        (0, text1.get_height(), text2.get_width(), text2.get_height()),
    )
    pygame.draw.rect(
        screen,
        bg_color,
        (
            0,
            text1.get_height() + text2.get_height(),
            text3.get_width(),
            text3.get_height(),
        ),
    )

    screen.blit(text1, (0, 0))
    screen.blit(text2, (0, text1.get_height()))
    screen.blit(text3, (0, text1.get_height() + text2.get_height()))
