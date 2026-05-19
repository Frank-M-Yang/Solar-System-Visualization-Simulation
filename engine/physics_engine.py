"""
physics_engine.py

Newtonian gravity engine for the main solar system simulation.

The engine computes pairwise gravitational acceleration between registered
CelestialBody instances and advances each movable body with symplectic Euler
integration:

    acceleration = G * other_mass / distance_squared
    velocity = velocity + acceleration * dt
    position = position + velocity * dt

The implementation first computes all accelerations from the same snapshot of
positions, then applies movement. That avoids order-dependent behavior.
"""

import math

import config
from core.celestial_body import CelestialBody
from core.star import Star


class PhysicsEngine:
    """
    Manage bodies and advance them through gravitational interaction.

    Attributes:
        G: Scaled gravitational constant from config.py.
        bodies: List of CelestialBody objects registered with the engine.
        dt: Base time step in simulation seconds.
    """

    G = config.G

    def __init__(self, dt: float = 0.1):
        """
        Create an empty physics engine.

        Args:
            dt: Base simulation time step. Smaller values improve accuracy but
                require more frames to show visible movement.
        """
        self.bodies: list[CelestialBody] = []
        self.dt = dt

    def add_body(self, body: CelestialBody):
        """
        Register a body so it participates in gravity calculations.

        Args:
            body: CelestialBody instance to add.
        """
        self.bodies.append(body)

    def remove_body(self, body: CelestialBody):
        """
        Remove a body from the engine if it is currently registered.

        Args:
            body: CelestialBody instance to remove.
        """
        if body in self.bodies:
            self.bodies.remove(body)

    def step(self, speed_multiplier: float = 1.0):
        """
        Advance the whole simulation by one scaled time step.

        Args:
            speed_multiplier: User-controlled factor applied to dt.

        Stars are skipped during movement because this project treats them as
        fixed anchors. Planets still receive acceleration from the Sun and from
        each other. If a moved body owns moons, their local hierarchical orbits
        are updated after the parent moves.
        """
        dt = self.dt * speed_multiplier
        accels = self._compute_all_accelerations()

        for body in self.bodies:
            if isinstance(body, Star):
                continue

            ax, ay = accels.get(id(body), (0.0, 0.0))

            body.velocity[0] += ax * dt
            body.velocity[1] += ay * dt

            body.trail.append((body.position[0], body.position[1]))
            if len(body.trail) > body.TRAIL_LENGTH:
                body.trail.pop(0)

            body.position[0] += body.velocity[0] * dt
            body.position[1] += body.velocity[1] * dt

            if hasattr(body, "moons"):
                body.update(dt)

    def _compute_all_accelerations(self) -> dict:
        """
        Compute net acceleration for every registered body.

        Returns:
            Dictionary mapping id(body) to an (ax, ay) acceleration tuple.

        Every unique body pair is evaluated once. The equal-and-opposite
        accelerations from that pair are accumulated into each body's total.
        """
        accels = {id(body): [0.0, 0.0] for body in self.bodies}

        pairs = [
            (self.bodies[i], self.bodies[j])
            for i in range(len(self.bodies))
            for j in range(i + 1, len(self.bodies))
        ]

        for b1, b2 in pairs:
            ax1, ay1, ax2, ay2 = self._compute_pair_acceleration(b1, b2)
            accels[id(b1)][0] += ax1
            accels[id(b1)][1] += ay1
            accels[id(b2)][0] += ax2
            accels[id(b2)][1] += ay2

        return {key: tuple(value) for key, value in accels.items()}

    def _compute_pair_acceleration(
        self,
        b1: CelestialBody,
        b2: CelestialBody,
    ) -> tuple:
        """
        Compute mutual gravitational acceleration between two bodies.

        Args:
            b1: First body in the pair.
            b2: Second body in the pair.

        Returns:
            Tuple (ax1, ay1, ax2, ay2), where the first two values are the
            acceleration on b1 and the last two values are the acceleration on
            b2.

        The calculation uses the acceleration form of Newton's law:
            a_on_1 = G * mass_2 / r_squared
            a_on_2 = G * mass_1 / r_squared

        A small softening value is added to distance squared so overlapping
        bodies do not cause division by zero or extreme acceleration spikes.
        """
        dx = b2.position[0] - b1.position[0]
        dy = b2.position[1] - b1.position[1]

        r_sq = dx * dx + dy * dy
        epsilon = 1.0
        r_sq_soft = r_sq + epsilon
        r = math.sqrt(r_sq_soft)

        a1_mag = self.G * b2.mass / r_sq_soft
        a2_mag = self.G * b1.mass / r_sq_soft

        ux = dx / r
        uy = dy / r

        ax1, ay1 = a1_mag * ux, a1_mag * uy
        ax2, ay2 = -a2_mag * ux, -a2_mag * uy

        return ax1, ay1, ax2, ay2

    def circular_orbit_speed(self, central_mass: float, orbital_radius: float) -> float:
        """
        Compute the tangential speed for a circular orbit.

        Args:
            central_mass: Mass of the body being orbited.
            orbital_radius: Distance from the central body.

        Returns:
            Speed in pixels per second.

        The formula comes from balancing gravity with centripetal acceleration:
            G * central_mass / radius_squared = speed_squared / radius
        which reduces to:
            speed = sqrt(G * central_mass / radius)
        """
        return math.sqrt(self.G * central_mass / orbital_radius)
