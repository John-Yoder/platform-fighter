import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BACKGROUND_COLOR = (135, 206, 235)   # Sky blue
PLATFORM_COLOR = (139, 69, 19)       # Saddle brown
PLAYER_COLOR = (0, 128, 255)         # Vivid blue
ENEMY_COLOR = (255, 0, 0)            # Red
ATTACK_FLASH_COLOR = (255, 255, 0)   # Yellow
TEXT_COLOR = (0, 0, 0)               # Black

# Death borders
LEFT_BORDER = -100
RIGHT_BORDER = SCREEN_WIDTH + 100
TOP_BORDER = -100
BOTTOM_BORDER = SCREEN_HEIGHT + 100

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D Platform Fighter")

clock = pygame.time.Clock()

# Gravity constant
GRAVITY = 0.5

# Game states
MENU = 'menu'
PLAYING = 'playing'
GAME_OVER = 'game_over'

# Font for text
font = pygame.font.SysFont(None, 48)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.original_image = pygame.Surface((40, 60))
        self.original_image.fill(color)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.velocity_y = 0
        self.speed = 7
        self.on_ground = False
        self.attack_cooldown = 0
        self.is_attacking = False
        self.flash_duration = 5
        self.flash_counter = 0
        self.damage = 0  # Damage percentage

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_w] and self.on_ground:
            self.velocity_y = -15
            self.on_ground = False
        if keys[pygame.K_s]:
            self.is_falling_through = True
        else:
            self.is_falling_through = False
        if keys[pygame.K_SPACE]:
            self.attack()

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

    def attack(self):
        if self.attack_cooldown == 0:
            self.is_attacking = True
            self.flash_counter = self.flash_duration
            self.attack_cooldown = 30  # Cooldown frames

    def take_damage(self, amount):
        self.damage += amount
        # Calculate knockback based on damage
        knockback_x = 10 + (self.damage / 100) * 20  # More horizontal knockback
        knockback_y = -5 - (self.damage / 100) * 5   # Less vertical knockback
        return knockback_x, knockback_y

    def update(self, *args):
        self.handle_keys()
        self.apply_gravity()
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.flash_counter > 0:
            self.flash_counter -= 1
            self.image.fill(ATTACK_FLASH_COLOR)
        else:
            self.image = self.original_image.copy()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color, level):
        super().__init__()
        self.original_image = pygame.Surface((40, 60))
        self.original_image.fill(color)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.velocity_y = 0
        self.speed = 3 + level  # Enemy speed increases with level
        self.on_ground = False
        self.attack_cooldown = 0
        self.is_attacking = False
        self.flash_duration = 5
        self.flash_counter = 0
        self.damage = 0  # Damage percentage
        self.level = level

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

    def move_towards_player(self, player):
        if self.rect.x < player.rect.x:
            self.rect.x += self.speed
        elif self.rect.x > player.rect.x:
            self.rect.x -= self.speed

    def attack(self):
        if self.attack_cooldown == 0:
            self.is_attacking = True
            self.flash_counter = self.flash_duration
            # Attack rate increases with level
            self.attack_cooldown = max(60 - self.level * 5, 15)

    def take_damage(self, amount):
        self.damage += amount
        # Calculate knockback based on damage
        knockback_x = 10 + (self.damage / 100) * 20  # More horizontal knockback
        knockback_y = -5 - (self.damage / 100) * 5   # Less vertical knockback
        return knockback_x, knockback_y

    def update(self, player):
        self.apply_gravity()
        self.move_towards_player(player)
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        # Attack if close to player
        if abs(self.rect.x - player.rect.x) < 50 and self.attack_cooldown == 0:
            self.attack()
        if self.flash_counter > 0:
            self.flash_counter -= 1
            self.image.fill(ATTACK_FLASH_COLOR)
        else:
            self.image = self.original_image.copy()

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height=20, solid=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(PLATFORM_COLOR)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.solid = solid  # Determines if the platform is solid (cannot pass through)

def check_collisions(player, enemy):
    global game_state, level

    # Player collision with platforms
    hits = pygame.sprite.spritecollide(player, platforms, False)
    player.on_ground = False
    for platform in hits:
        if player.is_falling_through and not platform.solid:
            continue
        if player.velocity_y > 0 and player.rect.bottom <= platform.rect.bottom:
            player.rect.bottom = platform.rect.top
            player.velocity_y = 0
            player.on_ground = True

    # Enemy collision with platforms
    enemy_hits = pygame.sprite.spritecollide(enemy, platforms, False)
    enemy.on_ground = False
    for platform in enemy_hits:
        if enemy.velocity_y > 0 and enemy.rect.bottom <= platform.rect.bottom:
            enemy.rect.bottom = platform.rect.top
            enemy.velocity_y = 0
            enemy.on_ground = True

    # Player attack collision with enemy
    if player.is_attacking and player.rect.colliderect(enemy.rect):
        knockback_x, knockback_y = enemy.take_damage(10)  # Increase damage by 10%
        enemy.velocity_y = knockback_y
        if player.rect.centerx < enemy.rect.centerx:
            enemy.rect.x += knockback_x
        else:
            enemy.rect.x -= knockback_x
        player.is_attacking = False  # Reset attack after hit

    # Enemy attack collision with player
    if enemy.is_attacking and enemy.rect.colliderect(player.rect):
        knockback_x, knockback_y = player.take_damage(10)  # Increase damage by 10%
        player.velocity_y = knockback_y
        if enemy.rect.centerx < player.rect.centerx:
            player.rect.x += knockback_x
        else:
            player.rect.x -= knockback_x
        enemy.is_attacking = False  # Reset attack after hit

    # Check if enemy goes beyond death borders
    if (enemy.rect.right < LEFT_BORDER or
        enemy.rect.left > RIGHT_BORDER or
        enemy.rect.bottom < TOP_BORDER or
        enemy.rect.top > BOTTOM_BORDER):
        level += 1
        start_new_level()

    # Check if player goes beyond death borders
    if (player.rect.right < LEFT_BORDER or
        player.rect.left > RIGHT_BORDER or
        player.rect.bottom < TOP_BORDER or
        player.rect.top > BOTTOM_BORDER):
        game_state = GAME_OVER

