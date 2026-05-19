"""
rocket.py

Defines a reusable rocket object.

The current Qian Xuesen easter egg uses a dedicated precomputed two-body
visualization, but this class remains available for future missions that need a
rocket inside the main N-body solar system.
"""

import math

import pygame

from core.celestial_body import CelestialBody


class Rocket(CelestialBody):
    """
    Small controllable or mission-driven craft.

    Attributes:
        launched_from: Object that provided the launch position.
        active: Whether the rocket should still be updated or drawn.
        success: Mission flag that can be set by scenario code.
    """

    SUCCESS_RADIUS = 30

    def __init__(
        self,
        name: str,
        description: str,
        mass: float,
        radius: float,
        color: tuple,
        x: float,
        y: float,
        vx: float,
        vy: float,
        launched_from,
    ):
        """
        Create a rocket with initial position and velocity.

        Args:
            name: Display label.
            description: Short English description.
            mass: Relative simulation mass.
            radius: Drawn radius in pixels.
            color: RGB draw color.
            x: Initial x coordinate.
            y: Initial y coordinate.
            vx: Initial x velocity.
            vy: Initial y velocity.
            launched_from: Source body or object for the launch.
        """
        super().__init__(name, description, mass, radius, color, x, y, vx, vy)
        self.launched_from = launched_from
        self.active = True
        self.success = False

    def check_return(self, earth) -> bool:
        """
        Check whether the rocket is close enough to Earth to count as returned.

        Args:
            earth: Body whose position is used as the return target.

        Returns:
            True when the rocket is inside SUCCESS_RADIUS of Earth.
        """
        dx = self.position[0] - earth.position[0]
        dy = self.position[1] - earth.position[1]
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < self.SUCCESS_RADIUS

    def is_off_screen(self, screen_width: int, screen_height: int) -> bool:
        """
        Check whether the rocket has left the visible simulation area.

        Args:
            screen_width: Width of the pygame window in pixels.
            screen_height: Height of the pygame window in pixels.

        Returns:
            True if the rocket is outside the window plus a margin.
        """
        margin = 100
        return (
            self.position[0] < -margin
            or self.position[0] > screen_width + margin
            or self.position[1] < -margin
            or self.position[1] > screen_height + margin
        )

    def draw(self, screen: pygame.Surface):
        """
        Draw the rocket as a direction-facing triangle with a fading trail.

        Args:
            screen: Active pygame surface.
        """
        for i, (tx, ty) in enumerate(self.trail):
            brightness = i / max(len(self.trail), 1)
            trail_color = tuple(int(c * brightness * 0.7) for c in self.color)
            if 0 <= int(tx) < screen.get_width() and 0 <= int(ty) < screen.get_height():
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 1)

        vx, vy = self.velocity
        speed = math.sqrt(vx * vx + vy * vy)

        if speed > 0:
            ux, uy = vx / speed, vy / speed
            px, py = -uy, ux

            tip = (self.position[0] + ux * 7, self.position[1] + uy * 7)
            left = (
                self.position[0] - ux * 4 + px * 3,
                self.position[1] - uy * 4 + py * 3,
            )
            right = (
                self.position[0] - ux * 4 - px * 3,
                self.position[1] - uy * 4 - py * 3,
            )

            pygame.draw.polygon(
                screen,
                self.color,
                [
                    (int(tip[0]), int(tip[1])),
                    (int(left[0]), int(left[1])),
                    (int(right[0]), int(right[1])),
                ],
            )
        else:
            pygame.draw.circle(
                screen,
                self.color,
                (int(self.position[0]), int(self.position[1])),
                3,
            )

        font = pygame.font.SysFont("Arial", 10)
        label = font.render(self.name, True, (255, 150, 150))
        screen.blit(label, (int(self.position[0]) + 6, int(self.position[1]) - 5))
