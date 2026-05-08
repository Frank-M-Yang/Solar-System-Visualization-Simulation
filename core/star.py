"""
star.py
Represents the Sun (or any star) at the centre of the solar system.
A Star is a CelestialBody that never moves; it acts as the gravitational anchor.
"""

import pygame
from core.celestial_body import CelestialBody


class Star(CelestialBody):
    """
    A star fixed at the centre of the simulation.

    Inherits all physical attributes from CelestialBody.
    Extra attribute:
        luminosity (float): Brightness factor (0.0 – 1.0), used for the glow effect
    """

    def __init__(
        self,
        name: str,
        description: str,
        mass: float,
        radius: float,
        color: tuple,
        luminosity: float,
        x: float = 0.0,
        y: float = 0.0,
    ):
        # velocity is always zero — stars are fixed
        super().__init__(name, description, mass, radius, color, x, y, vx=0.0, vy=0.0)
        self.luminosity = luminosity

    # ------------------------------------------------------------------
    # Physics  — stars do not move
    # ------------------------------------------------------------------

    def update(self, dt: float, ax: float = 0.0, ay: float = 0.0):
        """Stars are stationary — override update to do nothing."""
        pass

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface):
        """
        Draw the star with a two-layer glow effect:
        - a large, dim outer halo
        - the bright main disc
        - a bold name label
        """
        cx, cy = int(self.position[0]), int(self.position[1])

        # outer glow  (larger radius, muted colour)
        glow_radius = int(self.radius * 1.8)
        glow_color  = tuple(min(int(c * 0.35), 255) for c in self.color)
        pygame.draw.circle(screen, glow_color, (cx, cy), glow_radius)

        # inner glow  (medium radius, slightly brighter)
        inner_radius = int(self.radius * 1.3)
        inner_color  = tuple(min(int(c * 0.6), 255) for c in self.color)
        pygame.draw.circle(screen, inner_color, (cx, cy), inner_radius)

        # main body
        pygame.draw.circle(screen, self.color, (cx, cy), int(self.radius))

        # name label
        font  = pygame.font.SysFont("Arial", 13, bold=True)
        label = font.render(self.name, True, (255, 255, 180))
        screen.blit(label, (cx + int(self.radius) + 4, cy - 7))
