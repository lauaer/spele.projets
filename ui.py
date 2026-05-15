import pygame
from config import WHITE


def draw_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    x: int,
    y: int,
    color: tuple[int, int, int] = WHITE,
    center: bool = False,
    with_outline: bool = True,
    outline_color: tuple[int, int, int] = (0, 0, 0),
) -> None:
    if with_outline:
        outline_surface = font.render(text, True, outline_color)
        outline_rect = outline_surface.get_rect()
        if center:
            outline_rect.center = (x, y)
        else:
            outline_rect.topleft = (x, y)
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            screen.blit(outline_surface, outline_rect.move(dx, dy))

    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)