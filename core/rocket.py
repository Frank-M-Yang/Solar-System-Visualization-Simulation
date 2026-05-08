"""
rocket.py
Represents a rocket launched from Earth toward the Moon.
Used by the Qian Xuesen easter egg.
Inherits physics from CelestialBody; draws a small triangle instead of a circle.
"""

import pygame
import math
from core.celestial_body import CelestialBody


class Rocket(CelestialBody):
    """
    A rocket with negligible mass, launched from a planet.
    Affected by gravity from all other bodies just like any celestial body.

    Extra attributes:
        launched_from (Planet): The planet it was launched from
        active        (bool)  : False once it flies off screen
        success       (bool)  : True if it returns close to Earth
    """

    SUCCESS_RADIUS = 30   # pixels — how close counts as "returned to Earth"

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
        super().__init__(name, description, mass, radius, color, x, y, vx, vy)
        self.launched_from = launched_from
        self.active        = True
        self.success       = False

    def check_return(self, earth) -> bool:
        """
        Check if the rocket has returned close to Earth after orbiting the Moon.

        Args:
            earth (Planet): Earth object to measure distance against
        Returns:
            bool: True if within SUCCESS_RADIUS
        """
        dx   = self.position[0] - earth.position[0]
        dy   = self.position[1] - earth.position[1]
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < self.SUCCESS_RADIUS

    def is_off_screen(self, screen_width: int, screen_height: int) -> bool:
        """Returns True if the rocket has flown beyond the visible area."""
        margin = 100
        return (
            self.position[0] < -margin
            or self.position[0] > screen_width  + margin
            or self.position[1] < -margin
            or self.position[1] > screen_height + margin
        )

    def draw(self, screen: pygame.Surface):
        """
        Draw the rocket as a small triangle pointing in its direction of travel,
        with a coloured trail behind it.
        """
        # trail
        for i, (tx, ty) in enumerate(self.trail):
            brightness  = i / max(len(self.trail), 1)
            trail_color = tuple(int(c * brightness * 0.7) for c in self.color)
            if 0 <= int(tx) < screen.get_width() and 0 <= int(ty) < screen.get_height():
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 1)

        # triangle pointing along velocity vector
        vx, vy = self.velocity
        speed  = math.sqrt(vx * vx + vy * vy)

        if speed > 0:
            ux, uy = vx / speed, vy / speed   # unit forward vector
            px, py = -uy, ux                  # perpendicular vector

            tip   = (self.position[0] + ux * 7,  self.position[1] + uy * 7)
            left  = (self.position[0] - ux * 4 + px * 3,
                     self.position[1] - uy * 4 + py * 3)
            right = (self.position[0] - ux * 4 - px * 3,
                     self.position[1] - uy * 4 - py * 3)

            pygame.draw.polygon(
                screen, self.color,
                [(int(tip[0]),   int(tip[1])),
                 (int(left[0]),  int(left[1])),
                 (int(right[0]), int(right[1]))],
            )
        else:
            pygame.draw.circle(screen, self.color,
                               (int(self.position[0]), int(self.position[1])), 3)

        # label
        font  = pygame.font.SysFont("Arial", 10)
        label = font.render(self.name, True, (255, 150, 150))
        screen.blit(label, (int(self.position[0]) + 6, int(self.position[1]) - 5))
