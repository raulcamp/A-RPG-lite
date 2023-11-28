"""Lite 2D version of ER"""
import sys
from dataclasses import dataclass, field
import random
import pygame


# pylint: disable=no-member
pygame.init()

# Dimensions
WIDTH, HEIGHT = 1000, 500
GROUND_HEIGHT = (4/5)*HEIGHT

PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50

PROJECTILE_WIDTH = 10
PROJECTILE_HEIGHT = 10

SWORD_WIDTH = 1.5*PLAYER_WIDTH
SWORD_HEIGHT = PLAYER_HEIGHT // 5

ENEMY_WIDTH = 100
ENEMY_HEIGHT = 100


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
RED = (240, 0, 0)
BLUE = (0, 0, 240)
CYAN = (0, 240, 240)
GREEN = (0, 240, 0)
YELLOW = (240, 240, 0)
ORANGE = (240, 160, 0)
PURPLE = (160, 0, 240)


@dataclass
class Object:
    """Represents object"""
    x: int
    y: int
    width: int
    height: int
    color: tuple


@dataclass
class Projectile(Object):
    """Represents projectile"""
    x_v: int
    y_v: int

    def get_next(self) -> tuple:
        """Gets projectile's next position"""
        return (self.x + self.x_v, self.y + self.y_v)

    def set_next(self, x, y) -> None:
        """Sets projectile's next position"""
        self.x = x
        self.y = y

    def update_position(self) -> None:
        """Updates projectile's position"""
        self.set_next(*self.get_next())


@dataclass
class Sword(Object):
    """Represents sword"""


@dataclass
class Health(Object):
    """Represents healthbar"""
    orig_width: int
    current_hp: int
    max_hp: int

    def damage(self, amount):
        """Damages the healthbar"""
        self.current_hp -= amount
        self.current_hp = max(self.current_hp, 0)
        self.width = self.orig_width * (self.current_hp / self.max_hp)


@dataclass
class Player(Object):
    """Represents player"""
    name: str
    health: Health = Health(20, 20, 0.6*WIDTH, 15, RED,  0.6*WIDTH, 100, 100)
    crouch_height: int = PLAYER_HEIGHT // 2
    projectiles: list = field(default_factory=list)
    sword: Sword = None

    def add_projectile(self, x_direction):
        """Adds a projectile to the player"""
        x = self.x + self.width // 2 - PROJECTILE_WIDTH // 2
        y = self.y + self.height // 2 - PROJECTILE_HEIGHT // 2
        x_v = -10 if not x_direction else 10
        proj = Projectile(
            x, y, PROJECTILE_WIDTH, PROJECTILE_HEIGHT, GREEN, x_v, 0)
        self.projectiles.append(proj)

    def remove_projectile(self, projectile):
        """Removes a projectile from the player"""
        self.projectiles.remove(projectile)

    def swing_sword(self, x_direction):
        """Swings the sword"""
        if x_direction:
            x = self.x + self.width
        else:
            x = self.x - SWORD_WIDTH
        y = self.y + self.height // 2 - SWORD_HEIGHT // 2
        self.sword = Sword(x, y, SWORD_WIDTH, SWORD_HEIGHT, CYAN)

    def crouch(self):
        """Crouchs the player"""
        self.y += self.crouch_height
        self.height -= self.crouch_height

    def uncrouch(self):
        """Uncrouchs the player"""
        self.y -= self.crouch_height
        self.height += self.crouch_height

    def hit(self, damage_taken):
        """Hits the player"""
        self.health.damage(damage_taken)


@dataclass
class Enemy(Object):
    """Represents enemy"""
    name: str
    projectiles: list = field(default_factory=list)
    sword: Sword = None

    def add_projectile(self, x_direction):
        """Adds a projectile from the enemy"""
        x = self.x + self.width // 2 - PROJECTILE_WIDTH // 2
        y = self.y + self.height // 2 - PROJECTILE_HEIGHT // 2
        x_v = -10 if not x_direction else 10
        proj = Projectile(
            x, y, PROJECTILE_WIDTH, PROJECTILE_HEIGHT, GREEN, x_v, 0)
        self.projectiles.append(proj)

    def remove_projectile(self, projectile):
        """Removes a projectile from the enemy"""
        self.projectiles.remove(projectile)

    def swing_sword(self, x_direction):
        """Swings the sword"""
        if x_direction:
            x = self.x + self.width
        else:
            x = self.x - SWORD_WIDTH
        y = self.y + self.height // 2 - SWORD_HEIGHT // 2
        self.sword = Sword(x, y, SWORD_WIDTH, SWORD_HEIGHT, CYAN)

    def attack(self, player):
        """Attacks the player"""
        if abs(player.x - self.x) > 0.5*WIDTH:
            if random.randrange(100) == 0:
                print("Firing projectile")
                self.add_projectile(False)
        else:
            if random.randrange(100) == 0:
                print("Swinging sword")


