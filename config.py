"""
config.py
All simulation constants and planet data in one place.

Unit system:
  Distance : pixels  (1 AU ≈ 200 px)
  Mass     : scaled relative units  (Sun = 1.0)
  Time     : seconds (simulation time, not real time)

  G is tuned so that:
      v_circular = sqrt(G * M_sun / r)
      with M_sun = 1.0, r = 200 px  →  v ≈ 2.0 px/s
      G = v² * r / M_sun = 4 * 200 / 1.0 = 800
"""

# --- Window ---
SCREEN_WIDTH  = 1200
SCREEN_HEIGHT = 800
FPS           = 60
TITLE         = "Solar System Simulator"

# --- Physics ---
G  = 1e6      # scaled gravitational constant — tuned so Earth at r=150px
              # has orbital speed ~82 px/s, one orbit ≈ 11 real seconds
DT = 0.016    # base time step (~1 frame at 60fps)

# --- Centre of screen (where the Sun sits) ---
CX = SCREEN_WIDTH  // 2   # 600
CY = SCREEN_HEIGHT // 2   # 400

# --- Celestial body data (all in simulation units) ---
# mass          : relative to Sun = 1.0
# radius        : pixels
# orbital_radius: pixels from Sun  (0 for Sun itself)
# color         : RGB tuple

SUN_DATA = {
    "name"        : "Sun",
    "description" : "The star at the centre of our solar system",
    "mass"        : 1.0,
    "radius"      : 28,
    "color"       : (255, 220, 50),
    "luminosity"  : 1.0,
}

# Each entry is one planet; listed in order from the Sun.
# orbital_speed is computed from circular_orbit_speed() in PhysicsEngine,
# then optionally scaled (< 1.0 → elliptical orbit).
PLANET_DATA = [
    {
        "name"          : "Mercury",
        "description"   : "Smallest planet, closest to the Sun",
        "mass"          : 1.65e-7,
        "radius"        : 3,
        "color"         : (169, 169, 169),
        "orbital_radius": 60,
        "speed_factor"  : 1.0,    # 1.0 = circular,  <1.0 = elliptical
    },
    {
        "name"          : "Venus",
        "description"   : "Hottest planet, thick atmosphere",
        "mass"          : 2.45e-6,
        "radius"        : 6,
        "color"         : (255, 198, 120),
        "orbital_radius": 100,
        "speed_factor"  : 1.0,
    },
    {
        "name"          : "Earth",
        "description"   : "Our home planet",
        "mass"          : 3.0e-6,
        "radius"        : 7,
        "color"         : (70, 130, 180),
        "orbital_radius": 150,
        "speed_factor"  : 0.95,   # slightly elliptical, like the real orbit
    },
    {
        "name"          : "Mars",
        "description"   : "The red planet",
        "mass"          : 3.2e-7,
        "radius"        : 5,
        "color"         : (188, 74, 60),
        "orbital_radius": 210,
        "speed_factor"  : 0.93,
    },
    {
        "name"          : "Jupiter",
        "description"   : "Largest planet in the solar system",
        "mass"          : 9.5e-4,
        "radius"        : 18,
        "color"         : (201, 144, 57),
        "orbital_radius": 310,
        "speed_factor"  : 1.0,
    },
    {
        "name"          : "Saturn",
        "description"   : "Famous for its ring system",
        "mass"          : 2.86e-4,
        "radius"        : 15,
        "color"         : (210, 180, 100),
        "orbital_radius": 400,
        "speed_factor"  : 1.0,
    },
    {
        "name"          : "Uranus",
        "description"   : "Ice giant, rotates on its side",
        "mass"          : 4.36e-5,
        "radius"        : 11,
        "color"         : (173, 216, 230),
        "orbital_radius": 480,
        "speed_factor"  : 1.0,
    },
    {
        "name"          : "Neptune",
        "description"   : "Windiest planet, farthest from the Sun",
        "mass"          : 5.15e-5,
        "radius"        : 10,
        "color"         : (63, 84, 186),
        "orbital_radius": 550,
        "speed_factor"  : 1.0,
    },
]

# Dwarf planet
DWARF_PLANET_DATA = {
    "name"          : "Pluto",
    "description"   : "Dwarf planet, demoted in 2006",
    "mass"          : 6.6e-9,
    "radius"        : 2,
    "color"         : (188, 143, 143),
    "orbital_radius": 610,
    "speed_factor"  : 0.85,    # notably elliptical orbit
    "classification": "Dwarf Planet",
}

# Moon data — keyed by parent planet name
MOON_DATA = {
    "Earth": [
        {
            "name"          : "Moon",
            "description"   : "Earth's only natural satellite",
            "mass"          : 3.7e-8,
            "radius"        : 2,
            "color"         : (200, 200, 200),
            "orbital_radius": 20,
            "speed_factor"  : 1.0,
        }
    ],
    "Jupiter": [
        {
            "name"          : "Io",
            "description"   : "Most volcanically active body in the solar system",
            "mass"          : 4.5e-8,
            "radius"        : 2,
            "color"         : (255, 255, 100),
            "orbital_radius": 28,
            "speed_factor"  : 1.0,
        },
        {
            "name"          : "Europa",
            "description"   : "Icy moon, possible subsurface ocean",
            "mass"          : 3.9e-8,
            "radius"        : 2,
            "color"         : (200, 220, 255),
            "orbital_radius": 36,
            "speed_factor"  : 1.0,
        },
    ],
}

# --- Rocket (Qian Xuesen easter egg) ---
ROCKET_DATA = {
    "name"          : "Rocket",
    "description"   : "Qian Xuesen's lunar mission challenge",
    "mass"          : 1e-15,   # negligible mass, won't affect other bodies
    "radius"        : 2,
    "color"         : (255, 80, 80),
    "boost_speed"   : 3.5,     # extra speed added on top of Earth's velocity
}