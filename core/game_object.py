"""
game_object.py
Root base class for every object in the simulation.
All objects in the world share a position, name, and description.
"""


class GameObject:
    """
    The root base class for all objects in the solar system simulation.

    Attributes:
        name        (str):  Display name of the object
        description (str):  Short description
        position    (list): [x, y] coordinates in simulation space (pixels)
    """

    def __init__(self, name: str, description: str, x: float = 0.0, y: float = 0.0):
        self.name = name
        self.description = description
        self.position = [x, y]   # mutable list so subclasses can update in-place

    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}', pos={self.position})"
