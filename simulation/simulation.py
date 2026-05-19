"""
simulation.py

Top-level pygame runtime for the Solar System Simulator.

The Simulation class owns the main window, input handling, physics updates,
rendering, HUD text, and the Qian Xuesen easter egg launcher.
"""

import sys

import pygame

import config
from easter_egg.qian_xuesen import QianXuesenMission
from simulation.solar_system import SolarSystem


class Simulation:
    """
    Main application controller.

    Attributes:
        screen: Main pygame display surface.
        clock: Frame-rate controller.
        solar_system: World model and physics engine wrapper.
        speed_multiplier: User-controlled physics time scale.
        zoom: User-controlled visual camera scale.
        running: Main loop flag.
        mission: Qian Xuesen easter egg launcher.
    """

    MIN_SPEED = 0.1
    MAX_SPEED = 10.0
    SPEED_STEP = 0.5

    def __init__(self):
        """
        Initialize pygame, create the window, and build the simulation world.
        """
        pygame.init()
        pygame.display.set_caption(config.TITLE)

        self.screen = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.clock = pygame.time.Clock()
        self.solar_system = SolarSystem()
        self.speed_multiplier = 1.0
        self.zoom = 0.62
        self.running = True
        self.mission = QianXuesenMission()

    def run(self):
        """
        Run the main pygame loop until the user quits.

        Each frame handles input, updates simulation state, draws the current
        frame, and then waits just enough to maintain the configured FPS.
        """
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(config.FPS)

        pygame.quit()
        sys.exit()

    def _handle_events(self):
        """
        Process all queued pygame events for the current frame.

        Keyboard controls:
            Escape or Q: quit
            Plus: increase simulation speed
            Minus: decrease simulation speed
            R: open the Qian Xuesen solar-return easter egg

        Mouse wheel controls the camera zoom.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.speed_multiplier = min(
                        self.speed_multiplier + self.SPEED_STEP,
                        self.MAX_SPEED,
                    )

                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed_multiplier = max(
                        self.speed_multiplier - self.SPEED_STEP,
                        self.MIN_SPEED,
                    )

                elif event.key == pygame.K_r:
                    self.mission.launch()

            elif event.type == pygame.MOUSEWHEEL:
                self.zoom = max(0.20, min(3.0, self.zoom + event.y * 0.05))

    def _update(self):
        """
        Advance simulation state for one frame.

        The solar system receives the current speed multiplier. The easter egg
        launcher only needs to update its cooldown timer.
        """
        self.solar_system.update(self.speed_multiplier)
        self.mission.update(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    def _draw(self):
        """
        Draw one complete frame and present it to the display.
        """
        self.screen.fill((5, 5, 15))
        self.solar_system.draw(self.screen, self.zoom)
        self.mission.draw(self.screen)
        self._draw_hud()
        pygame.display.flip()

    def _draw_hud(self):
        """
        Draw speed, zoom, controls, and tracked body count.

        The HUD is intentionally minimal so it does not cover the orbital
        visualization. All text is English to keep the project consistent.
        """
        font = pygame.font.SysFont("Arial", 13)
        small = pygame.font.SysFont("Arial", 11)

        speed_txt = font.render(
            (
                f"Speed: {self.speed_multiplier:.1f}x  (+/-)     "
                f"Zoom: {self.zoom:.2f}x  (scroll wheel)"
            ),
            True,
            (180, 180, 180),
        )
        self.screen.blit(speed_txt, (10, 10))

        controls = [
            "+ / -      :  simulation speed",
            "Scroll     :  zoom in / out",
            "R          :  Qian Xuesen solar return",
            "ESC        :  quit",
        ]
        for i, line in enumerate(controls):
            surf = small.render(line, True, (100, 100, 100))
            self.screen.blit(surf, (10, 32 + i * 16))

        from core.star import Star as StarClass

        planet_names = list(
            map(
                lambda body: body.name,
                filter(
                    lambda body: not isinstance(body, StarClass),
                    self.solar_system.all_bodies(),
                ),
            )
        )
        count_txt = small.render(
            f"Tracking {len(planet_names)} bodies",
            True,
            (80, 80, 80),
        )
        self.screen.blit(count_txt, (10, 32 + len(controls) * 16 + 8))
