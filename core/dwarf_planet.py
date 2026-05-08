"""
dwarf_planet.py
Represents a dwarf planet (e.g. Pluto).
Inherits everything from Planet; adds a classification label
and a dotted trail to visually distinguish it from full planets.
"""

import pygame
from core.planet import Planet


class DwarfPlanet(Planet):
    """
    A dwarf planet orbiting the Sun.
    Inherits orbital physics from Planet.

    Extra attribute:
        classification (str): Always "Dwarf Planet", shown in the label
    """

    def __init__(
        self,
        name: str,
        description: str,
        mass: float,
        radius: float,
        color: tuple,
        orbital_radius: float,
        orbital_speed: float,
        classification: str = "Dwarf Planet",
        x: float = 0.0,
        y: float = 0.0,
    ):
        super().__init__(
            name, description, mass, radius, color,
            orbital_radius, orbital_speed, x, y,
        )
        self.classification = classification

    def draw(self, screen: pygame.Surface):
        """
        Draw with a dotted trail (every other point skipped)
        to distinguish from regular planets visually.
        """
        # dotted trail — skip every 2nd point
        for i, (tx, ty) in enumerate(self.trail):
            if i % 2 != 0:
                continue
            brightness  = i / max(len(self.trail), 1)
            trail_color = tuple(int(c * brightness * 0.4) for c in self.color)
            if 0 <= int(tx) < screen.get_width() and 0 <= int(ty) < screen.get_height():
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 1)

        # main body
        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position[0]), int(self.position[1])),
            max(int(self.radius), 2),
        )

        # label includes classification
        font  = pygame.font.SysFont("Arial", 10)
        label = font.render(f"{self.name} ({self.classification})", True, (180, 160, 160))
        screen.blit(
            label,
            (int(self.position[0]) + int(self.radius) + 3,
             int(self.position[1]) - 6),
        )
