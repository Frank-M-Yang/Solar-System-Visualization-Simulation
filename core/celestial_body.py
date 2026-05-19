"""
celestial_body.py

Defines the common physical and visual behavior for stars, planets, moons,
dwarf planets, and rockets.

CelestialBody extends GameObject with mass, radius, velocity, color, and an
orbit trail. Subclasses can override update or draw when they need specialized
behavior, but the base implementation covers the common case.
"""

import pygame

from core.game_object import GameObject


class CelestialBody(GameObject):
    """
    Physical object that can move and be drawn on a pygame surface.

    The class uses symplectic Euler style updates: velocity changes first from
    acceleration, then position changes from the new velocity. This is simple
    and stable enough for the scaled educational simulation.

    Attributes:
        mass: Relative mass used by the gravity engine.
        radius: Visual radius in pixels.
        color: RGB tuple used for drawing the object and trail.
        velocity: Two-item list containing x and y velocity.
        trail: Recent position snapshots used to render orbit history.
    """

    TRAIL_LENGTH = 150

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
        """
        Create a body with physical properties and initial motion.

        Args:
            name: Display label for the object.
            description: Short English description.
            mass: Relative simulation mass.
            radius: Drawn radius in pixels.
            color: RGB draw color.
            x: Initial x coordinate.
            y: Initial y coordinate.
            vx: Initial x velocity.
            vy: Initial y velocity.
        """
        super().__init__(name, description, x, y)
        self.mass = mass
        self.radius = radius
        self.color = color
        self.velocity = [vx, vy]
        self.trail = []

    def update(self, dt: float, ax: float = 0.0, ay: float = 0.0):
        """
        Advance this body by one time step.

        Args:
            dt: Time step in simulation seconds.
            ax: Net x acceleration applied during this step.
            ay: Net y acceleration applied during this step.

        The current position is recorded before motion so trails show where the
        body has been. Old trail points are trimmed to a fixed length to avoid
        unbounded memory growth.
        """
        self.velocity[0] += ax * dt
        self.velocity[1] += ay * dt

        self.trail.append((self.position[0], self.position[1]))
        if len(self.trail) > self.TRAIL_LENGTH:
            self.trail.pop(0)

        self.position[0] += self.velocity[0] * dt
        self.position[1] += self.velocity[1] * dt

    def draw(self, screen: pygame.Surface):
        """
        Draw the orbit trail, body disk, and name label.

        Args:
            screen: Active pygame surface.

        Trail points fade from dim to brighter as they approach the current
        position. The body itself is drawn as a filled circle with a small label
        placed to the right.
        """
        for i, (tx, ty) in enumerate(self.trail):
            brightness = i / self.TRAIL_LENGTH
            trail_color = tuple(int(c * brightness * 0.5) for c in self.color)
            if 0 <= int(tx) < screen.get_width() and 0 <= int(ty) < screen.get_height():
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 1)

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position[0]), int(self.position[1])),
            max(int(self.radius), 2),
        )

        font = pygame.font.SysFont("Arial", 11)
        label = font.render(self.name, True, (200, 200, 200))
        screen.blit(
            label,
            (
                int(self.position[0]) + int(self.radius) + 3,
                int(self.position[1]) - 6,
            ),
        )
