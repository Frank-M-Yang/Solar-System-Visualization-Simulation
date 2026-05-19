"""
solar_return_window.py

Standalone pygame window for the Qian Xuesen solar-return easter egg.

The classroom-style problem asks for a simplified trajectory: launch a rocket
from Earth, let it travel around the Sun, and return to Earth's position.

Model assumptions:
    1. Earth moves on a circular heliocentric orbit of radius R = 1 AU.
    2. Earth's angular speed is n_E = sqrt(mu_sun / R^3).
    3. After leaving Earth's sphere of influence, the rocket feels only the Sun.
    4. Motion stays in the ecliptic plane.
    5. Other planets, solar radiation pressure, and relativity are ignored.
    6. Launch and return are treated as position coincidence.

Run standalone:
    python easter_egg/solar_return_window.py
"""

import math
import os
import random
import sys

import pygame


W, H = 1120, 720
CX, CY = 315, H // 2
FPS = 60

R_EARTH = 145.0
MU_SUN = 1.0
N_EARTH = math.sqrt(MU_SUN / R_EARTH ** 3)
EARTH_PERIOD = 2 * math.pi / N_EARTH

RETURN_YEARS = 2
ROCKET_PERIOD = RETURN_YEARS * EARTH_PERIOD
SEMI_MAJOR = R_EARTH * RETURN_YEARS ** (2 / 3)
PERIHELION = R_EARTH
APHELION = 2 * SEMI_MAJOR - PERIHELION
V_EARTH = math.sqrt(MU_SUN / R_EARTH)
V_ROCKET_0 = math.sqrt(MU_SUN * (2 / PERIHELION - 1 / SEMI_MAJOR))
DELTA_V = V_ROCKET_0 - V_EARTH

DT_SIM = EARTH_PERIOD / 1800
MAX_STEPS = int(ROCKET_PERIOD / DT_SIM) + 8
SAMPLE_EVERY = 2

BLACK = (5, 5, 15)
PANEL = (14, 18, 30)
PANEL_LINE = (45, 52, 72)
SUN_COL = (255, 213, 74)
EARTH_COL = (70, 130, 190)
ROCKET_COL = (255, 92, 84)
TRAIL_COL = (255, 164, 80)
ORBIT_COL = (70, 80, 105)
TEXT_COL = (215, 218, 225)
MUTED_COL = (120, 128, 145)
GREEN = (150, 235, 170)
PHASE_COL = (255, 224, 120)
DIM_COLOR_ACTIVE = (105, 80, 55)

PHASES = [
    (0.00, "Phase 1 - Launch from Earth orbit"),
    (0.12, "Phase 2 - Faster heliocentric ellipse"),
    (0.42, "Phase 3 - Around the Sun, near aphelion"),
    (0.68, "Phase 4 - Falling back toward 1 AU"),
    (0.95, "Return - Earth and rocket positions coincide"),
]


def compute_trajectory() -> list[dict]:
    """
    Precompute the Earth and rocket paths for the demonstration.

    Returns:
        List of dictionaries. Each dictionary stores rocket position, Earth
        position, elapsed model time, and elapsed Earth years.

    Earth is evaluated analytically as:
        r_E(t) = R * (cos(n_E t), sin(n_E t))

    The rocket is integrated with:
        r'' = -mu_sun * r / |r|^3

    The chosen initial speed gives the rocket a two-Earth-year period. At the
    end of one rocket revolution, Earth has also completed two revolutions.
    """
    x, y = R_EARTH, 0.0
    vx, vy = 0.0, V_ROCKET_0
    samples = []

    for step in range(MAX_STEPS):
        t = step * DT_SIM
        theta = N_EARTH * t
        earth = (R_EARTH * math.cos(theta), R_EARTH * math.sin(theta))

        if step % SAMPLE_EVERY == 0:
            samples.append(
                {
                    "rocket": (x, y),
                    "earth": earth,
                    "time": t,
                    "years": t / EARTH_PERIOD,
                }
            )

        radius = math.sqrt(x * x + y * y)
        ax = -MU_SUN * x / radius ** 3
        ay = -MU_SUN * y / radius ** 3

        vx += ax * DT_SIM
        vy += ay * DT_SIM
        x += vx * DT_SIM
        y += vy * DT_SIM

    samples.append(
        {
            "rocket": (R_EARTH, 0.0),
            "earth": (R_EARTH, 0.0),
            "time": ROCKET_PERIOD,
            "years": RETURN_YEARS,
        }
    )
    return samples


