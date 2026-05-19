"""
planet.py

Defines planets that move under the global gravity engine and own local moons.
"""

import pygame

from core.celestial_body import CelestialBody


class Planet(CelestialBody):
    """
    Planet orbiting the Sun under Newtonian gravity.

    The planet's translational motion is updated by PhysicsEngine. The planet
    class adds initial orbital metadata and a list of moons. Moons are updated
    in a local frame after the planet has moved.

    Attributes:
        orbital_radius: Initial distance from the Sun in pixels.
        orbital_speed: Initial tangential speed in pixels per second.
        moons: Moon objects attached to this planet.
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
        x: float = 0.0,
        y: float = 0.0,
    ):
        """
        Create a planet with tangential starting velocity.

        Args:
            name: Display label.
            description: Short English description.
            mass: Relative simulation mass.
            radius: Drawn radius in pixels.
            color: RGB draw color.
            orbital_radius: Initial distance from the Sun.
            orbital_speed: Initial tangential speed.
            x: Initial x coordinate.
            y: Initial y coordinate.
        """
        super().__init__(
            name,
            description,
            mass,
            radius,
            color,
            x,
            y,
            vx=0.0,
            vy=-orbital_speed,
        )
        self.orbital_radius = orbital_radius
        self.orbital_speed = orbital_speed
        self.moons = []

    def add_moon(self, moon):
        """
        Attach a moon to this planet.

        Args:
            moon: Moon instance that should follow this planet.
        """
        self.moons.append(moon)

    def update(self, dt: float, ax: float = 0.0, ay: float = 0.0):
        """
        Update moons after the physics engine moves the planet.

        Args:
            dt: Time step in simulation seconds.
            ax: Ignored here because planet acceleration is handled externally.
            ay: Ignored here because planet acceleration is handled externally.
        """
        for moon in self.moons:
            moon.update(dt)

    def draw(self, screen: pygame.Surface):
        """
        Draw the planet and then draw all attached moons.

        Args:
            screen: Active pygame surface.
        """
        super().draw(screen)
        for moon in self.moons:
            moon.draw(screen)
