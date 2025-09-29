"""
Consulting Chaos — main game orchestrator (Python 3.13)

Minimal playable build (v0.1):
- Core app + scene manager + clock
- High score (best total) JSON (optional)
- Minigame 1: Email Blast (typing test)
- Main menu, interlude, results

Controls
- Global: Enter/Space to select/continue, Esc to quit
- Email Blast: Type letters; Backspace deletes; Enter submits when text matches

No external assets, no networking. Works on Windows/macOS/Linux with tkinter.
"""
from __future__ import annotations

import random
import time
from typing import Optional

try:
    import tkinter as tk
except Exception as e:  # pragma: no cover
    raise SystemExit("tkinter is required to run this game.\n" + str(e))

from game_common import (
    CANVAS_W, CANVAS_H, FPS_TARGET,
    Clock, SceneManager, HighScoreManager, Toasts, MinigameResult
)
from scenes import MainMenu


class GameApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Consulting Chaos")
        self.root.resizable(False, False)
        
        # Set window size explicitly
        self.root.geometry(f"{CANVAS_W}x{CANVAS_H}")
        
        self.canvas = tk.Canvas(self.root, width=CANVAS_W, height=CANVAS_H, highlightthickness=0)
        self.canvas.pack()
        
        self.clock = Clock(self.root)
        self.scenes = SceneManager(self)
        self.scores = HighScoreManager()
        self.toasts = Toasts()
        self.rng = random.Random(time.time_ns() & 0xFFFFFFFF)
        self.run_results: list[MinigameResult] = []
        
        # Input
        self.root.bind("<Key>", self.scenes.handle_key)
        self.canvas.focus_set()  # Make sure canvas can receive focus
        
        # Start at menu
        self.scenes.switch(MainMenu())
        
        # Make sure window is visible and on top
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after_idle(lambda: self.root.attributes('-topmost', False))
        
        # Force initial draw after window is set up
        self.root.after_idle(lambda: self.scenes.draw(self.canvas))

    def run(self) -> None:
        def tick(dt: float) -> None:
            self.scenes.update(dt)
            self.scenes.draw(self.canvas)
        self.clock.start(tick)
        self.root.mainloop()

    def reset_run(self) -> None:
        self.run_results = []

    def quit(self) -> None:
        self.clock.stop()
        self.root.destroy()


# ------------------------------
# Main
# ------------------------------
if __name__ == "__main__":
    GameApp().run()