def to_screen(point: tuple[float, float]) -> tuple[int, int]:
    """
    Convert model coordinates into pygame screen coordinates.

    Args:
        point: Tuple (x, y) in model coordinates.

    Returns:
        Tuple (screen_x, screen_y), with y flipped for screen space.
    """
    x, y = point
    return int(CX + x), int(CY - y)


def draw_text(
    screen: pygame.Surface,
    text: str,
    pos: tuple[int, int],
    font: pygame.font.Font,
    color=TEXT_COL,
):
    """
    Render one text string and blit it to the screen.

    Args:
        screen: Active pygame surface.
        text: English text to draw.
        pos: Top-left screen position.
        font: pygame Font object.
        color: RGB text color.

    Returns:
        Rect occupied by the rendered text.
    """
    surface = font.render(text, True, color)
    screen.blit(surface, pos)
    return surface.get_rect(topleft=pos)


def draw_star_field(screen: pygame.Surface, stars: list[tuple[int, int, int]]):
    """
    Draw static background stars.

    Args:
        screen: Active pygame surface.
        stars: List of (x, y, brightness) tuples.
    """
    for sx, sy, brightness in stars:
        pygame.draw.circle(screen, (brightness, brightness, brightness), (sx, sy), 1)


def draw_orbits(screen: pygame.Surface):
    """
    Draw Earth's circular orbit and the rocket transfer ellipse.

    Args:
        screen: Active pygame surface.
    """
    pygame.draw.circle(screen, ORBIT_COL, (CX, CY), int(R_EARTH), 1)
    rect = pygame.Rect(0, 0, int(2 * APHELION), int(2 * SEMI_MAJOR))
    rect.center = (CX + int(SEMI_MAJOR - R_EARTH), CY)
    pygame.draw.ellipse(screen, (72, 55, 42), rect, 1)


def draw_sun(screen: pygame.Surface, font: pygame.font.Font):
    """
    Draw the Sun with a simple layered glow.

    Args:
        screen: Active pygame surface.
        font: Font used for the label.
    """
    pygame.draw.circle(screen, (80, 55, 20), (CX, CY), 38)
    pygame.draw.circle(screen, (150, 105, 30), (CX, CY), 27)
    pygame.draw.circle(screen, SUN_COL, (CX, CY), 18)
    draw_text(screen, "Sun", (CX - 12, CY + 24), font, (255, 232, 150))


def draw_earth(
    screen: pygame.Surface,
    pos: tuple[float, float],
    font: pygame.font.Font,
):
    """
    Draw Earth at its current analytical orbit position.

    Args:
        screen: Active pygame surface.
        pos: Earth model coordinates.
        font: Font used for the label.
    """
    sx, sy = to_screen(pos)
    pygame.draw.circle(screen, (26, 48, 82), (sx, sy), 13)
    pygame.draw.circle(screen, EARTH_COL, (sx, sy), 8)
    pygame.draw.circle(screen, (130, 190, 230), (sx - 3, sy - 3), 3)
    draw_text(screen, "Earth", (sx + 10, sy - 8), font, (155, 200, 255))


def draw_rocket(
    screen: pygame.Surface,
    pos: tuple[float, float],
    prev: tuple[float, float] | None,
):
    """
    Draw the rocket as a small triangle aligned with its motion.

    Args:
        screen: Active pygame surface.
        pos: Current rocket model coordinates.
        prev: Previous rocket model coordinates, or None at launch.
    """
    sx, sy = to_screen(pos)
    if prev is None:
        pygame.draw.circle(screen, ROCKET_COL, (sx, sy), 4)
        return

    px, py = to_screen(prev)
    dx, dy = sx - px, sy - py
    speed = math.hypot(dx, dy)
    if speed < 0.01:
        pygame.draw.circle(screen, ROCKET_COL, (sx, sy), 4)
        return

    ux, uy = dx / speed, dy / speed
    nx, ny = -uy, ux
    tip = (sx + ux * 10, sy + uy * 10)
    left = (sx - ux * 6 + nx * 5, sy - uy * 6 + ny * 5)
    right = (sx - ux * 6 - nx * 5, sy - uy * 6 - ny * 5)
    pygame.draw.polygon(screen, ROCKET_COL, [tip, left, right])


