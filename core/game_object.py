"""
game_object.py

Defines the smallest shared object model used by the simulation.

Every visible or simulated entity has a name, a human-readable description, and
a mutable two-dimensional position. More specialized classes add physics,
rendering, and mission-specific behavior on top of this base state.
"""


class GameObject:
    """
    Base class for all named objects in the simulation world.

    The class deliberately stores position as a mutable list instead of a tuple
    because the physics engine updates coordinates in place every frame.

    Attributes:
        name: Display name used in labels and debugging output.
        description: Short English description of the object.
        position: Two-item list containing x and y simulation coordinates.
    """

    def __init__(self, name: str, description: str, x: float = 0.0, y: float = 0.0):
        """
        Initialize shared identity and position data.

        Args:
            name: Display name for the object.
            description: Short text explaining what the object represents.
            x: Initial x coordinate in simulation space.
            y: Initial y coordinate in simulation space.
        """
        self.name = name
        self.description = description
        self.position = [x, y]

    def __repr__(self):
        """
        Return a compact debug representation.

        The representation is useful when printing lists of objects from tests
        or diagnostics because it includes both type and current position.
        """
        return f"{self.__class__.__name__}(name='{self.name}', pos={self.position})"
