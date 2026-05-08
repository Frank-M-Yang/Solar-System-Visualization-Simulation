"""
solar_system.py
World manager — builds all celestial bodies from config.py
and registers them with the PhysicsEngine.
"""

import config
from core.star             import Star
from core.planet           import Planet
from core.moon             import Moon
from core.dwarf_planet     import DwarfPlanet
from engine.physics_engine import PhysicsEngine


class SolarSystem:
    """
    Constructs and owns all celestial bodies in the simulation.

    Attributes:
        engine  (PhysicsEngine): Shared physics engine
        star    (Star)         : The Sun
        planets (list)         : All 8 planets
        pluto   (DwarfPlanet)  : Pluto
        moons   (list)         : All moons across all planets
        earth   (Planet)       : Quick reference to Earth (for easter egg)
        moon    (Moon)         : Quick reference to Earth's Moon
    """

    def __init__(self):
        self.engine  = PhysicsEngine(dt=config.DT)
        self.star    = None
        self.planets = []
        self.pluto   = None
        self.moons   = []
        self.earth   = None
        self.moon    = None
        self._build()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self):
        """Instantiate every body from config and register with the engine."""

        # Sun
        self.star = Star(
            **{k: v for k, v in config.SUN_DATA.items()},
            x=float(config.CX),
            y=float(config.CY),
        )
        self.engine.add_body(self.star)

        # Planets
        for pd in config.PLANET_DATA:
            v = (self.engine.circular_orbit_speed(self.star.mass, pd["orbital_radius"])
                 * pd["speed_factor"])

            planet = Planet(
                name           = pd["name"],
                description    = pd["description"],
                mass           = pd["mass"],
                radius         = pd["radius"],
                color          = pd["color"],
                orbital_radius = pd["orbital_radius"],
                orbital_speed  = v,
                x              = float(config.CX + pd["orbital_radius"]),
                y              = float(config.CY),
            )
            self.planets.append(planet)
            self.engine.add_body(planet)

            if pd["name"] == "Earth":
                self.earth = planet

        # Moons — filter() finds planets that have moon entries in config
        for planet in filter(lambda p: p.name in config.MOON_DATA, self.planets):
            for md in config.MOON_DATA[planet.name]:
                mv = (self.engine.circular_orbit_speed(planet.mass, md["orbital_radius"])
                      * md["speed_factor"])

                moon = Moon(
                    name           = md["name"],
                    description    = md["description"],
                    mass           = md["mass"],
                    radius         = md["radius"],
                    color          = md["color"],
                    parent         = planet,
                    orbital_radius = md["orbital_radius"],
                    orbital_speed  = mv,
                )
                planet.add_moon(moon)
                self.moons.append(moon)
                # Moons use hierarchical orbits — NOT registered with PhysicsEngine
                # They are updated by Planet.update() each frame instead

                if planet.name == "Earth" and md["name"] == "Moon":
                    self.moon = moon

        # Pluto (Dwarf Planet)
        dd = config.DWARF_PLANET_DATA
        dv = (self.engine.circular_orbit_speed(self.star.mass, dd["orbital_radius"])
              * dd["speed_factor"])

        self.pluto = DwarfPlanet(
            name           = dd["name"],
            description    = dd["description"],
            mass           = dd["mass"],
            radius         = dd["radius"],
            color          = dd["color"],
            orbital_radius = dd["orbital_radius"],
            orbital_speed  = dv,
            classification = dd["classification"],
            x              = float(config.CX + dd["orbital_radius"]),
            y              = float(config.CY),
        )
        self.engine.add_body(self.pluto)

    # ------------------------------------------------------------------
    # Per-frame update and draw
    # ------------------------------------------------------------------

    def update(self, speed_multiplier: float = 1.0):
        """Step the physics engine forward."""
        self.engine.step(speed_multiplier)

    def draw(self, screen, zoom: float = 1.0):
        """
        Draw all bodies with camera zoom applied.
        Physics positions are unchanged — only the visual transform differs.

        Args:
            screen (pygame.Surface): Display surface
            zoom   (float): Scale factor; <1.0 zooms out, >1.0 zooms in
        """
        cx = screen.get_width()  // 2
        cy = screen.get_height() // 2
        sx = self.star.position[0]
        sy = self.star.position[1]

        def apply(body):
            """Temporarily transform body position/radius/trail for drawing."""
            ox, oy = body.position[0], body.position[1]
            or_    = body.radius
            otrail = body.trail[:]
            body.position[0] = (ox - sx) * zoom + cx
            body.position[1] = (oy - sy) * zoom + cy
            body.radius       = max(or_ * zoom, 1.5)
            body.trail        = [((tx - sx) * zoom + cx,
                                  (ty - sy) * zoom + cy)
                                 for tx, ty in otrail]
            return ox, oy, or_, otrail

        def restore(body, ox, oy, or_, otrail):
            """Restore original physics values after drawing."""
            body.position[0] = ox
            body.position[1] = oy
            body.radius       = or_
            body.trail        = otrail

        # star
        saved = apply(self.star)
        self.star.draw(screen)
        restore(self.star, *saved)

        # planets + their moons
        for planet in self.planets:
            p_saved = apply(planet)
            m_saved = [apply(m) for m in planet.moons]
            planet.draw(screen)
            restore(planet, *p_saved)
            for moon, ms in zip(planet.moons, m_saved):
                restore(moon, *ms)

        # pluto
        saved = apply(self.pluto)
        self.pluto.draw(screen)
        restore(self.pluto, *saved)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def all_bodies(self):
        """
        Flat list of every celestial body in the simulation.
        Uses list comprehension to flatten each planet's moon list.
        """
        all_moons = [moon for planet in self.planets for moon in planet.moons]
        return [self.star] + self.planets + all_moons + [self.pluto]