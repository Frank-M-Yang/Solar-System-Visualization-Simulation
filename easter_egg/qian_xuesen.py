"""
qian_xuesen.py
Manages the Qian Xuesen easter egg in the main simulation.

When the user presses R, this spawns lunar_window.py as a separate
subprocess — giving it its own pygame window and event loop,
completely independent from the main solar system simulation.

The main simulation keeps running in the background while the
lunar window is open.
"""

import sys
import os
import subprocess
import pygame


class QianXuesenMission:
    """
    Handles the R-key trigger in the main simulation.
    Spawns the lunar challenge window as a child process.

    Attributes:
        _proc      (subprocess.Popen | None): Handle to the child process
        _cooldown  (int): Frame counter to prevent rapid re-spawning
    """

    COOLDOWN_FRAMES = 120   # 2 seconds at 60fps before R can be pressed again

    def __init__(self):
        self._proc     = None
        self._cooldown = 0

    # ------------------------------------------------------------------
    # Called from Simulation.handle_events() on K_r
    # ------------------------------------------------------------------

    def launch(self):
        """
        Spawn the lunar challenge window as a subprocess.
        Only one instance at a time; ignored if already running.
        """
        if self._cooldown > 0:
            return

        # if a previous window is still open, don't open another
        if self._proc is not None and self._proc.poll() is None:
            return

        # path to lunar_window.py (relative to this file's directory)
        window_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "lunar_window.py"
        )

        # project root (one level above easter_egg/)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self._proc = subprocess.Popen(
            [sys.executable, window_script],
            cwd=project_root,
        )
        self._cooldown = self.COOLDOWN_FRAMES
        print("[Easter Egg] Qian Xuesen window launched.")

    # ------------------------------------------------------------------
    # Called every frame from Simulation._update()
    # ------------------------------------------------------------------

    def update(self, screen_width: int = 0, screen_height: int = 0):
        """Tick down the cooldown counter each frame."""
        if self._cooldown > 0:
            self._cooldown -= 1

    # ------------------------------------------------------------------
    # Draw the R-key hint in the main simulation HUD
    # ------------------------------------------------------------------

    def draw(self, screen: pygame.Surface):
        """Show a small hint in the corner of the main window."""
        font = pygame.font.SysFont("Arial", 12)

        active = self._proc is not None and self._proc.poll() is None
        if active:
            text  = "Qian Xuesen window is open  (press R again to reopen)"
            color = (80, 180, 80)
        else:
            text  = "Press R — Qian Xuesen's Lunar Challenge  (钱学森月球挑战)"
            color = (130, 130, 130)

        hint = font.render(text, True, color)
        screen.blit(hint, (10, screen.get_height() - 25))
