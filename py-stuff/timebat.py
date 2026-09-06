#!/usr/bin/env python3
"""
timerbar.py — a minimal, sharp CLI countdown progress bar.

Asks the user for a duration in seconds or minutes, then fills a
single-line progress bar in real time until the duration elapses.

No external dependencies. Works in any ANSI-capable terminal.
"""

from __future__ import annotations

import sys
import time
import shutil


# ---- visual configuration -------------------------------------------------

BAR_CHAR_FILLED = "█"
BAR_CHAR_EMPTY = "░"
BAR_MIN_WIDTH = 10
BAR_MAX_WIDTH = 50

COLOR_RESET = "\x1b[0m"
COLOR_DIM = "\x1b[2m"
COLOR_BOLD = "\x1b[1m"
COLOR_ACCENT = "\x1b[38;5;80m"   # soft cyan
COLOR_TRACK = "\x1b[38;5;238m"   # dark gray track
COLOR_DONE = "\x1b[38;5;82m"     # green on completion

CURSOR_HIDE = "\x1b[?25l"
CURSOR_SHOW = "\x1b[?25h"


# ---- input handling ---------------------------------------------------------

def prompt_duration() -> float:
    """Ask the user for a duration in seconds or minutes, return seconds."""
    print(f"{COLOR_BOLD}timerbar{COLOR_RESET}{COLOR_DIM} — minimal countdown{COLOR_RESET}\n")

    unit = ""
    while unit not in ("s", "m"):
        unit = input("Unit — (s)econds or (m)inutes: ").strip().lower()
        if unit in ("sec", "secs", "second", "seconds"):
            unit = "s"
        elif unit in ("min", "mins", "minute", "minutes"):
            unit = "m"
        if unit not in ("s", "m"):
            print(f"{COLOR_DIM}  please type 's' or 'm'{COLOR_RESET}")

    value = None
    while value is None:
        raw = input(f"Duration in {'seconds' if unit == 's' else 'minutes'}: ").strip()
        try:
            value = float(raw)
            if value <= 0:
                print(f"{COLOR_DIM}  must be greater than 0{COLOR_RESET}")
                value = None
        except ValueError:
            print(f"{COLOR_DIM}  not a valid number{COLOR_RESET}")

    return value * 60 if unit == "m" else value


# ---- rendering ---------------------------------------------------------------

def format_time(seconds: float) -> str:
    seconds = max(0, int(round(seconds)))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def bar_width() -> int:
    term_width = shutil.get_terminal_size(fallback=(80, 24)).columns
    # reserve space for percentage + time readout on either side
    available = term_width - 20
    return max(BAR_MIN_WIDTH, min(BAR_MAX_WIDTH, available))


def render(elapsed: float, total: float, done: bool = False) -> str:
    width = bar_width()
    fraction = min(1.0, elapsed / total) if total > 0 else 1.0
    filled = int(round(fraction * width))
    empty = width - filled

    bar_color = COLOR_DONE if done else COLOR_ACCENT
    bar = (
        f"{bar_color}{BAR_CHAR_FILLED * filled}"
        f"{COLOR_TRACK}{BAR_CHAR_EMPTY * empty}{COLOR_RESET}"
    )

    percent = f"{int(fraction * 100):3d}%"
    remaining = format_time(max(0.0, total - elapsed))
    elapsed_str = format_time(elapsed)

    label = f"{COLOR_DIM}{elapsed_str}{COLOR_RESET}" if not done else f"{COLOR_DONE}done{COLOR_RESET}"

    return f"\r{bar_color}{percent}{COLOR_RESET} │{bar}│ {label} {COLOR_DIM}-{remaining}{COLOR_RESET}  "


def run(total_seconds: float) -> None:
    tick = 0.05  # refresh interval, seconds — smooth without hammering the CPU
    start = time.monotonic()

    sys.stdout.write(CURSOR_HIDE)
    sys.stdout.flush()

    try:
        while True:
            elapsed = time.monotonic() - start
            done = elapsed >= total_seconds
            sys.stdout.write(render(min(elapsed, total_seconds), total_seconds, done=done))
            sys.stdout.flush()
            if done:
                break
            time.sleep(tick)
    except KeyboardInterrupt:
        sys.stdout.write(f"\n{COLOR_DIM}interrupted{COLOR_RESET}\n")
        sys.stdout.flush()
        return
    finally:
        sys.stdout.write(CURSOR_SHOW)
        sys.stdout.flush()

    print(f"\n\n{COLOR_DONE}{COLOR_BOLD}✓ complete{COLOR_RESET}")


def main() -> None:
    try:
        total_seconds = prompt_duration()
        print()
        run(total_seconds)
    except (KeyboardInterrupt, EOFError):
        sys.stdout.write(CURSOR_SHOW)
        print(f"\n{COLOR_DIM}cancelled{COLOR_RESET}")


if __name__ == "__main__":
    main()