class Game:
    """Represents game"""
    def __init__(self):
        self.player = Player((WIDTH - PLAYER_WIDTH) // 4,
                             GROUND_HEIGHT - PLAYER_HEIGHT,
                             PLAYER_WIDTH,
                             PLAYER_HEIGHT,
                             WHITE,
                             "Player 1")
        self.enemy = Enemy((WIDTH - 2 * ENEMY_WIDTH),
                           GROUND_HEIGHT - ENEMY_HEIGHT,
                           ENEMY_WIDTH,
                           ENEMY_HEIGHT,
                           RED,
                           "Enemy 1")

    def valid_move(self, obj, x, y):
        """Check if the object can move to the given position"""
        if obj.x + x < 0 or obj.x + x > WIDTH - obj.width:
            return False
        if obj.y + y < 0 or obj.y + y > GROUND_HEIGHT - obj.height:
            return False
        return True

    def is_out_of_bounds(self, obj):
        """Checks if the object is out of bounds"""
        if obj.x < 0 or obj.x > WIDTH - obj.width:
            return True
        if obj.y < 0 or obj.y > GROUND_HEIGHT - obj.height:
            return True
        return False

    def collision(self, obj1, obj2):
        """Checks if two objects collide"""
        if obj1.x < obj2.x + obj2.width \
                and obj1.x + obj1.width > obj2.x:
            if obj1.y < obj2.y + obj2.height \
                    and obj1.y + obj1.height > obj2.y:
                return True
        return False

    def draw_rect(self, screen, obj, width=0):
        """Draws a rectangle"""
        pygame.draw.rect(screen, obj.color,
                         (obj.x, obj.y, obj.width, obj.height), width)

    def draw(self, screen):
        """Draw the grid and the current objects"""
        for projectile in [*self.player.projectiles, *self.enemy.projectiles]:
            self.draw_rect(screen, projectile)

        if self.enemy.sword:
            self.draw_rect(screen, self.enemy.sword)
        if self.player.sword:
            self.draw_rect(screen, self.player.sword)

        self.draw_rect(screen, self.enemy)
        self.draw_rect(screen, self.player)
        self.draw_rect(screen, self.player.health, 1)


def main():
    """Runs the game"""
    # Initialize pygame
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Game')
    # Create a clock object
    clock = pygame.time.Clock()
    # Create a Game object
    game = Game()

    jumping = False
    y_gravity = 0.5
    jump_height = 10
    y_velocity = jump_height

    x_direction = True

    swinging = False
    swing_time = 0
    swing_duration = 200

    crouching = False
    while True:
        # Fill the background
        pygame.draw.rect(screen, BLACK, (0, 0, WIDTH, GROUND_HEIGHT))
        pygame.draw.rect(screen, GRAY, (0, GROUND_HEIGHT, WIDTH, HEIGHT))

        speed = 5
        if crouching:
            speed = 3

        for event in pygame.event.get():
            # Check for the QUIT event
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if swinging:
                break
            # Check for the KEYDOWN event
            if event.type == pygame.KEYDOWN:
                # Check for creating projectiles
                if event.key == pygame.K_SPACE:
                    # game.player.add_projectile(x_direction)
                    pass
                if event.key == pygame.K_s and not crouching and not jumping:
                    game.player.crouch()
                    crouching = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_s and crouching:
                    game.player.uncrouch()
                    crouching = False

            # Check for the MOUSEBUTTONDOWN event
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not jumping and not swinging and not crouching:
                        game.player.swing_sword(x_direction)
                        swinging = True
                elif event.button == 3:
                    pass

        # Move projectiles
        for projectile in game.player.projectiles:
            if game.is_out_of_bounds(projectile):
                game.player.remove_projectile(projectile)
            else:
                projectile.update_position()

        # Check for key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if game.valid_move(game.player, -speed, 0) and not swinging:
                game.player.x -= speed
                x_direction = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if game.valid_move(game.player, speed, 0) and not swinging:
                game.player.x += speed
                x_direction = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            pass
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            if not swinging and not crouching:
                jumping = True

        if jumping:
            game.player.y -= y_velocity
            y_velocity -= y_gravity
            if y_velocity < -jump_height:
                jumping = False
                y_velocity = jump_height

        if swinging:
            # Get the number of milliseconds since the last frame
            delta_time = clock.tick(60)
            # Add the delta time to the swing time
            swing_time += delta_time
            if swing_time >= swing_duration:
                # Stop swinging
                swinging = False
                game.player.sword = None
                # Reset the swing time
                swing_time = 0

        game.enemy.attack(game.player)
        for projectile in game.enemy.projectiles:
            if game.collision(game.player, projectile):
                game.player.hit(5)
                game.enemy.remove_projectile(projectile)
            elif game.is_out_of_bounds(projectile):
                game.enemy.remove_projectile(projectile)
            else:
                projectile.update_position()
        # Draw the grid and the current piece
        game.draw(screen)
        # Update the display
        pygame.display.flip()
        # Set the framerate
        clock.tick(60)


if __name__ == "__main__":
    main()
