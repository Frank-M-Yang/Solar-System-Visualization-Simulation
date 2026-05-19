"""
main.py

Application entry point for the Solar System Simulator.

Run from the project root with:
    python main.py

The main function creates a Simulation object and delegates all runtime work
to that object. Keeping this file small makes startup easy to understand and
keeps pygame-specific logic inside the simulation package.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from simulation.simulation import Simulation


def main():
    """
    Create and run the top-level simulation controller.

    The Simulation class owns pygame initialization, the event loop, rendering,
    physics updates, and the Qian Xuesen easter egg launcher. This function is
    intentionally thin so the command-line entry point has no hidden state.
    """
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()
