"""
qian_xuesen.py

Launcher for the Qian Xuesen solar-return easter egg.

The main simulation calls QianXuesenMission.launch when the user presses R.
The launcher starts solar_return_window.py in a separate Python process so the
easter egg has its own pygame window and event loop.
"""

import os
import subprocess
import sys

import pygame


class QianXuesenMission:
    """
    Manage the R-key easter egg trigger.

    Attributes:
        _proc: Child process handle for the easter egg window.
        _cooldown: Frame countdown that prevents rapid repeated launches.
    """

    COOLDOWN_FRAMES = 120

    def __init__(self):
        """
        Create an idle mission launcher.
        """
        self._proc = None
        self._cooldown = 0

    def launch(self):
        """
        Start the solar-return demonstration window if it is not already open.

        The function ignores repeated launch requests during the cooldown and
        while the child process is still running.
        """
        if self._cooldown > 0:
            return

        if self._proc is not None and self._proc.poll() is None:
            return

        window_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "solar_return_window.py",
        )
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self._proc = subprocess.Popen(
            [sys.executable, window_script],
            cwd=project_root,
        )
        self._cooldown = self.COOLDOWN_FRAMES
        print("[Easter Egg] Qian Xuesen solar-return window launched.")

    def update(self, screen_width: int = 0, screen_height: int = 0):
        """
        Advance launcher state by one frame.

        Args:
            screen_width: Unused placeholder kept for interface stability.
            screen_height: Unused placeholder kept for interface stability.
        """
        if self._cooldown > 0:
            self._cooldown -= 1

    def draw(self, screen: pygame.Surface):
        """
        Draw a small English hint in the main simulation window.

        Args:
            screen: Active pygame surface.
        """
        font = pygame.font.SysFont("Arial", 12)

        active = self._proc is not None and self._proc.poll() is None
        if active:
            text = "Qian Xuesen solar-return window is open"
            color = (80, 180, 80)
        else:
            text = "Press R - Qian Xuesen's Solar Return Challenge"
            color = (130, 130, 130)

        hint = font.render(text, True, color)
        screen.blit(hint, (10, screen.get_height() - 25))
