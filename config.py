"""
config.py

Central configuration for the Solar System Simulator.

The project uses scaled units rather than real SI units:
    Distance: pixels on the simulation canvas
    Mass: relative simulation mass, with the Sun set to 1.0
    Time: simulation seconds, advanced once per pygame frame

The gravitational constant is intentionally tuned for a visually pleasing
desktop simulation. It is not the real physical constant. The goal is to keep
orbital periods short enough to watch while preserving Newtonian behavior.
"""

# Window settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TITLE = "Solar System Simulator"

# Physics settings
G = 1e6
DT = 0.016

# Screen center, used as the initial Sun position.
CX = SCREEN_WIDTH // 2
CY = SCREEN_HEIGHT // 2

# Data schema for celestial bodies:
#   name: display label
#   description: short English description
#   mass: relative mass in simulation units
#   radius: visual radius in pixels
#   color: RGB tuple used by pygame
#   orbital_radius: initial distance from the Sun in pixels
#   speed_factor: multiplier applied to the circular-orbit speed

SUN_DATA = {
    "name": "Sun",
    "description": "The star at the center of our solar system",
    "mass": 1.0,
    "radius": 28,
    "color": (255, 220, 50),
    "luminosity": 1.0,
}

PLANET_DATA = [
    {
        "name": "Mercury",
        "description": "Smallest planet and closest to the Sun",
        "mass": 1.65e-7,
        "radius": 3,
        "color": (169, 169, 169),
        "orbital_radius": 60,
        "speed_factor": 1.0,
    },
    {
        "name": "Venus",
        "description": "Hottest planet, with a thick atmosphere",
        "mass": 2.45e-6,
        "radius": 6,
        "color": (255, 198, 120),
        "orbital_radius": 100,
        "speed_factor": 1.0,
    },
    {
        "name": "Earth",
        "description": "Our home planet",
        "mass": 3.0e-6,
        "radius": 7,
        "color": (70, 130, 180),
        "orbital_radius": 150,
        "speed_factor": 0.95,
    },
    {
        "name": "Mars",
        "description": "The red planet",
        "mass": 3.2e-7,
        "radius": 5,
        "color": (188, 74, 60),
        "orbital_radius": 210,
        "speed_factor": 0.93,
    },
    {
        "name": "Jupiter",
        "description": "Largest planet in the solar system",
        "mass": 9.5e-4,
        "radius": 18,
        "color": (201, 144, 57),
        "orbital_radius": 310,
        "speed_factor": 1.0,
    },
    {
        "name": "Saturn",
        "description": "Gas giant famous for its ring system",
        "mass": 2.86e-4,
        "radius": 15,
        "color": (210, 180, 100),
        "orbital_radius": 400,
        "speed_factor": 1.0,
    },
    {
        "name": "Uranus",
        "description": "Ice giant with an unusual axial tilt",
        "mass": 4.36e-5,
        "radius": 11,
        "color": (173, 216, 230),
        "orbital_radius": 480,
        "speed_factor": 1.0,
    },
    {
        "name": "Neptune",
        "description": "Distant ice giant with powerful winds",
        "mass": 5.15e-5,
        "radius": 10,
        "color": (63, 84, 186),
        "orbital_radius": 550,
        "speed_factor": 1.0,
    },
]

DWARF_PLANET_DATA = {
    "name": "Pluto",
    "description": "Dwarf planet beyond Neptune",
    "mass": 6.6e-9,
    "radius": 2,
    "color": (188, 143, 143),
    "orbital_radius": 610,
    "speed_factor": 0.85,
    "classification": "Dwarf Planet",
}

MOON_DATA = {
    "Earth": [
        {
            "name": "Moon",
            "description": "Earth's only natural satellite",
            "mass": 3.7e-8,
            "radius": 2,
            "color": (200, 200, 200),
            "orbital_radius": 20,
            "speed_factor": 1.0,
        }
    ],
    "Jupiter": [
        {
            "name": "Io",
            "description": "Volcanically active Jovian moon",
            "mass": 4.5e-8,
            "radius": 2,
            "color": (255, 255, 100),
            "orbital_radius": 28,
            "speed_factor": 1.0,
        },
        {
            "name": "Europa",
            "description": "Icy Jovian moon with a possible ocean",
            "mass": 3.9e-8,
            "radius": 2,
            "color": (200, 220, 255),
            "orbital_radius": 36,
            "speed_factor": 1.0,
        },
    ],
}

ROCKET_DATA = {
    "name": "Rocket",
    "description": "Generic rocket data reserved for future missions",
    "mass": 1e-15,
    "radius": 2,
    "color": (255, 80, 80),
    "boost_speed": 3.5,
}
