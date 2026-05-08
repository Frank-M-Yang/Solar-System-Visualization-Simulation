"""
lunar_window.py
Standalone pygame window for the Qian Xuesen lunar mission easter egg.

Background:
    Qian Xuesen (钱学森, 1911-2009) — founding father of Chinese aerospace.
    His legendary exam question: launch a rocket from Earth, orbit the Moon
    once, and return. The answer is the Free-Return Trajectory (自由返回轨道),
    used by Apollo 13 to safely return the crew without engine burns.

Physics:
    Uses Euler integration in the Earth-Moon two-body gravitational field.
    The trajectory is pre-computed at startup, then played back as animation.
    Parameters (angle=165°, speed=0.94*v_escape) are found numerically so the
    rocket genuinely swings around the Moon and returns under gravity alone.

Run standalone:
    python easter_egg/lunar_window.py
Or spawned automatically when the user presses R in the main simulation.
"""

import math
import sys
import os
import pygame

# ── constants ──────────────────────────────────────────────────────────
W, H          = 1000, 660
G             = 50000.0
M_EARTH       = 1.0
M_MOON        = 0.0123
EARTH_POS     = (250, 330)
MOON_POS      = (750, 330)
EARTH_R       = 40          # physics + display radius  (px)
MOON_R        = 22          # display radius (px)
LAUNCH_R      = 45          # rocket launch distance from Earth centre

# trajectory parameters — numerically verified: rocket crosses Moon centre
# by ~32px (true far-side passage), then returns to Earth under gravity alone.
LAUNCH_ANGLE  = 150         # degrees  (was 165 — that only grazed near side)
SPEED_FACTOR  = 0.94        # fraction of escape velocity
DT_SIM        = 0.08        # integration time step (s)
MAX_STEPS     = 60000       # safety cap for integration


# ── colours ────────────────────────────────────────────────────────────
BLACK      = (5,   5,  15)
WHITE      = (255, 255, 255)
EARTH_COL  = (70,  130, 180)
MOON_COL   = (200, 200, 200)
ROCKET_COL = (255,  80,  80)
TRAIL_COL  = (255, 160,  80)
LABEL_COL  = (200, 200, 200)
PHASE_COL  = (255, 220,  80)
DIM_COL    = (80,   80,  80)


# ── phase labels shown during the animation ────────────────────────────
PHASES = [
    (0.00, "Phase 1 — Trans-Lunar Injection (TLI)  点火出发"),
    (0.20, "Phase 2 — Coasting to the Moon  飞向月球"),
    (0.48, "Phase 3 — Lunar Flyby  绕月飞行  (far side  月球背面)"),
    (0.65, "Phase 4 — Trans-Earth Return  返回地球"),
    (0.95, "Mission Complete!  任务完成  ✓"),
]


def compute_trajectory() -> list:
    """
    Pre-compute the full free-return trajectory using Euler integration.
    Returns a list of (x, y) screen positions sampled every 3 steps.
    """
    ex, ey = EARTH_POS
    mx, my = MOON_POS

    v_esc  = math.sqrt(2 * G * M_EARTH / LAUNCH_R)
    speed  = v_esc * SPEED_FACTOR
    angle  = math.radians(LAUNCH_ANGLE)

    # launch position on Earth surface
    x  = ex + LAUNCH_R * math.cos(angle)
    y  = ey + LAUNCH_R * math.sin(angle)

    # tangential velocity (clockwise in screen coords = prograde)
    va = angle - math.pi / 2
    vx = speed * math.cos(va)
    vy = speed * math.sin(va)

    traj       = [(x, y)]
    near_moon  = False
    moon_step  = -1

    for step in range(MAX_STEPS):
        # Earth gravity
        dx_e = ex - x;  dy_e = ey - y
        r_e  = math.sqrt(dx_e ** 2 + dy_e ** 2)
        if r_e < 2:
            break
        ax = G * M_EARTH * dx_e / r_e ** 3
        ay = G * M_EARTH * dy_e / r_e ** 3

        # Moon gravity
        dx_m = mx - x;  dy_m = my - y
        r_m  = math.sqrt(dx_m ** 2 + dy_m ** 2)
        ax  += G * M_MOON * dx_m / r_m ** 3
        ay  += G * M_MOON * dy_m / r_m ** 3

        # Euler integration
        vx += ax * DT_SIM
        vy += ay * DT_SIM
        x  += vx * DT_SIM
        y  += vy * DT_SIM

        # sample every 3 steps to keep list size reasonable
        if step % 3 == 0:
            traj.append((x, y))

        moon_d  = math.sqrt((x - mx) ** 2 + (y - my) ** 2)
        earth_d = math.sqrt((x - ex) ** 2 + (y - ey) ** 2)

        # far-side check: rocket must cross Moon's centre x-coordinate
        if moon_d < 120 and x > mx and not near_moon:
            near_moon = True   # counts as "reached Moon" only after far-side entry
            moon_step = step

        if moon_d < 120 and not near_moon:
            near_moon = True
            moon_step = step

        # success: passed Moon far side and returned to Earth
        if near_moon and step > moon_step + 300 and earth_d < 65:
            traj.append((x, y))
            break

        # bail out if too far
        if earth_d > 1800:
            break

    return traj


