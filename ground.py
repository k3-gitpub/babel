import pygame
import config

class Ground:
    """Manages the ground, including the animation on collision."""
    def __init__(self):
        """Initializes the ground."""
        # Store the original position and size of the ground
        self.original_rect = pygame.Rect(0, config.GROUND_Y, config.SCREEN_WIDTH, config.SCREEN_HEIGHT - config.GROUND_Y)
        self.rect = self.original_rect.copy()
        self.color = config.GREEN

        # Animation-related attributes
        self.is_animating = False
        self.animation_start_time = 0
        self.current_scale_y = 1.0 # Only scale in the Y direction

    def start_animation(self):
        """Starts the collision animation."""
        if not self.is_animating:
            self.is_animating = True
            self.animation_start_time = pygame.time.get_ticks()

    def update(self):
        """Updates the ground's animation state."""
        if not self.is_animating:
            return

        elapsed_time = pygame.time.get_ticks() - self.animation_start_time

        if elapsed_time >= config.GROUND_ANIMATION_DURATION:
            self.is_animating = False
            self.current_scale_y = 1.0
            self.rect = self.original_rect.copy()
        else:
            # Use an ease-out function for a smoother, more natural animation
            progress = elapsed_time / config.GROUND_ANIMATION_DURATION
            eased_progress = 1 - (1 - progress) ** 2 # Ease-out quad
            min_scale = config.GROUND_ANIMATION_MIN_SCALE
            self.current_scale_y = min_scale + (1.0 - min_scale) * eased_progress
            self.rect.height = self.original_rect.height * self.current_scale_y
            self.rect.bottom = self.original_rect.bottom # Keep the bottom of the ground fixed to the screen bottom

    def draw(self, screen):
        """Draws the ground."""
        pygame.draw.rect(screen, self.color, self.rect)