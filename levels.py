from config import WIDTH
from entities import Brick


def build_level(rows: int = 6, cols: int = 10) -> list[Brick]:
    bricks: list[Brick] = []
    margin_x = 40
    margin_top = 70
    gap = 8
    brick_w = (WIDTH - margin_x * 2 - gap * (cols - 1)) // cols
    brick_h = 28

    for r in range(rows):
        for c in range(cols):
            x = margin_x + c * (brick_w + gap)
            y = margin_top + r * (brick_h + gap)
            hp = 1 + (r // 2)
            bricks.append(Brick(x, y, brick_w, brick_h, hp=min(hp, 3)))

    return bricks