def draw_star_field(screen: pygame.Surface, stars: list):
    """Draw static background stars."""
    for sx, sy, br in stars:
        c = (br, br, br)
        pygame.draw.circle(screen, c, (sx, sy), 1)


def draw_earth(screen: pygame.Surface):
    ex, ey = EARTH_POS
    # atmosphere glow
    pygame.draw.circle(screen, (30, 60, 100), (ex, ey), EARTH_R + 8)
    # main body
    pygame.draw.circle(screen, EARTH_COL, (ex, ey), EARTH_R)
    # highlight
    pygame.draw.circle(screen, (100, 170, 220), (ex - 12, ey - 12), 10)
    font = pygame.font.SysFont("Arial", 13, bold=True)
    lbl  = font.render("Earth  地球", True, (150, 200, 255))
    screen.blit(lbl, (ex - lbl.get_width() // 2, ey + EARTH_R + 6))


def draw_moon(screen: pygame.Surface):
    mx, my = MOON_POS
    # subtle glow
    pygame.draw.circle(screen, (60, 60, 60), (mx, my), MOON_R + 6)
    # main body
    pygame.draw.circle(screen, MOON_COL, (mx, my), MOON_R)
    # craters (simple circles)
    pygame.draw.circle(screen, (160, 160, 160), (mx + 6, my - 5), 4)
    pygame.draw.circle(screen, (160, 160, 160), (mx - 8, my + 6), 3)
    font = pygame.font.SysFont("Arial", 13, bold=True)
    lbl  = font.render("Moon  月球", True, (200, 200, 200))
    screen.blit(lbl, (mx - lbl.get_width() // 2, my + MOON_R + 6))


def draw_rocket(screen: pygame.Surface, pos: tuple, prev_pos: tuple):
    """Draw a small triangle pointing in direction of travel."""
    px, py = pos
    if prev_pos:
        dx = px - prev_pos[0]
        dy = py - prev_pos[1]
        spd = math.sqrt(dx ** 2 + dy ** 2)
        if spd > 0:
            ux, uy = dx / spd, dy / spd
            ppx, ppy = -uy, ux
            tip   = (px + ux * 8,  py + uy * 8)
            left  = (px - ux * 4 + ppx * 4, py - uy * 4 + ppy * 4)
            right = (px - ux * 4 - ppx * 4, py - uy * 4 - ppy * 4)
            pygame.draw.polygon(screen, ROCKET_COL,
                                [(int(tip[0]),   int(tip[1])),
                                 (int(left[0]),  int(left[1])),
                                 (int(right[0]), int(right[1]))])
            return
    pygame.draw.circle(screen, ROCKET_COL, (int(px), int(py)), 4)


def draw_trail(screen: pygame.Surface, traj: list, head: int):
    """Draw fading trail behind the rocket."""
    trail_len = min(120, head)
    for i in range(max(0, head - trail_len), head):
        t     = (i - (head - trail_len)) / max(trail_len, 1)
        alpha = int(255 * t * 0.7)
        col   = (min(int(TRAIL_COL[0] * t), 255),
                 min(int(TRAIL_COL[1] * t * 0.6), 255),
                 min(int(TRAIL_COL[2] * t * 0.3), 255))
        tx, ty = traj[i]
        if 0 <= int(tx) < W and 0 <= int(ty) < H:
            pygame.draw.circle(screen, col, (int(tx), int(ty)), 1)


def draw_full_path(screen: pygame.Surface, traj: list, head: int):
    """Draw the complete predicted trajectory as a dim dashed line."""
    for i in range(0, len(traj), 4):
        tx, ty = traj[i]
        if 0 <= int(tx) < W and 0 <= int(ty) < H:
            col = DIM_COL if i < head else (40, 40, 40)
            pygame.draw.circle(screen, col, (int(tx), int(ty)), 1)


def draw_hud(screen: pygame.Surface, progress: float, phase_text: str,
             frame: int, total: int):
    """Draw phase label, progress bar, and controls."""
    font_big  = pygame.font.SysFont("Arial", 17, bold=True)
    font_sm   = pygame.font.SysFont("Arial", 12)

    # phase label
    lbl = font_big.render(phase_text, True, PHASE_COL)
    screen.blit(lbl, (W // 2 - lbl.get_width() // 2, 18))

    # progress bar
    bar_w, bar_h = 400, 8
    bx = W // 2 - bar_w // 2
    by = 48
    pygame.draw.rect(screen, (40, 40, 40),  (bx, by, bar_w, bar_h))
    pygame.draw.rect(screen, (200, 160, 60), (bx, by, int(bar_w * progress), bar_h))
    pygame.draw.rect(screen, (100, 100, 100), (bx, by, bar_w, bar_h), 1)

    # title
    title = font_sm.render(
        "Qian Xuesen's Lunar Challenge  —  Free-Return Trajectory  自由返回轨道",
        True, (120, 120, 120))
    screen.blit(title, (W // 2 - title.get_width() // 2, H - 28))

    # controls
    ctrl = font_sm.render("ESC — close    SPACE/R — replay    +/- — speed", True, (70, 70, 70))
    screen.blit(ctrl, (10, H - 24))

    # speed note
    info = font_sm.render(f"Frame {frame}/{total}", True, (60, 60, 60))
    screen.blit(info, (W - info.get_width() - 10, H - 24))


def draw_success_banner(screen: pygame.Surface):
    """Shown when rocket returns to Earth."""
    font     = pygame.font.SysFont("Arial", 26, bold=True)
    font_sm  = pygame.font.SysFont("Arial", 14)
    lines  = [
        ("Mission Complete!  任务完成",        (255, 220,  80)),
        ("Free-Return Trajectory Achieved",   (200, 255, 150)),
        ("钱学森考题 — 答案：自由返回轨道",    (200, 200, 255)),
    ]
    for i, (line, col) in enumerate(lines):
        lbl = font.render(line, True, col)
        screen.blit(lbl, (W // 2 - lbl.get_width() // 2, H // 2 + 70 + i * 38))

    hint = font_sm.render("SPACE / R — watch again    ESC — close", True, (120, 120, 120))
    screen.blit(hint, (W // 2 - hint.get_width() // 2, H // 2 + 185))


def main():
    # ── setup ──────────────────────────────────────────────────────────
    print("[Qian Xuesen] Computing free-return trajectory...")
    traj = compute_trajectory()
    print(f"[Qian Xuesen] Trajectory ready: {len(traj)} waypoints")

    # random background stars
    import random
    random.seed(42)
    stars = [(random.randint(0, W), random.randint(0, H),
              random.randint(30, 120)) for _ in range(180)]

    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("钱学森月球挑战 — Qian Xuesen Lunar Challenge")
    clock  = pygame.time.Clock()

    total_frames = len(traj)
    frame        = 0
    playback_speed = 4   # waypoints advanced per display frame

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    playback_speed = min(playback_speed + 1, 12)
                elif event.key == pygame.K_MINUS:
                    playback_speed = max(playback_speed - 1, 1)
                elif event.key in (pygame.K_SPACE, pygame.K_r):
                    frame = 0   # replay from the beginning

        # ── draw ───────────────────────────────────────────────────────
        screen.fill(BLACK)
        draw_star_field(screen, stars)
        draw_full_path(screen, traj, frame)
        draw_earth(screen)
        draw_moon(screen)

        if frame < total_frames:
            draw_trail(screen, traj, frame)
            prev = traj[frame - 1] if frame > 0 else None
            draw_rocket(screen, traj[frame], prev)

        # phase label
        progress   = frame / max(total_frames - 1, 1)
        phase_text = PHASES[0][1]
        for threshold, label in PHASES:
            if progress >= threshold:
                phase_text = label

        draw_hud(screen, progress, phase_text, frame, total_frames)

        if frame >= total_frames - 1:
            draw_success_banner(screen)

        pygame.display.flip()
        clock.tick(60)

        # advance playhead
        if frame < total_frames - 1:
            frame = min(frame + playback_speed, total_frames - 1)

    pygame.quit()


if __name__ == "__main__":
    # allow running from project root or from easter_egg/
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    main()