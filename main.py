import random
import sys
import pygame

try:
    from .config import (
        WIDTH,
        HEIGHT,
        FPS,
        BLACK,
        WHITE,
        TEXT_PRIMARY,
        TEXT_ACCENT,
    )
    from .entities import Paddle, Ball, FallingBonus
    from .levels import build_level
    from .ui import draw_text
except ImportError:
    from config import (
        WIDTH,
        HEIGHT,
        FPS,
        BLACK,
        WHITE,
        TEXT_PRIMARY,
        TEXT_ACCENT,
    )
    from entities import Paddle, Ball, FallingBonus
    from levels import build_level
    from ui import draw_text


def run_game() -> None:
    pygame.init()
    pygame.display.set_caption("Breakout")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    font_ui = pygame.font.SysFont("arial", 24)
    font_big = pygame.font.SysFont("arial", 46, bold=True)
    font_small = pygame.font.SysFont("arial", 18)

    paddle = Paddle()
    balls: list[Ball] = [Ball()]
    current_level = 1
    max_level = 2
    bricks = build_level(current_level)
    bonuses: list[FallingBonus] = []
    score = 0
    lives = 3
    game_state = "menu"

    base_paddle_width = 120
    expand_until = 0
    slow_until = 0
    power_until = 0
    slow_factor = 0.7
    level_start_delay_until = 0

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_state == "menu":
                    if event.key == pygame.K_RETURN:
                        paddle = Paddle()
                        balls = [Ball()]
                        current_level = 1
                        bricks = build_level(current_level)
                        bonuses = []
                        score = 0
                        lives = 3
                        expand_until = 0
                        slow_until = 0
                        power_until = 0
                        level_start_delay_until = now + 3000
                        game_state = "playing"
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_r and game_state in ("game_over", "win"):
                    game_state = "menu"

        keys = pygame.key.get_pressed()
        if game_state == "playing":
            paddle.update(keys)
            is_countdown_active = now < level_start_delay_until
            if not is_countdown_active:
                for ball in balls:
                    ball.update()

            if expand_until and now > expand_until:
                center_x = paddle.rect.centerx
                paddle.rect.width = base_paddle_width
                paddle.rect.centerx = center_x
                paddle.rect.x = max(0, min(WIDTH - paddle.rect.width, paddle.rect.x))
                expand_until = 0

            if slow_until and now > slow_until:
                for ball in balls:
                    ball.dx /= slow_factor
                    ball.dy /= slow_factor
                slow_until = 0

            for ball in balls:
                if ball.rect.colliderect(paddle.rect) and ball.dy > 0:
                    hit_pos = (ball.x - paddle.rect.centerx) / (paddle.rect.width / 2)
                    ball.dy = -abs(ball.dy)
                    ball.dx = ball.speed * 1.5 * hit_pos
                    ball.y = paddle.rect.top - ball.radius

                hit_brick = None
                for brick in bricks:
                    if ball.rect.colliderect(brick.rect):
                        hit_brick = brick
                        break

                if hit_brick:
                    overlap_left = ball.rect.right - hit_brick.rect.left
                    overlap_right = hit_brick.rect.right - ball.rect.left
                    overlap_top = ball.rect.bottom - hit_brick.rect.top
                    overlap_bottom = hit_brick.rect.bottom - ball.rect.top
                    min_overlap_x = min(overlap_left, overlap_right)
                    min_overlap_y = min(overlap_top, overlap_bottom)

                    if min_overlap_x < min_overlap_y:
                        ball.dx *= -1
                    else:
                        ball.dy *= -1

                    if power_until > now:
                        destroyed = True
                        hit_brick.hp = 0
                    else:
                        destroyed = hit_brick.hit()

                    if destroyed:
                        if hit_brick in bricks:
                            bricks.remove(hit_brick)
                        score += 100
                        if random.random() < 0.55:
                            bonus_type = random.choice(["expand", "slow", "power", "multiball"])
                            bonuses.append(FallingBonus(hit_brick.rect.centerx, hit_brick.rect.centery, bonus_type))
                    else:
                        score += 50

            for bonus in bonuses[:]:
                bonus.update()
                if bonus.rect.colliderect(paddle.rect):
                    if bonus.bonus_type == "expand":
                        center_x = paddle.rect.centerx
                        paddle.rect.width = 180
                        paddle.rect.centerx = center_x
                        paddle.rect.x = max(0, min(WIDTH - paddle.rect.width, paddle.rect.x))
                        expand_until = now + 8000
                    elif bonus.bonus_type == "slow":
                        if slow_until == 0:
                            for ball in balls:
                                ball.dx *= slow_factor
                                ball.dy *= slow_factor
                        slow_until = now + 7000
                    elif bonus.bonus_type == "power":
                        power_until = now + 8000
                    elif bonus.bonus_type == "multiball":
                        extra_balls: list[Ball] = []
                        for src in balls:
                            clone = Ball()
                            clone.x = src.x
                            clone.y = src.y
                            clone.dx = -src.dx if src.dx != 0 else random.choice([-1, 1]) * clone.speed
                            clone.dy = src.dy
                            if slow_until > now:
                                clone.dx *= slow_factor
                                clone.dy *= slow_factor
                            extra_balls.append(clone)
                        balls.extend(extra_balls)
                        if len(balls) > 6:
                            balls = balls[:6]
                    bonuses.remove(bonus)
                elif bonus.rect.top > HEIGHT:
                    bonuses.remove(bonus)

            balls = [ball for ball in balls if ball.y - ball.radius <= HEIGHT]
            if not balls:
                lives -= 1
                if lives <= 0:
                    game_state = "game_over"
                else:
                    balls = [Ball()]
                    balls[0].y = HEIGHT - 80
                    level_start_delay_until = now + 3000

            if not bricks:
                if current_level < max_level:
                    current_level += 1
                    bricks = build_level(current_level)
                    balls = [Ball()]
                    bonuses = []
                    expand_until = 0
                    slow_until = 0
                    power_until = 0
                    level_start_delay_until = now + 3000
                else:
                    game_state = "win"

        screen.fill(BLACK)

        if game_state == "menu":
            draw_text(screen, font_big, "BREAKOUT", WIDTH // 2, 190, TEXT_ACCENT, center=True)
            draw_text(screen, font_ui, "ENTER - start game", WIDTH // 2, 280, TEXT_PRIMARY, center=True)
            draw_text(screen, font_ui, "ESC - quit", WIDTH // 2, 315, TEXT_PRIMARY, center=True)
            draw_text(screen, font_small, "Bonus E: wider paddle", WIDTH // 2, 375, TEXT_PRIMARY, center=True)
            draw_text(screen, font_small, "Bonus S: slower ball", WIDTH // 2, 400, TEXT_PRIMARY, center=True)
            draw_text(screen, font_small, "Bonus P: faster brick breaking", WIDTH // 2, 425, TEXT_PRIMARY, center=True)
            draw_text(screen, font_small, "Bonus M: doubles balls", WIDTH // 2, 450, TEXT_PRIMARY, center=True)
        else:
            for brick in bricks:
                brick.draw(screen)
            for bonus in bonuses:
                bonus.draw(screen, font_small)
            paddle.draw(screen)
            for ball in balls:
                ball.draw(screen)

            draw_text(screen, font_ui, f"Score: {score}", 20, 14)
            draw_text(screen, font_ui, f"Lives: {lives}", WIDTH - 120, 14)
            draw_text(screen, font_small, f"Level: {current_level}", WIDTH // 2 - 30, 14, TEXT_PRIMARY)

            if expand_until > now:
                draw_text(screen, font_small, "E active", WIDTH // 2 - 55, 14, TEXT_PRIMARY)
            if slow_until > now:
                draw_text(screen, font_small, "S active", WIDTH // 2 + 20, 14, TEXT_PRIMARY)
            if power_until > now:
                draw_text(screen, font_small, "P active", WIDTH // 2 + 95, 14, TEXT_PRIMARY)

            if game_state == "playing" and now < level_start_delay_until:
                seconds_left = (level_start_delay_until - now + 999) // 1000
                draw_text(screen, font_big, str(seconds_left), WIDTH // 2, HEIGHT // 2, WHITE, center=True)

            if game_state == "game_over":
                draw_text(screen, font_big, "GAME OVER", WIDTH // 2, HEIGHT // 2 - 20, TEXT_PRIMARY, center=True)
                draw_text(screen, font_ui, "Press R to return to menu", WIDTH // 2, HEIGHT // 2 + 30, TEXT_PRIMARY, center=True)
            elif game_state == "win":
                draw_text(screen, font_big, "YOU WIN!", WIDTH // 2, HEIGHT // 2 - 20, TEXT_PRIMARY, center=True)
                draw_text(screen, font_ui, "Press R to return to menu", WIDTH // 2, HEIGHT // 2 + 30, TEXT_PRIMARY, center=True)

        pygame.display.flip()

run_game()