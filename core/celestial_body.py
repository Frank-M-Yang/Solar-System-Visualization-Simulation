"""
celestial_body.py
Abstract-style base class for all celestial bodies (Star, Planet, Moon).
Inherits position from GameObject; adds mass, radius, velocity, color, and trail.
"""

import pygame
from core.game_object import GameObject


class CelestialBody(GameObject):
    """
    Represents any physical body in the solar system.

    Extends GameObject with:
        mass     (float): Mass in kg — drives gravitational calculations
        radius   (float): Visual radius in pixels
        velocity (list):  [vx, vy] velocity vector, pixels per second
        color    (tuple): RGB color used for rendering
        trail    (list):  Recent past positions, used to draw orbit trail
    """

    TRAIL_LENGTH = 150  # number of past positions kept for the orbit trail

    def __init__(
        self,
        name: str,
        description: str,
        mass: float,
        radius: float,
        color: tuple,
        x: float = 0.0,
        y: float = 0.0,
        vx: float = 0.0,
        vy: float = 0.0,
    ):
        super().__init__(name, description, x, y)
        self.mass     = mass
        self.radius   = radius
        self.color    = color
        self.velocity = [vx, vy]
        self.trail    = []          # list of (x, y) snapshots

    # ------------------------------------------------------------------
    # Physics
    # ------------------------------------------------------------------

    def update(self, dt: float, ax: float = 0.0, ay: float = 0.0):
        """
        Advance the body by one time step using Euler integration.

        Args:
            dt (float): Time step in seconds
            ax (float): Net gravitational acceleration in x  (pixels/s²)
            ay (float): Net gravitational acceleration in y  (pixels/s²)
        """
        # 1. update velocity from acceleration
        self.velocity[0] += ax * dt
        self.velocity[1] += ay * dt

        # 2. record current position for trail before moving
        self.trail.append((self.position[0], self.position[1]))
        if len(self.trail) > self.TRAIL_LENGTH:
            self.trail.pop(0)

        # 3. update position from velocity
        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface):
        """
        Draw the orbit trail and the body itself onto the pygame surface.

        Args:
            screen (pygame.Surface): The active display surface
        """
        # --- draw trail (older points are dimmer) ---
        for i, (tx, ty) in enumerate(self.trail):
            brightness = i / self.TRAIL_LENGTH          # 0.0 → 1.0
            trail_color = tuple(int(c * brightness * 0.5) for c in self.color)
            if 0 <= int(tx) < screen.get_width() and 0 <= int(ty) < screen.get_height():
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 1)

        # --- draw main body ---
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position[0]), int(self.position[1])),
            max(int(self.radius), 2),
        )

        # --- draw name label ---
        font  = pygame.font.SysFont("Arial", 11)
        label = font.render(self.name, True, (200, 200, 200))
        screen.blit(
            label,
            (int(self.position[0]) + int(self.radius) + 3,
             int(self.position[1]) - 6),
        )
