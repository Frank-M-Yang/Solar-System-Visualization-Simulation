"""
moon.py

Defines natural satellites that orbit a parent planet in a local frame.

Moons are intentionally not registered with the global N-body physics engine.
At the current pixel scale, direct Sun gravity would dominate and make moons
escape their planets. A local circular orbit gives a stable educational view.
"""

import math

import pygame

from core.celestial_body import CelestialBody


class Moon(CelestialBody):
    """
    Natural satellite updated by hierarchical local orbit logic.

    Attributes:
        parent: Planet object that acts as the local orbit center.
        orbital_radius: Distance from the parent in pixels.
        angular_velocity: Orbital angular speed in radians per second.
        angle: Current angle around the parent in radians.
    """

    def __init__(
        self,
        name: str,
        description: str,
        mass: float,
        radius: float,
        color: tuple,
        parent,
        orbital_radius: float,
        orbital_speed: float,
    ):
        """
        Create a moon to the right of its parent planet.

        Args:
            name: Display label.
            description: Short English description.
            mass: Relative simulation mass, kept for consistency.
            radius: Drawn radius in pixels.
            color: RGB draw color.
            parent: Planet object this moon orbits.
            orbital_radius: Distance from parent in pixels.
            orbital_speed: Tangential local speed in pixels per second.
        """
        x = parent.position[0] + orbital_radius
        y = parent.position[1]
        super().__init__(name, description, mass, radius, color, x, y, 0.0, 0.0)

        self.parent = parent
        self.orbital_radius = orbital_radius
        self.angular_velocity = orbital_speed / orbital_radius
        self.angle = 0.0

    def update(self, dt: float, ax: float = 0.0, ay: float = 0.0):
        """
        Advance the local orbital angle and recompute position.

        Args:
            dt: Time step in simulation seconds.
            ax: Ignored because this is a prescribed local orbit.
            ay: Ignored because this is a prescribed local orbit.
        """
        self.angle += self.angular_velocity * dt
        self.position[0] = self.parent.position[0] + math.cos(self.angle) * self.orbital_radius
        self.position[1] = self.parent.position[1] + math.sin(self.angle) * self.orbital_radius

        self.trail.append((self.position[0], self.position[1]))
        if len(self.trail) > self.TRAIL_LENGTH:
            self.trail.pop(0)

    def draw(self, screen: pygame.Surface):
        """
        Draw the moon, its shorter dim trail, and its label.

        Args:
            screen: Active pygame surface.
        """
        for i, (tx, ty) in enumerate(self.trail):
            brightness = i / max(len(self.trail), 1)
            trail_color = tuple(int(c * brightness * 0.3) for c in self.color)
            if 0 <= int(tx) < screen.get_width() and 0 <= int(ty) < screen.get_height():
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 1)

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position[0]), int(self.position[1])),
            max(int(self.radius), 1),
        )

        font = pygame.font.SysFont("Arial", 9)
        label = font.render(self.name, True, (140, 140, 140))
        screen.blit(
            label,
            (
                int(self.position[0]) + int(self.radius) + 2,
                int(self.position[1]) - 4,
            ),
        )
