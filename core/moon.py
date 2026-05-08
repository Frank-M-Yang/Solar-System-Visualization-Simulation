"""
moon.py
Represents a natural satellite orbiting a Planet.

Unlike planets, moons use a HIERARCHICAL orbit model:
they are NOT registered with the global PhysicsEngine.
Instead, each frame the Moon computes its position directly
from its parent's current position + a local orbital angle.

Why:
    In pixel-scale simulations the Sun's gravity completely
    dominates at all distances. Earth's Hill sphere (the region
    where it can gravitationally hold the Moon) is only ~1.5 px,
    so any Moon in the global n-body physics immediately escapes
    to orbit the Sun.  Hierarchical integration (used by real
    solar-system simulators like REBOUND) solves this by treating
    each moon as orbiting its parent in a local frame.
"""

import math
import pygame
from core.celestial_body import CelestialBody


class Moon(CelestialBody):
    """
    A natural satellite that orbits a Planet using local orbital mechanics.

    Inherits rendering attributes from CelestialBody (color, radius, trail).
    Does NOT participate in the global PhysicsEngine step.

    Attributes:
        parent          (Planet): The planet this moon orbits
        orbital_radius  (float):  Distance from parent in pixels
        angular_velocity(float):  Radians per second  (derived from orbital_speed)
        angle           (float):  Current orbital angle in radians
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
        orbital_speed: float,          # px/s tangential speed around parent
    ):
        # Start position: directly to the right of parent
        x = parent.position[0] + orbital_radius
        y = parent.position[1]

        # velocity doesn't matter for hierarchical orbit, but keep for interface
        super().__init__(name, description, mass, radius, color, x, y, 0.0, 0.0)

        self.parent           = parent
        self.orbital_radius   = orbital_radius
        # convert tangential speed to angular velocity: ω = v / r
        self.angular_velocity = orbital_speed / orbital_radius
        self.angle            = 0.0    # start at 3 o'clock relative to parent

    # ------------------------------------------------------------------
    # Physics  — local hierarchical update, NOT called by PhysicsEngine
    # ------------------------------------------------------------------

    def update(self, dt: float, ax: float = 0.0, ay: float = 0.0):
        """
        Advance orbital angle and recompute position from parent.
        Called by Planet.update(), not by PhysicsEngine.

        Args:
            dt (float): Time step in seconds
        """
        self.angle += self.angular_velocity * dt

        # position = parent position + local orbit vector
        self.position[0] = self.parent.position[0] + math.cos(self.angle) * self.orbital_radius
        self.position[1] = self.parent.position[1] + math.sin(self.angle) * self.orbital_radius

        # trail
        self.trail.append((self.position[0], self.position[1]))
        if len(self.trail) > self.TRAIL_LENGTH:
            self.trail.pop(0)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface):
        """Draw the moon with a dim short trail."""
        for i, (tx, ty) in enumerate(self.trail):
            brightness  = i / max(len(self.trail), 1)
            trail_color = tuple(int(c * brightness * 0.3) for c in self.color)
            if 0 <= int(tx) < screen.get_width() and 0 <= int(ty) < screen.get_height():
                pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), 1)

        pygame.draw.circle(
            screen,
            self.color,
            (int(self.position[0]), int(self.position[1])),
            max(int(self.radius), 1),
        )

        font  = pygame.font.SysFont("Arial", 9)
        label = font.render(self.name, True, (140, 140, 140))
        screen.blit(label, (int(self.position[0]) + int(self.radius) + 2,
                            int(self.position[1]) - 4))
