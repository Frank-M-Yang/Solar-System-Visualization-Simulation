"""
main.py
Entry point — run with:  python main.py

Solar System Simulator
======================
A real-time simulation of the solar system using Newtonian gravity.
All orbits emerge naturally from physics — no hardcoded ellipses.

Controls:
    + / -   Speed up / slow down
    R       Launch Qian Xuesen's lunar rocket (easter egg)
    ESC     Quit

Inspired by NASA's Artemis II mission (April 2026) and
Qian Xuesen's legendary exam problem for his aerospace students.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from simulation.simulation import Simulation


def main():
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()
