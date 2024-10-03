import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BACKGROUND_COLOR = (135, 206, 235)  # Sky blue
PLATFORM_COLOR = (139, 69, 19)      # Saddle brown
PLAYER_COLOR = (0, 128, 255)        # Vivid blue
ENEMY_COLOR = (255, 0, 0)           # Red

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platform Fighter")

clock = pygame.time.Clock()

# Gravity constant
GRAVITY = 0.5

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(color)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.velocity_y = 0
        self.speed = 5
        self.on_ground = False
        self.attack_cooldown = 0

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_w] and self.on_ground:
            self.velocity_y = -15
            self.on_ground = False
        if keys[pygame.K_SPACE]:
            self.attack()

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

    def attack(self):
        if self.attack_cooldown == 0:
            # Implement attack logic here
            self.attack_cooldown = 30  # Cooldown frames

    def update(self):
        self.handle_keys()
        self.apply_gravity()
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height=20):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((40, 60))
        self.image.fill(color)
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.velocity_y = 0
        self.on_ground = False

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

    def update(self):
        self.apply_gravity()

# Create sprite groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Create instances
player = Player(SCREEN_WIDTH / 4, SCREEN_HEIGHT - 300, PLAYER_COLOR)
enemy = Enemy(3 * SCREEN_WIDTH / 4, SCREEN_HEIGHT - 300, ENEMY_COLOR)
all_sprites.add(player)
all_sprites.add(enemy)
enemies.add(enemy)

# Create platforms
ground = Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH)
platform1 = Platform(200, SCREEN_HEIGHT - 150, 200)
platform2 = Platform(500, SCREEN_HEIGHT - 250, 200)
platforms.add(ground, platform1, platform2)
all_sprites.add(ground, platform1, platform2)

def check_collisions():
    # Player collision with platforms
    hits = pygame.sprite.spritecollide(player, platforms, False)
    if hits:
        player.rect.bottom = hits[0].rect.top
        player.velocity_y = 0
        player.on_ground = True
    else:
        player.on_ground = False

    # Enemy collision with platforms
    enemy_hits = pygame.sprite.spritecollide(enemy, platforms, False)
    if enemy_hits:
        enemy.rect.bottom = enemy_hits[0].rect.top
        enemy.velocity_y = 0
        enemy.on_ground = True
    else:
        enemy.on_ground = False

    # Player attack collision with enemy
    if player.attack_cooldown > 0 and player.rect.colliderect(enemy.rect):
        # Simple knockback effect
        enemy.velocity_y = -10
        if player.rect.centerx < enemy.rect.centerx:
            enemy.rect.x += 20
        else:
            enemy.rect.x -= 20

# Game loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update
    all_sprites.update()
    check_collisions()

    # Draw
    screen.fill(BACKGROUND_COLOR)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
