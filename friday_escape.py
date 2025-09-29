"""
Friday Escape minigame - Partner Pac-Man maze escape for Consulting Chaos.
"""
from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING

from game_common import (
    Scene, MinigameResult, CANVAS_W, CANVAS_H, BG, FG, ACCENT, GOOD, BAD, WARN, MUTED, CARD, GRID,
    ESCAPE_ENEMIES, ESCAPE_TAG_PENALTY, ESCAPE_DECISION_INTERVAL
)

if TYPE_CHECKING:
    from main import GameApp


class FridayEscape(Scene):
    name = "Friday Escape"

    # Tuning
    ESCAPE_ENEMIES = ESCAPE_ENEMIES
    ESCAPE_TAG_PENALTY = ESCAPE_TAG_PENALTY
    ESCAPE_DECISION_INTERVAL = ESCAPE_DECISION_INTERVAL
    
    # Partner/MD quotes when they catch you
    PARTNER_QUOTES = [
        "Hey! Do you have a minute to discuss the Q4 strategy?",
        "Wait! I need to run something by you before you go.",
        "Perfect timing! Let's sync on the client deliverables.",
        "Hold on! The steering committee needs your input.",
        "Quick question about the financial model before you leave.",
        "Can we discuss the implementation roadmap? It's urgent.",
        "I need your perspective on the market analysis.",
        "Wait! The board presentation needs your review.",
        "Do you have time for a quick alignment session?",
        "Perfect! Let's discuss the resource allocation.",
        "I need your expertise on the competitive landscape.",
        "Can we quickly review the risk assessment?",
        "Hold on! The client is asking about the timeline.",
        "Quick sync on the stakeholder management plan?",
        "I need your input on the change management strategy.",
        "Wait! The due diligence needs your sign-off.",
        "Can we discuss the operational efficiency metrics?",
        "Perfect timing! Let's review the cost optimization.",
        "I need your perspective on the digital transformation.",
        "Quick question about the sustainability framework."
    ]

    GRID_W = 15
    GRID_H = 11
    TILE = 36  # pixels

    def __init__(self):
        self.started = False
        self.start_time = 0.0
        self.end_time = 0.0

        self.grid = []  # 0 floor, 1 wall
        self.start = (1, 1)
        self.exit = (self.GRID_W - 2, self.GRID_H - 2)

        self.player = (1, 1)
        self.enemies: list[tuple[int, int]] = []
        self.enemy_timer = 0.0
        self.tags = 0
        self.invuln = 0.0  # seconds after tag

        # drawing origin
        self.x0 = (CANVAS_W - self.GRID_W * self.TILE) // 2
        self.y0 = 90

    # -------- timing helpers --------
    def elapsed(self) -> float:
        end = self.end_time if self.end_time else time.perf_counter()
        return max(0.0, end - self.start_time) if self.started else 0.0

    # -------- fixed Pac-Man style maze --------
    def _gen_maze(self, rng: random.Random) -> None:
        # Fixed Pac-Man style maze with multiple paths
        # 0 = floor, 1 = wall
        self.grid = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # 0
            [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],  # 1
            [1,0,1,1,0,1,0,1,0,1,0,1,1,0,1],  # 2
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 3
            [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],  # 4
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 5
            [1,0,1,0,1,1,1,1,1,1,1,0,1,0,1],  # 6
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],  # 7
            [1,0,1,1,0,1,0,1,0,1,0,1,1,0,1],  # 8
            [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],  # 9
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],  # 10
        ]
        
        self.start = (1, 1)
        self.exit = (13, 9)
        self.player = self.start

        # Place enemies at strategic positions with multiple paths
        self.enemies = [
            (7, 3), (7, 7),  # Center column (2 enemies)
            (3, 5), (11, 5),  # Side positions (2 enemies)
        ]

    # -------- drawing helpers --------
    def _draw_grid(self, c) -> None:
        for y in range(self.GRID_H):
            for x in range(self.GRID_W):
                X = self.x0 + x * self.TILE
                Y = self.y0 + y * self.TILE
                if self.grid[y][x] == 1:
                    c.create_rectangle(X, Y, X + self.TILE, Y + self.TILE, fill=GRID, width=0)
                else:
                    c.create_rectangle(X, Y, X + self.TILE, Y + self.TILE, fill=CARD, width=0)
        # start / exit
        sx, sy = self.start
        ex, ey = self.exit
        c.create_rectangle(self.x0 + sx * self.TILE + 6, self.y0 + sy * self.TILE + 6,
                           self.x0 + (sx + 1) * self.TILE - 6, self.y0 + (sy + 1) * self.TILE - 6,
                           fill=GOOD, width=0)
        c.create_rectangle(self.x0 + ex * self.TILE + 6, self.y0 + ey * self.TILE + 6,
                           self.x0 + (ex + 1) * self.TILE - 6, self.y0 + (ey + 1) * self.TILE - 6,
                           outline=ACCENT, width=3)

    def _draw_entity(self, c, pos: tuple[int, int], color: str) -> None:
        x, y = pos
        X = self.x0 + x * self.TILE + self.TILE // 2
        Y = self.y0 + y * self.TILE + self.TILE // 2
        
        # Use emojis instead of circles
        if color == BAD:  # Partner/MD emojis
            partner_emojis = ["👨‍💼", "👩‍💼", "🧑‍💼"]
            emoji = partner_emojis[hash((x, y)) % len(partner_emojis)]
        else:  # Player emoji (worried face)
            emoji = "😰"
        
        c.create_text(X, Y, text=emoji, font=("TkDefaultFont", 20), fill=color)

    # -------- logic helpers --------
    def _is_wall(self, x: int, y: int) -> bool:
        if not (0 <= x < self.GRID_W and 0 <= y < self.GRID_H):
            return True
        return self.grid[y][x] == 1

    def _neighbors4(self, x: int, y: int):
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not self._is_wall(nx, ny):
                yield nx, ny

    def _enemy_step(self, rng: random.Random, target: tuple[int, int], pos: tuple[int, int]) -> tuple[int, int]:
        # Greedy Manhattan with a bit of randomness
        px, py = pos
        tx, ty = target
        options = list(self._neighbors4(px, py))
        if not options:
            return pos
        # 20% random move to add spice
        if rng.random() < 0.2:
            return rng.choice(options)
        best = min(options, key=lambda p: abs(p[0] - tx) + abs(p[1] - ty))
        return best

    # -------- lifecycle --------
    def on_enter(self, app: "GameApp") -> None:
        self.started = False
        self.start_time = 0.0
        self.end_time = 0.0
        self.tags = 0
        self.invuln = 0.0
        self.enemy_timer = 0.0
        self._gen_maze(app.rng)

    def update(self, app: "GameApp", dt: float) -> None:
        app.toasts.update(dt)
        if not self.started:
            return
        if self.invuln > 0:
            self.invuln = max(0.0, self.invuln - dt)

        # enemies think on a fixed cadence
        self.enemy_timer += dt
        if self.enemy_timer >= self.ESCAPE_DECISION_INTERVAL:
            self.enemy_timer = 0.0
            self.enemies = [self._enemy_step(app.rng, self.player, e) for e in self.enemies]

        # collision check
        if self.invuln <= 0 and any(e == self.player for e in self.enemies):
            self.tags += 1
            self.player = self.start  # respawn
            self.invuln = 1.0
            # Show a random partner quote
            quote = app.rng.choice(self.PARTNER_QUOTES)
            app.toasts.add(f"Partner: \"{quote}\" +{self.ESCAPE_TAG_PENALTY:.1f}s")

        # win?
        if self.player == self.exit:
            # Show escape success message
            app.toasts.add("🎉 You escaped! Enjoy your weekend... but only for now... 😈")
            self.end_time = time.perf_counter()
            pen = self.tags * self.ESCAPE_TAG_PENALTY
            result = MinigameResult(
                name=self.name,
                elapsed=self.elapsed(),
                penalty=pen,
                detail={"tags": self.tags},
            )
            app.run_results.append(result)
            from scenes import Results
            app.scenes.switch(Results(app.run_results))

    def draw(self, app: "GameApp", c) -> None:
        c.delete("all")
        c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=BG, width=0)

        # HUD
        c.create_text(20, 20, text=self.name, fill=ACCENT, font=("TkDefaultFont", 18, "bold"), anchor="nw")
        
        # Instructions summary (top left)
        if self.started:
            c.create_text(
                20,
                50,
                text="Arrows: move • Avoid Partners/MDs • Reach EXIT",
                fill=MUTED,
                font=("TkDefaultFont", 10),
                anchor="nw",
            )
        
        c.create_text(CANVAS_W - 20, 20, text=f"Time: {self.elapsed():.2f}s", fill=FG,
                      font=("TkDefaultFont", 14, "bold"), anchor="ne")
        c.create_text(CANVAS_W - 20, 44, text=f"Tags: {self.tags} (x {self.ESCAPE_TAG_PENALTY:.1f}s)",
                      fill=WARN, font=("TkDefaultFont", 12), anchor="ne")

        self._draw_grid(c)
        # draw enemies
        for e in self.enemies:
            self._draw_entity(c, e, BAD)
        # draw player (blink when invuln)
        if self.invuln <= 0 or int(self.invuln * 10) % 2 == 0:
            self._draw_entity(c, self.player, ACCENT)

        # overlay
        if not self.started:
            # BCG-style professional overlay
            c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill="#1a1a2e", stipple="gray25", width=0)
            
            # Header section
            c.create_rectangle(40, 80, CANVAS_W - 40, 120, fill="#0f3460", width=2, outline="#4a90e2")
            c.create_text(
                CANVAS_W // 2,
                100,
                text="BCG OFFICE POLITICS NAVIGATION ASSESSMENT",
                fill="#4a90e2",
                font=("TkDefaultFont", 16, "bold"),
            )
            
            # Main content box
            c.create_rectangle(60, 140, CANVAS_W - 60, 400, fill="#2c3e50", width=2, outline="#34495e")
            
            lines = [
                "STRATEGIC SITUATION:",
                "It's Friday 4:59 PM. Navigate office politics",
                "and escape before Partners/MDs catch you leaving early!",
                "",
                "STRATEGIC OBJECTIVES:",
                "• Demonstrate strategic navigation skills",
                "• Avoid detection by senior leadership",
                "• Execute flawless escape strategy",
                "",
                "OPERATIONAL INSTRUCTIONS:",
                "Reach the EXIT without getting tagged.",
                "Arrows move. Tagging adds +2.0s and sends you back.",
                "",
                "Press Enter to Begin Assessment"
            ]
            c.create_text(
                CANVAS_W // 2,
                270,
                text="\n".join(lines),
                fill="#ecf0f1",
                font=("TkDefaultFont", 12),
                justify="center",
            )
            
            # Professional call-to-action button
            c.create_rectangle(CANVAS_W // 2 - 150, 420, CANVAS_W // 2 + 150, 460, fill="#e74c3c", width=0)
            c.create_text(
                CANVAS_W // 2,
                440,
                text="BEGIN NAVIGATION ASSESSMENT",
                fill="#ffffff",
                font=("TkDefaultFont", 12, "bold"),
            )

        app.toasts.draw(c)

    def handle_key(self, app: "GameApp", e) -> None:
        if e.keysym == "Escape":
            app.quit()
            return
        if not self.started:
            if e.keysym in ("Return", "space"):
                self.started = True
                self.start_time = time.perf_counter()
            return

        # movement (tile-by-tile)
        dx = (e.keysym == "Right") - (e.keysym == "Left")
        dy = (e.keysym == "Down") - (e.keysym == "Up")
        if (dx, dy) != (0, 0):
            nx, ny = self.player[0] + dx, self.player[1] + dy
            if not self._is_wall(nx, ny):
                self.player = (nx, ny)
