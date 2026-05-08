"""
simulation.py
Main pygame loop — handles rendering, user input, HUD, and the easter egg.

Controls:
    +  /  =     Increase simulation speed
    -           Decrease simulation speed
    R           Launch Qian Xuesen's rocket (easter egg)
    ESC / Q     Quit
"""

import sys
import pygame
import config
from simulation.solar_system  import SolarSystem
from easter_egg.qian_xuesen   import QianXuesenMission


class Simulation:
    """
    Top-level controller for the solar system simulation.

    Attributes:
        screen           (pygame.Surface): Main display surface
        clock            (pygame.time.Clock): Frame rate controller
        solar_system     (SolarSystem)   : All bodies + physics engine
        mission          (QianXuesenMission): Easter egg manager
        speed_multiplier (float)         : Simulation speed (1.0 = normal)
        running          (bool)          : Main loop flag
    """

    MIN_SPEED = 0.1
    MAX_SPEED = 10.0
    SPEED_STEP = 0.5

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.TITLE)

        self.screen           = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        )
        self.clock            = pygame.time.Clock()
        self.solar_system     = SolarSystem()
        self.speed_multiplier = 1.0
        self.zoom             = 0.62   # default: fits all planets incl. Pluto
        self.running          = True

        # Easter egg — needs Earth and Moon references from the world
        self.mission = QianXuesenMission()

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        """Start and maintain the main simulation loop."""
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(config.FPS)

        pygame.quit()
        sys.exit()

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _handle_events(self):
        """Process all pygame events for the current frame."""
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:

                # quit
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    self.running = False

                # speed up
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self.speed_multiplier = min(
                        self.speed_multiplier + self.SPEED_STEP, self.MAX_SPEED
                    )

                # slow down
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self.speed_multiplier = max(
                        self.speed_multiplier - self.SPEED_STEP, self.MIN_SPEED
                    )

                # easter egg
                elif event.key == pygame.K_r:
                    self.mission.launch()

            elif event.type == pygame.MOUSEWHEEL:
                # scroll up = zoom in, scroll down = zoom out
                self.zoom = max(0.20, min(3.0, self.zoom + event.y * 0.05))

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def _update(self):
        """Advance physics and check easter egg status."""
        self.solar_system.update(self.speed_multiplier)
        self.mission.update(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    # ------------------------------------------------------------------
    # Draw
    # ------------------------------------------------------------------

    def _draw(self):
        """Render everything onto the screen."""
        self.screen.fill((5, 5, 15))          # deep space background

        self.solar_system.draw(self.screen, self.zoom)    # all celestial bodies
        self.mission.draw(self.screen)         # rocket + easter egg UI

        self._draw_hud()                       # speed + controls overlay

        pygame.display.flip()

    def _draw_hud(self):
        """Draw the heads-up display: speed indicator and key hints."""
        font      = pygame.font.SysFont("Arial", 13)
        small     = pygame.font.SysFont("Arial", 11)

        # speed display
        speed_txt = font.render(
            f"Speed: {self.speed_multiplier:.1f}x  (+/-)     Zoom: {self.zoom:.2f}x  (scroll wheel)",
            True, (180, 180, 180),
        )
        self.screen.blit(speed_txt, (10, 10))

        # controls
        controls = [
            "+ / -      :  simulation speed",
            "Scroll     :  zoom in / out",
            "R          :  Qian Xuesen rocket",
            "ESC        :  quit",
        ]
        for i, line in enumerate(controls):
            surf = small.render(line, True, (100, 100, 100))
            self.screen.blit(surf, (10, 32 + i * 16))

        # body count — uses map to extract names, filter to skip Star
        from core.star import Star as StarClass
        planet_names = list(map(
            lambda b: b.name,
            filter(lambda b: not isinstance(b, StarClass), self.solar_system.all_bodies())
        ))
        count_txt = small.render(
            f"Tracking {len(planet_names)} bodies",
            True, (80, 80, 80),
        )
        self.screen.blit(count_txt, (10, 32 + len(controls) * 16 + 8))