def draw_path(screen: pygame.Surface, trajectory: list[dict], head: int):
    """
    Draw the full predicted path and a brighter recent trail.

    Args:
        screen: Active pygame surface.
        trajectory: Precomputed trajectory samples.
        head: Current playback frame index.
    """
    for i in range(0, len(trajectory), 5):
        sx, sy = to_screen(trajectory[i]["rocket"])
        color = DIM_COLOR_ACTIVE if i <= head else (45, 38, 34)
        if 0 <= sx < W and 0 <= sy < H:
            pygame.draw.circle(screen, color, (sx, sy), 1)

    trail_start = max(0, head - 150)
    for i in range(trail_start, head):
        t = (i - trail_start) / max(head - trail_start, 1)
        col = (
            int(TRAIL_COL[0] * t),
            int(TRAIL_COL[1] * t * 0.75),
            int(TRAIL_COL[2] * t * 0.45),
        )
        sx, sy = to_screen(trajectory[i]["rocket"])
        if 0 <= sx < W and 0 <= sy < H:
            pygame.draw.circle(screen, col, (sx, sy), 2)


def draw_panel(
    screen: pygame.Surface,
    sample: dict,
    progress: float,
    frame: int,
    total: int,
    playback_speed: int,
):
    """
    Draw the right-side explanation and controls panel.

    Args:
        screen: Active pygame surface.
        sample: Current trajectory sample.
        progress: Playback progress from 0.0 to 1.0.
        frame: Current frame index.
        total: Total number of trajectory frames.
        playback_speed: Number of samples advanced per display frame.
    """
    panel_rect = pygame.Rect(745, 28, 345, 664)
    pygame.draw.rect(screen, PANEL, panel_rect, border_radius=6)
    pygame.draw.rect(screen, PANEL_LINE, panel_rect, 1, border_radius=6)

    title_font = pygame.font.SysFont("Arial", 18, bold=True)
    font = pygame.font.SysFont("Arial", 13)
    small = pygame.font.SysFont("Arial", 12)

    y = 48
    draw_text(screen, "Qian Xuesen Solar Return", (765, y), title_font, PHASE_COL)
    y += 34
    draw_text(screen, "Classroom two-body model", (765, y), font, TEXT_COL)
    y += 38

    draw_text(screen, "Model equations", (765, y), font, GREEN)
    y += 24
    equations = [
        "Earth: r_E = R(cos n_E t, sin n_E t)",
        "n_E = sqrt(mu_sun / R^3)",
        "Rocket: r'' = -mu_sun r / |r|^3",
        "r(0) = r_E(0)",
        "v(0) = v_E + Delta v",
    ]
    for line in equations:
        draw_text(screen, line, (765, y), small, TEXT_COL)
        y += 20

    y += 12
    draw_text(screen, "Assumptions", (765, y), font, GREEN)
    y += 24
    assumptions = [
        "1. Earth orbit is circular, R = 1 AU.",
        "2. Solar gravity dominates after launch.",
        "3. Motion stays in the ecliptic plane.",
        "4. Ignore planets, radiation, relativity.",
        "5. Return means matching position.",
    ]
    for line in assumptions:
        draw_text(screen, line, (765, y), small, MUTED_COL)
        y += 20

    y += 12
    draw_text(screen, "Demo parameter choice", (765, y), font, GREEN)
    y += 24
    demo = [
        f"Rocket period: {RETURN_YEARS} Earth years",
        f"a = R * {RETURN_YEARS}^(2/3) = {SEMI_MAJOR / R_EARTH:.3f} AU",
        f"v0 = {V_ROCKET_0 / V_EARTH:.3f} * v_E",
        f"Delta v = {DELTA_V / V_EARTH:.3f} * v_E",
        f"Elapsed time: {sample['years']:.2f} years",
    ]
    for line in demo:
        draw_text(screen, line, (765, y), small, TEXT_COL)
        y += 20

    y += 18
    bar_w, bar_h = 290, 9
    pygame.draw.rect(screen, (42, 45, 56), (765, y, bar_w, bar_h), border_radius=3)
    pygame.draw.rect(
        screen,
        (220, 170, 70),
        (765, y, int(bar_w * progress), bar_h),
        border_radius=3,
    )
    y += 25
    draw_text(
        screen,
        f"Frame {frame}/{total - 1}   speed {playback_speed}x",
        (765, y),
        small,
        MUTED_COL,
    )

    y += 40
    controls = [
        "SPACE / R : replay",
        "+ / -     : playback speed",
        "P         : pause / resume",
        "ESC       : close",
    ]
    for line in controls:
        draw_text(screen, line, (765, y), small, (150, 156, 170))
        y += 21


