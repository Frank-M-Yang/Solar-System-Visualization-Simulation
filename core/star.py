"""
star.py

Defines the Star class used for the Sun.

In this project stars are fixed gravitational anchors. They are included in
force calculations, but their own position is not advanced by the engine.
"""

import pygame

from core.celestial_body import CelestialBody


class Star(CelestialBody):
    """
    Stationary luminous body at the center of the simulation.

    Attributes:
        luminosity: Relative brightness factor used to describe the star.
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
        """
        Create a fixed star with zero initial velocity.

        Args:
            name: Display label.
            description: Short English description.
            mass: Relative mass used by gravity calculations.
            radius: Drawn radius in pixels.
            color: RGB draw color.
            luminosity: Relative brightness value.
            x: Initial x coordinate.
            y: Initial y coordinate.
        """
        super().__init__(name, description, mass, radius, color, x, y, vx=0.0, vy=0.0)
        self.luminosity = luminosity

    def update(self, dt: float, ax: float = 0.0, ay: float = 0.0):
        """
        Keep the star fixed in place.

        The physics engine calls update-compatible methods on bodies, but stars
        are treated as immovable anchors in this simplified simulator.
        """
        return None

    def draw(self, screen: pygame.Surface):
        """
        Draw the star with a soft two-layer glow and a label.

        Args:
            screen: Active pygame surface.
        """
        cx, cy = int(self.position[0]), int(self.position[1])

        glow_radius = int(self.radius * 1.8)
        glow_color = tuple(min(int(c * 0.35), 255) for c in self.color)
        pygame.draw.circle(screen, glow_color, (cx, cy), glow_radius)

        inner_radius = int(self.radius * 1.3)
        inner_color = tuple(min(int(c * 0.6), 255) for c in self.color)
        pygame.draw.circle(screen, inner_color, (cx, cy), inner_radius)

        pygame.draw.circle(screen, self.color, (cx, cy), int(self.radius))

        font = pygame.font.SysFont("Arial", 13, bold=True)
        label = font.render(self.name, True, (255, 255, 180))
        screen.blit(label, (cx + int(self.radius) + 4, cy - 7))