def start_new_level():
    global enemy, level, player
    # Remove old enemy
    enemy.kill()
    # Create a new enemy with increased difficulty
    enemy = Enemy(3 * SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2 - 100, ENEMY_COLOR, level)
    all_sprites.add(enemy)
    enemies.add(enemy)
    # Reset player position
    player.rect.midbottom = (SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2 - 100)
    player.velocity_y = 0
    # Reset player's damage
    player.damage = 0

def show_menu():
    screen.fill(BACKGROUND_COLOR)
    title_text = font.render("2D Platform Fighter", True, TEXT_COLOR)
    start_text = font.render("Press Enter to Start", True, TEXT_COLOR)
    screen.blit(title_text, (SCREEN_WIDTH / 2 - title_text.get_width() / 2, SCREEN_HEIGHT / 3))
    screen.blit(start_text, (SCREEN_WIDTH / 2 - start_text.get_width() / 2, SCREEN_HEIGHT / 2))
    pygame.display.flip()

def show_game_over():
    screen.fill(BACKGROUND_COLOR)
    game_over_text = font.render("Game Over", True, TEXT_COLOR)
    retry_text = font.render("Press Enter to Retry", True, TEXT_COLOR)
    level_text = font.render(f"You reached level {level}", True, TEXT_COLOR)
    screen.blit(game_over_text, (SCREEN_WIDTH / 2 - game_over_text.get_width() / 2, SCREEN_HEIGHT / 3))
    screen.blit(level_text, (SCREEN_WIDTH / 2 - level_text.get_width() / 2, SCREEN_HEIGHT / 2))
    screen.blit(retry_text, (SCREEN_WIDTH / 2 - retry_text.get_width() / 2, SCREEN_HEIGHT / 1.5))
    pygame.display.flip()

def reset_game():
    global player, enemy, level, all_sprites, platforms, enemies
    level = 1
    all_sprites.empty()
    platforms.empty()
    enemies.empty()
    # Create player and enemy
    player = Player(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2 - 100, PLAYER_COLOR)
    enemy = Enemy(3 * SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2 - 100, ENEMY_COLOR, level)
    all_sprites.add(player, enemy)
    enemies.add(enemy)
    # Create platforms
    # Bottom platform (ground)
    ground = Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, solid=True)
    platforms.add(ground)
    all_sprites.add(ground)
    # Smaller platforms
    platform1 = Platform(SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2, 300, 20)
    platform2 = Platform(SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 - 100, 100, 15)
    platform3 = Platform(SCREEN_WIDTH / 2 + 150, SCREEN_HEIGHT / 2 - 100, 100, 15)
    platform4 = Platform(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2 - 200, 100, 15)
    platforms.add(platform1, platform2, platform3, platform4)
    all_sprites.add(platform1, platform2, platform3, platform4)

# Initialize game variables
game_state = MENU
level = 1

# Create sprite groups
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()

# Initialize player and enemy
player = Player(SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2 - 100, PLAYER_COLOR)
enemy = Enemy(3 * SCREEN_WIDTH / 4, SCREEN_HEIGHT / 2 - 100, ENEMY_COLOR, level)
all_sprites.add(player, enemy)
enemies.add(enemy)

# Create platforms
# Bottom platform (ground)
ground = Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50, solid=True)
platforms.add(ground)
all_sprites.add(ground)
# Smaller platforms
platform1 = Platform(SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2, 300, 20)
platform2 = Platform(SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 - 100, 100, 15)
platform3 = Platform(SCREEN_WIDTH / 2 + 150, SCREEN_HEIGHT / 2 - 100, 100, 15)
platform4 = Platform(SCREEN_WIDTH / 2 - 50, SCREEN_HEIGHT / 2 - 200, 100, 15)
platforms.add(platform1, platform2, platform3, platform4)
all_sprites.add(platform1, platform2, platform3, platform4)

# Game loop
running = True
while running:
    clock.tick(FPS)
    if game_state == MENU:
        show_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = PLAYING
                    reset_game()
    elif game_state == PLAYING:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update all sprites with player as argument
        all_sprites.update(player)

        # Check collisions and game conditions
        check_collisions(player, enemy)

        # Draw
        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)

        # Draw level counter
        level_text = font.render(f"Level: {level}", True, TEXT_COLOR)
        screen.blit(level_text, (10, 10))

        # Draw player and enemy damage percentages
        player_damage_text = font.render(f"Player Damage: {player.damage}%", True, TEXT_COLOR)
        enemy_damage_text = font.render(f"Enemy Damage: {enemy.damage}%", True, TEXT_COLOR)
        screen.blit(player_damage_text, (10, 60))
        screen.blit(enemy_damage_text, (10, 110))

        pygame.display.flip()
    elif game_state == GAME_OVER:
        show_game_over()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    game_state = MENU

pygame.quit()
sys.exit()