def current_phase(progress: float) -> str:
    """
    Select the current phase label from the playback progress.

    Args:
        progress: Value from 0.0 to 1.0.

    Returns:
        English phase label for the current progress value.
    """
    phase = PHASES[0][1]
    for threshold, text in PHASES:
        if progress >= threshold:
            phase = text
    return phase


def draw_phase_banner(screen: pygame.Surface, phase: str):
    """
    Draw the current phase label above the orbit scene.

    Args:
        screen: Active pygame surface.
        phase: Phase label returned by current_phase.
    """
    font = pygame.font.SysFont("Arial", 18, bold=True)
    label = font.render(phase, True, PHASE_COL)
    screen.blit(label, (CX - label.get_width() // 2, 28))


def draw_success_banner(screen: pygame.Surface):
    """
    Draw the completion message after the return frame is reached.

    Args:
        screen: Active pygame surface.
    """
    font = pygame.font.SysFont("Arial", 22, bold=True)
    small = pygame.font.SysFont("Arial", 13)
    lines = [
        ("Return achieved: rocket and Earth meet at 1 AU", GREEN),
        ("Simplified model complete: one heliocentric loop returns to Earth.", TEXT_COL),
    ]
    base_y = 610
    for i, (text, color) in enumerate(lines):
        label = font.render(text, True, color) if i == 0 else small.render(text, True, color)
        screen.blit(label, (CX - label.get_width() // 2, base_y + i * 32))


def main():
    """
    Run the standalone easter egg pygame application.

    The function precomputes the trajectory once, then plays it back as an
    animation with replay, pause, and speed controls.
    """
    print("[Qian Xuesen] Computing solar-return trajectory...")
    trajectory = compute_trajectory()
    print(f"[Qian Xuesen] Trajectory ready: {len(trajectory)} samples")

    random.seed(42)
    stars = [
        (random.randint(0, W), random.randint(0, H), random.randint(30, 125))
        for _ in range(220)
    ]

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Qian Xuesen Solar Return")
    clock = pygame.time.Clock()

    frame = 0
    playback_speed = 3
    paused = False
    running = True
    total = len(trajectory)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    playback_speed = min(playback_speed + 1, 12)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    playback_speed = max(playback_speed - 1, 1)
                elif event.key in (pygame.K_SPACE, pygame.K_r):
                    frame = 0
                    paused = False
                elif event.key == pygame.K_p:
                    paused = not paused

        sample = trajectory[frame]
        progress = frame / max(total - 1, 1)

        screen.fill(BLACK)
        draw_star_field(screen, stars)
        draw_orbits(screen)
        draw_path(screen, trajectory, frame)
        draw_sun(screen, pygame.font.SysFont("Arial", 11))
        draw_earth(screen, sample["earth"], pygame.font.SysFont("Arial", 11))
        prev = trajectory[frame - 1]["rocket"] if frame > 0 else None
        draw_rocket(screen, sample["rocket"], prev)
        draw_phase_banner(screen, current_phase(progress))
        draw_panel(screen, sample, progress, frame, total, playback_speed)

        if frame >= total - 1:
            draw_success_banner(screen)

        pygame.display.flip()
        clock.tick(FPS)

        if not paused and frame < total - 1:
            frame = min(frame + playback_speed, total - 1)

    pygame.quit()


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    main()
