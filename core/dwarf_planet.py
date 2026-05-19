"""
dwarf_planet.py

Defines dwarf planets, currently used for Pluto.
"""

import pygame

from core.planet import Planet


class DwarfPlanet(Planet):
    """
    Planet-like body with an additional classification label.

    DwarfPlanet inherits orbital setup and moon support from Planet. Its draw
    method is specialized so the trail is dotted and the label includes the
    classification string.

    Attributes:
        classification: Text label such as "Dwarf Planet".
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
        """
        Create a dwarf planet with normal planet orbital properties.

        Args:
            name: Display label.
            description: Short English description.
            mass: Relative simulation mass.
            radius: Drawn radius in pixels.
            color: RGB draw color.
            orbital_radius: Initial distance from the Sun.
            orbital_speed: Initial tangential speed.
            classification: Label appended to the rendered name.
            x: Initial x coordinate.
            y: Initial y coordinate.
        """
        super().__init__(
            name,
            description,
            mass,
            radius,
            color,
            orbital_radius,
            orbital_speed,
            x,
            y,
        )
        self.classification = classification

    def draw(self, screen: pygame.Surface):
        """
        Draw a dotted trail, body disk, and classification label.

        Args:
            screen: Active pygame surface.
        """
        for i, (tx, ty) in enumerate(self.trail):
            if i % 2 != 0:
                continue
            brightness = i / max(len(self.trail), 1)
            trail_color = tuple(int(c * brightness * 0.4) for c in self.color)
            if 0 <= int(tx) < screen.get_width() and 0 <= int(ty) < screen.get_height():
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 1)

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position[0]), int(self.position[1])),
            max(int(self.radius), 2),
        )

        font = pygame.font.SysFont("Arial", 10)
        label = font.render(f"{self.name} ({self.classification})", True, (180, 160, 160))
        screen.blit(
            label,
            (
                int(self.position[0]) + int(self.radius) + 3,
                int(self.position[1]) - 6,
            ),
        )
