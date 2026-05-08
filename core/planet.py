"""
planet.py
Represents a planet orbiting the star.
Inherits physical movement from CelestialBody; adds orbital data and a moon list.
"""

import pygame
from core.celestial_body import CelestialBody


class Planet(CelestialBody):
    """
    A planet that orbits a star under gravitational force.

    Inherits from CelestialBody:
        mass, radius, color, velocity, position, trail, update(), draw()

    Extra attributes:
        orbital_radius (float): Distance from the star in pixels (used for setup)
        orbital_speed  (float): Initial tangential speed in pixels/second
        moons          (list):  List of Moon objects orbiting this planet
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
        # Initial velocity is tangential (upward = negative y) for a clockwise orbit
        super().__init__(
            name, description, mass, radius, color,
            x, y,
            vx=0.0, vy=-orbital_speed,   # tangential velocity at start
        )
        self.orbital_radius = orbital_radius
        self.orbital_speed  = orbital_speed
        self.moons          = []           # populated later by SolarSystem

    def add_moon(self, moon):
        """
        Register a Moon as orbiting this planet.

        Args:
            moon (Moon): The moon object to attach
        """
        self.moons.append(moon)

    def update(self, dt: float, ax: float = 0.0, ay: float = 0.0):
        """
        Update the planet's position via PhysicsEngine (handled externally),
        then update all attached moons using hierarchical orbits.

        Note: PhysicsEngine calls this indirectly by modifying velocity/position
        directly. We override here only to cascade the update to moons.
        """
        # moons update their angle relative to this planet's current position
        for moon in self.moons:
            moon.update(dt)

    def draw(self, screen: pygame.Surface):
        """
        Draw the planet, its trail, its label, and all its moons.

        Args:
            screen (pygame.Surface): The active display surface
        """
        # draw planet + trail via parent
        super().draw(screen)

        # draw each moon
        for moon in self.moons:
            moon.draw(screen)
