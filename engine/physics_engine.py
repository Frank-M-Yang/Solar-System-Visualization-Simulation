"""
physics_engine.py

Computes gravitational interactions between all celestial bodies
and advances their positions by one time step.

Integration method: Symplectic (Semi-implicit) Euler
  - Update velocity first using acceleration
  - Then update position using the NEW velocity
  This keeps energy approximately conserved over long simulations,
  preventing orbits from slowly spiralling in or out.

Key formula:
  F  = G * m1 * m2 / r²          (Newton's law of gravitation)
  a  = F / m                      (Newton's second law)
  v  += a * dt                    (velocity update)
  x  += v * dt                    (position update, using new v)
"""

import math
from core.celestial_body import CelestialBody
from core.star           import Star
import config


class PhysicsEngine:
    """
    Manages all celestial bodies and steps the simulation forward.

    Attributes:
        G       (float): Gravitational constant, scaled for the simulation.
                         Real value is 6.674e-11 N·m²/kg² but we use a
                         scaled version so the simulation fits on screen.
        bodies  (list):  All CelestialBody instances in the simulation.
        dt      (float): Base time step in seconds (scaled simulation time).
        _accels (dict):  Stores computed accelerations before applying them,
                         so all bodies are updated simultaneously (not sequentially).
    """

    # Gravitational constant loaded from config.py (simulation units).
    # Tuned so circular_orbit_speed() returns ~2 px/s at 200 px with M_sun=1.0
    G = config.G

    def __init__(self, dt: float = 0.1):
        """
        Args:
            dt (float): Simulation time step. Smaller = more accurate, slower.
        """
        self.bodies: list[CelestialBody] = []
        self.dt = dt

    # ------------------------------------------------------------------
    # Body management
    # ------------------------------------------------------------------

    def add_body(self, body: CelestialBody):
        """
        Register a celestial body with the engine.

        Args:
            body (CelestialBody): The body to add (Star, Planet, Moon, Rocket…)
        """
        self.bodies.append(body)

    def remove_body(self, body: CelestialBody):
        """
        Remove a body from the simulation (e.g. rocket that flew off screen).

        Args:
            body (CelestialBody): The body to remove
        """
        if body in self.bodies:
            self.bodies.remove(body)

    # ------------------------------------------------------------------
    # Core physics step
    # ------------------------------------------------------------------

    def step(self, speed_multiplier: float = 1.0):
        """
        Advance the entire simulation by one time step.

        Process:
          1. Compute net gravitational acceleration on every non-Star body
             from every other body.
          2. Apply Symplectic Euler integration to update velocities and positions.

        Stars are skipped (they are fixed anchors and do not move).

        Args:
            speed_multiplier (float): Scale factor for dt, controlled by the user
                                      pressing +/- keys. Default 1.0 = real sim speed.
        """
        dt = self.dt * speed_multiplier

        # --- step 1: compute accelerations for all non-star bodies ---
        # We collect all accelerations first so every body is updated
        # using positions from the SAME moment (not a mix of old and new).
        accels = self._compute_all_accelerations()

        # --- step 2: apply Symplectic Euler integration ---
        for body in self.bodies:
            if isinstance(body, Star):
                continue   # stars are stationary

            ax, ay = accels.get(id(body), (0.0, 0.0))

            # update velocity first (symplectic step)
            body.velocity[0] += ax * dt
            body.velocity[1] += ay * dt

            # record trail snapshot
            body.trail.append((body.position[0], body.position[1]))
            if len(body.trail) > body.TRAIL_LENGTH:
                body.trail.pop(0)

            # update position using new velocity
            body.position[0] += body.velocity[0] * dt
            body.position[1] += body.velocity[1] * dt

            # if this body has moons, update them hierarchically
            if hasattr(body, 'moons'):
                body.update(dt)

    # ------------------------------------------------------------------
    # Acceleration calculation
    # ------------------------------------------------------------------

    def _compute_all_accelerations(self) -> dict:
        """
        Compute net gravitational acceleration on every body from all others.

        Returns:
            dict: { id(body): (ax, ay) } for every non-Star body
        """
        accels = {id(b): [0.0, 0.0] for b in self.bodies}

        # iterate over every unique pair (i, j) — use list comprehension
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

        return {k: tuple(v) for k, v in accels.items()}

    def _compute_pair_acceleration(
        self,
        b1: CelestialBody,
        b2: CelestialBody,
    ) -> tuple:
        """
        Compute the mutual gravitational acceleration between two bodies.

        Uses Newton's law:
            F  = G * m1 * m2 / r²
            a1 = F / m1  (acceleration on b1 toward b2)
            a2 = F / m2  (acceleration on b2 toward b1, opposite direction)

        A softening factor ε is added to r² to prevent numerical explosion
        when two bodies get extremely close (avoids division by near-zero).

        Args:
            b1, b2 (CelestialBody): The two bodies interacting

        Returns:
            tuple: (ax1, ay1, ax2, ay2) — accelerations for b1 and b2
        """
        dx = b2.position[0] - b1.position[0]
        dy = b2.position[1] - b1.position[1]

        r_sq = dx * dx + dy * dy

        # softening factor — only prevents singularity when bodies
        # overlap completely; tiny value preserves accuracy at normal distances
        epsilon = 1.0
        r_sq_soft = r_sq + epsilon

        r = math.sqrt(r_sq_soft)

        # gravitational acceleration magnitude for each body
        # a1 = G * m2 / r²,  a2 = G * m1 / r²
        a1_mag = self.G * b2.mass / r_sq_soft
        a2_mag = self.G * b1.mass / r_sq_soft

        # unit vector from b1 → b2
        ux = dx / r
        uy = dy / r

        # b1 accelerates toward b2, b2 accelerates toward b1 (opposite)
        ax1, ay1 =  a1_mag * ux,  a1_mag * uy
        ax2, ay2 = -a2_mag * ux, -a2_mag * uy

        return ax1, ay1, ax2, ay2

    # ------------------------------------------------------------------
    # Helpers used by SolarSystem to set up initial circular orbits
    # ------------------------------------------------------------------

    def circular_orbit_speed(self, central_mass: float, orbital_radius: float) -> float:
        """
        Compute the tangential speed needed for a perfectly circular orbit.

        Formula derived from balancing gravitational force and centripetal force:
            G * M * m / r² = m * v² / r
            →  v = sqrt(G * M / r)

        Args:
            central_mass   (float): Mass of the body being orbited (e.g. the Sun)
            orbital_radius (float): Distance between the two bodies in pixels

        Returns:
            float: Speed in pixels/second for a circular orbit
        """
        return math.sqrt(self.G * central_mass / orbital_radius)
