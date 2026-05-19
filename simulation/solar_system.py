"""
solar_system.py

Builds and owns the simulated solar system.

SolarSystem translates static data from config.py into live Star, Planet, Moon,
and DwarfPlanet objects. It also owns the PhysicsEngine used by the main
simulation loop.
"""

import config
from core.dwarf_planet import DwarfPlanet
from core.moon import Moon
from core.planet import Planet
from core.star import Star
from engine.physics_engine import PhysicsEngine


class SolarSystem:
    """
    Container for all celestial bodies and the physics engine.

    Attributes:
        engine: Shared PhysicsEngine instance.
        star: The Sun object.
        planets: List of eight Planet objects.
        pluto: DwarfPlanet object for Pluto.
        moons: Flat list of all Moon objects.
        earth: Convenience reference to Earth.
        moon: Convenience reference to Earth's Moon.
    """

    def __init__(self):
        """
        Create an empty world and immediately populate it from config data.
        """
        self.engine = PhysicsEngine(dt=config.DT)
        self.star = None
        self.planets = []
        self.pluto = None
        self.moons = []
        self.earth = None
        self.moon = None
        self._build()

    def _build(self):
        """
        Instantiate every configured body and register physics participants.

        The Sun, planets, and Pluto are registered with the global engine. Moons
        are attached to their parent planets but are not registered globally
        because they use local hierarchical orbit logic.
        """
        self.star = Star(
            **{key: value for key, value in config.SUN_DATA.items()},
            x=float(config.CX),
            y=float(config.CY),
        )
        self.engine.add_body(self.star)

        for planet_data in config.PLANET_DATA:
            orbital_speed = (
                self.engine.circular_orbit_speed(
                    self.star.mass,
                    planet_data["orbital_radius"],
                )
                * planet_data["speed_factor"]
            )

            planet = Planet(
                name=planet_data["name"],
                description=planet_data["description"],
                mass=planet_data["mass"],
                radius=planet_data["radius"],
                color=planet_data["color"],
                orbital_radius=planet_data["orbital_radius"],
                orbital_speed=orbital_speed,
                x=float(config.CX + planet_data["orbital_radius"]),
                y=float(config.CY),
            )
            self.planets.append(planet)
            self.engine.add_body(planet)

            if planet.name == "Earth":
                self.earth = planet

        for planet in filter(lambda item: item.name in config.MOON_DATA, self.planets):
            for moon_data in config.MOON_DATA[planet.name]:
                moon_speed = (
                    self.engine.circular_orbit_speed(
                        planet.mass,
                        moon_data["orbital_radius"],
                    )
                    * moon_data["speed_factor"]
                )

                moon = Moon(
                    name=moon_data["name"],
                    description=moon_data["description"],
                    mass=moon_data["mass"],
                    radius=moon_data["radius"],
                    color=moon_data["color"],
                    parent=planet,
                    orbital_radius=moon_data["orbital_radius"],
                    orbital_speed=moon_speed,
                )
                planet.add_moon(moon)
                self.moons.append(moon)

                if planet.name == "Earth" and moon.name == "Moon":
                    self.moon = moon

        dwarf_data = config.DWARF_PLANET_DATA
        dwarf_speed = (
            self.engine.circular_orbit_speed(
                self.star.mass,
                dwarf_data["orbital_radius"],
            )
            * dwarf_data["speed_factor"]
        )

        self.pluto = DwarfPlanet(
            name=dwarf_data["name"],
            description=dwarf_data["description"],
            mass=dwarf_data["mass"],
            radius=dwarf_data["radius"],
            color=dwarf_data["color"],
            orbital_radius=dwarf_data["orbital_radius"],
            orbital_speed=dwarf_speed,
            classification=dwarf_data["classification"],
            x=float(config.CX + dwarf_data["orbital_radius"]),
            y=float(config.CY),
        )
        self.engine.add_body(self.pluto)

    def update(self, speed_multiplier: float = 1.0):
        """
        Advance all global physics bodies by one frame.

        Args:
            speed_multiplier: User-controlled time scaling factor.
        """
        self.engine.step(speed_multiplier)

    def draw(self, screen, zoom: float = 1.0):
        """
        Draw the world using a camera transform centered on the Sun.

        Args:
            screen: Active pygame surface.
            zoom: Visual scale factor. Values below 1.0 zoom out, values above
                1.0 zoom in.

        The physics coordinates are not permanently changed. Each body is
        temporarily transformed into screen space, drawn, and then restored.
        """
        cx = screen.get_width() // 2
        cy = screen.get_height() // 2
        sx = self.star.position[0]
        sy = self.star.position[1]

        def apply_camera(body):
            """
            Temporarily convert one body's position, radius, and trail.

            Returns:
                Tuple containing original position, radius, and trail data.
            """
            original_x, original_y = body.position[0], body.position[1]
            original_radius = body.radius
            original_trail = body.trail[:]

            body.position[0] = (original_x - sx) * zoom + cx
            body.position[1] = (original_y - sy) * zoom + cy
            body.radius = max(original_radius * zoom, 1.5)
            body.trail = [
                ((tx - sx) * zoom + cx, (ty - sy) * zoom + cy)
                for tx, ty in original_trail
            ]
            return original_x, original_y, original_radius, original_trail

        def restore_body(body, original_x, original_y, original_radius, original_trail):
            """
            Restore one body after temporary camera-space drawing.
            """
            body.position[0] = original_x
            body.position[1] = original_y
            body.radius = original_radius
            body.trail = original_trail

        saved = apply_camera(self.star)
        self.star.draw(screen)
        restore_body(self.star, *saved)

        for planet in self.planets:
            planet_saved = apply_camera(planet)
            moon_saved = [apply_camera(moon) for moon in planet.moons]
            planet.draw(screen)
            restore_body(planet, *planet_saved)
            for moon, saved_state in zip(planet.moons, moon_saved):
                restore_body(moon, *saved_state)

        saved = apply_camera(self.pluto)
        self.pluto.draw(screen)
        restore_body(self.pluto, *saved)

    def all_bodies(self):
        """
        Return a flat list of all bodies owned by the solar system.

        Returns:
            List containing the Sun, planets, moons, and Pluto.
        """
        all_moons = [moon for planet in self.planets for moon in planet.moons]
        return [self.star] + self.planets + all_moons + [self.pluto]
