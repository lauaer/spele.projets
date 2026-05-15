import random
import pygame

from config import WIDTH, HEIGHT, BLUE, YELLOW, RED, ORANGE, GREEN, BLACK, WHITE


class Paddle:
    def __init__(self) -> None:
        self.width = 120
        self.height = 16
        self.speed = 8
        self.rect = pygame.Rect((WIDTH - self.width) // 2, HEIGHT - 48, self.width, self.height)

    def update(self, keys: pygame.key.ScancodeWrapper) -> None:
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, BLUE, self.rect, border_radius=8)


class Ball:
    def __init__(self) -> None:
        self.radius = 10
        self.reset()

    def reset(self) -> None:
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.speed = 5
        self.dx = random.choice([-1, 1]) * self.speed
        self.dy = self.speed

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

    def update(self) -> None:
        self.x += self.dx
        self.y += self.dy

        if self.x - self.radius <= 0:
            self.x = self.radius
            self.dx *= -1
        elif self.x + self.radius >= WIDTH:
            self.x = WIDTH - self.radius
            self.dx *= -1

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.dy *= -1

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)


class Brick:
    def __init__(self, x: int, y: int, width: int, height: int, hp: int = 1) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.hp = hp

    def hit(self) -> bool:
        self.hp -= 1
        return self.hp <= 0

    def color(self) -> tuple[int, int, int]:
        if self.hp == 3:
            return RED
        if self.hp == 2:
            return ORANGE
        return GREEN

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.color(), self.rect, border_radius=5)
        pygame.draw.rect(screen, BLACK, self.rect, width=2, border_radius=5)


class FallingBonus:
    def __init__(self, x: int, y: int, bonus_type: str) -> None:
        self.size = 22
        self.rect = pygame.Rect(x - self.size // 2, y - self.size // 2, self.size, self.size)
        self.speed = 3
        self.bonus_type = bonus_type

    def update(self) -> None:
        self.rect.y += self.speed

    def draw(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        if self.bonus_type == "expand":
            color = BLUE
            label = "E"
        elif self.bonus_type == "slow":
            color = ORANGE
            label = "S"
        elif self.bonus_type == "power":
            color = RED
            label = "P"
        else:
            color = GREEN
            label = "M"

        pygame.draw.rect(screen, color, self.rect, border_radius=6)
        pygame.draw.rect(screen, WHITE, self.rect, width=2, border_radius=6)
        text = font.render(label, True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)