"""
Shared utilities and base classes for Consulting Chaos game.
"""
from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable

try:
    import tkinter as tk
except Exception as e:  # pragma: no cover
    raise SystemExit("tkinter is required to run this game.\n" + str(e))

# ------------------------------
# Config & Theme
# ------------------------------
CANVAS_W, CANVAS_H = 800, 600
FPS_TARGET = 60

# Colors (BCG green theme)
BG = "#1a3a1e"  # Dark green background
FG = "#e8f5e8"  # Light green text
ACCENT = "#4CAF50"  # BCG green accent
GOOD = "#2E7D32"  # Dark green for success
BAD = "#d32f2f"  # Red for errors
WARN = "#ff9800"  # Orange for warnings
GRID = "#2d4a2d"  # Medium green for grids
MUTED = "#81c784"  # Muted green
CARD = "#2E7D32"  # Green cards

EMAIL_PENALTY_PER_MISS = 0.3
MATH_COUNT = 8
MATH_WRONG_PENALTY = 1.0

# Puzzle game constants
CAL_TARGET_SECONDS = 60.0
CAL_OVER_PENALTY_PER_10S = 2.0
CAL_LEFTOVER_PENALTY = 1.0

# Friday Escape constants
ESCAPE_ENEMIES = 4
ESCAPE_TAG_PENALTY = 2.0
ESCAPE_DECISION_INTERVAL = 0.5

SCORES_PATH = Path(__file__).parent / "consulting_chaos.scores.json"

JARGON = [
    "Let's circle back post-standup.",
    "Driving synergy for cross-functional KPIs.",
    "Deck alignment before EOD, thanks!",
    "Can we socialize the roadmap ASAP?",
    "Low-hanging fruit for Q4 quick wins.",
    "Double-click the assumptions and de-risk.",
    "Let's park this and revisit offline.",
    "Push the deck to green for tomorrow's steerco.",
]

# ------------------------------
# Utility
# ------------------------------

def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ------------------------------
# High Score Manager
# ------------------------------
class HighScoreManager:
    def __init__(self, path: Path = SCORES_PATH):
        self.path = path
        self.best_total_seconds: Optional[float] = None
        self.best_individual_times: dict[str, float] = {}
        self.leaderboard: list[dict] = []  # List of {"name": str, "title": str, "total": float, "individual": dict}
        self._load()

    def _load(self) -> None:
        try:
            if self.path.exists():
                data = json.loads(self.path.read_text(encoding="utf-8"))
                self.best_total_seconds = data.get("best_total_seconds")
                self.best_individual_times = data.get("best_individual_times", {})
                self.leaderboard = data.get("leaderboard", [])
        except Exception:
            self.best_total_seconds = None
            self.best_individual_times = {}
            self.leaderboard = []

    def maybe_update(self, total_seconds: float, individual_times: dict[str, float]) -> bool:
        """Return True if new personal best saved."""
        is_best = (
            self.best_total_seconds is None or total_seconds < self.best_total_seconds
        )
        
        # Update individual best times
        for game_name, time in individual_times.items():
            if game_name not in self.best_individual_times or time < self.best_individual_times[game_name]:
                self.best_individual_times[game_name] = time
        
        if not is_best:
            return False
        self.best_total_seconds = total_seconds
        self._save()
        return True

    def add_to_leaderboard(self, name: str, title: str, total_seconds: float, individual_times: dict[str, float]) -> int:
        """Add entry to leaderboard, return position (0-based)"""
        entry = {
            "name": name,
            "title": title,
            "total": total_seconds,
            "individual": individual_times,
            "date": time.time()
        }
        self.leaderboard.append(entry)
        self.leaderboard.sort(key=lambda x: x["total"])
        self._save()
        return self.leaderboard.index(entry)

    def _save(self) -> None:
        try:
            data = {
                "best_total_seconds": self.best_total_seconds,
                "best_individual_times": self.best_individual_times,
                "leaderboard": self.leaderboard[-10:]  # Keep only top 10
            }
            self.path.write_text(
                json.dumps(data, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass


# ------------------------------
# Scene System
# ------------------------------
class Scene:
    name: str = "Scene"

    def on_enter(self, app: "GameApp") -> None:
        pass

    def on_exit(self, app: "GameApp") -> None:
        pass

    def update(self, app: "GameApp", dt: float) -> None:
        pass

    def draw(self, app: "GameApp", c: tk.Canvas) -> None:
        pass

    def handle_key(self, app: "GameApp", e: tk.Event) -> None:
        pass


class SceneManager:
    def __init__(self, app: "GameApp"):
        self.app = app
        self.current: Optional[Scene] = None

    def switch(self, scene: Scene) -> None:
        if self.current:
            self.current.on_exit(self.app)
        self.current = scene
        self.current.on_enter(self.app)

    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(self.app, dt)

    def draw(self, c: tk.Canvas) -> None:
        if self.current:
            self.current.draw(self.app, c)

    def handle_key(self, e: tk.Event) -> None:
        if self.current:
            self.current.handle_key(self.app, e)


# ------------------------------
# Timing & Clock
# ------------------------------
class Clock:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.running = False
        self._last = 0.0

    def start(self, tick: Callable[[float], None]) -> None:
        self.running = True

        def loop():
            if not self.running:
                return
            now = time.perf_counter()
            dt = now - self._last if self._last else 1.0 / FPS_TARGET
            self._last = now
            # clamp dt to avoid jumps if the window is paused
            dt = min(dt, 1 / 15)
            tick(dt)
            self.root.after(int(1000 / FPS_TARGET), loop)

        loop()

    def stop(self) -> None:
        self.running = False


# ------------------------------
# Results Dataclass
# ------------------------------
@dataclass
class MinigameResult:
    name: str
    elapsed: float
    penalty: float
    detail: dict

    @property
    def total(self) -> float:
        return self.elapsed + self.penalty


# ------------------------------
# Simple Toast (text that fades)
# ------------------------------
class Toasts:
    def __init__(self):
        self.messages: list[tuple[str, float]] = []  # (text, ttl)

    def add(self, text: str, ttl: float = 1.5) -> None:
        self.messages.append((text, ttl))

    def update(self, dt: float) -> None:
        if not self.messages:
            return
        self.messages = [(t, ttl - dt) for (t, ttl) in self.messages if ttl - dt > 0]

    def draw(self, c: tk.Canvas) -> None:
        if not self.messages:
            return
        y = CANVAS_H - 40
        for text, ttl in self.messages[-3:]:
            alpha = clamp(ttl / 1.5, 0.0, 1.0)
            c.create_text(
                CANVAS_W // 2,
                y,
                text=text,
                fill=FG,
                font=("TkDefaultFont", 14, "bold"),
            )
            y -= 22
