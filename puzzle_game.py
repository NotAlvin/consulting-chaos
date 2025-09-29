"""
Puzzle minigame - Tetris-like puzzle solving for Consulting Chaos.
"""
from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING

from game_common import (
    Scene, MinigameResult, CANVAS_W, CANVAS_H, BG, FG, ACCENT, GOOD, BAD, WARN, MUTED, CARD, GRID,
    CAL_TARGET_SECONDS, CAL_OVER_PENALTY_PER_10S, CAL_LEFTOVER_PENALTY, clamp
)

if TYPE_CHECKING:
    from main import GameApp


class PuzzleGame(Scene):
    name = "Calendar Scheduler Puzzle"
    
    GRID_W, GRID_H = 8, 8
    CELL_SIZE = 30
    GRID_X = (CANVAS_W - GRID_W * CELL_SIZE) // 2
    GRID_Y = 100

    def __init__(self):
        self.started = False
        self.start_time = 0.0
        self.end_time = 0.0
        self.grid = [[0 for _ in range(self.GRID_W)] for _ in range(self.GRID_H)]
        self.remaining = []
        self.cur_idx = 0
        self.cur_cells = []
        self.pos = [0, 0]
        
        # Define meeting blocks (calendar-style pieces)
        self.pieces = [
            {"cells": [(0, 0), (1, 0), (0, 1), (1, 1)], "name": "Team Standup", "color": "#4A90E2"},  # 2x2 square
            {"cells": [(0, 0), (1, 0), (2, 0), (3, 0)], "name": "All Hands", "color": "#7ED321"},      # 4x1 line
            {"cells": [(0, 0), (1, 0), (2, 0), (1, 1)], "name": "Client Call", "color": "#F5A623"},     # T-shape
            {"cells": [(0, 0), (1, 0), (1, 1), (2, 1)], "name": "Workshop", "color": "#BD10E0"},        # Z-shape
            {"cells": [(0, 0), (1, 0), (2, 0), (0, 1)], "name": "Review", "color": "#B8E986"},          # L-shape
            {"cells": [(0, 0), (1, 0), (2, 0), (2, 1)], "name": "Planning", "color": "#50E3C2"},        # Reverse L
            {"cells": [(0, 0), (1, 0), (1, 1)], "name": "1:1", "color": "#D0021B"},                     # Small L
            {"cells": [(0, 0), (1, 0), (0, 1)], "name": "Sync", "color": "#9013FE"},                    # Small reverse L
        ]

    def elapsed(self) -> float:
        end = self.end_time if self.end_time else time.perf_counter()
        return max(0.0, end - self.start_time) if self.started else 0.0

    def _rot_ccw(self, cells):
        """Rotate cells 90 degrees counter-clockwise"""
        return [(-y, x) for x, y in cells]

    def _rot_cw(self, cells):
        """Rotate cells 90 degrees clockwise"""
        return [(y, -x) for x, y in cells]

    def _can_place(self, x, y, cells):
        """Check if cells can be placed at position (x, y)"""
        for dx, dy in cells:
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= self.GRID_W or ny < 0 or ny >= self.GRID_H:
                return False
            if self.grid[ny][nx] != 0:
                return False
        return True

    def _place(self):
        """Place current piece at current position"""
        current_piece = self.remaining[self.cur_idx]
        for dx, dy in self.cur_cells:
            x, y = self.pos[0] + dx, self.pos[1] + dy
            self.grid[y][x] = current_piece  # Store the piece object instead of just 1

    def _advance_piece(self):
        """Move to next piece"""
        self.cur_idx += 1
        if self.cur_idx < len(self.remaining):
            self.cur_cells = self.remaining[self.cur_idx]["cells"]
            self.pos = [0, 0]
        else:
            self.cur_cells = []

    def _is_grid_filled(self):
        """Check if the entire grid is filled (all cells have pieces)"""
        for row in self.grid:
            for cell in row:
                if cell == 0:
                    return False
        return True


    def _finish(self, app: "GameApp", forced: bool = False) -> None:
        self.end_time = time.perf_counter()
        over = max(0.0, self.elapsed() - CAL_TARGET_SECONDS)
        over_pen = math.floor(over / 10.0) * CAL_OVER_PENALTY_PER_10S
        
        # Count unused pieces
        unused_pieces = len(self.remaining) - self.cur_idx
        unused_penalty = unused_pieces * 10.0  # 10s per unused piece
        pen = over_pen + unused_penalty
        
        result = MinigameResult(
            name=self.name,
            elapsed=self.elapsed(),
            penalty=pen,
            detail={"over_seconds": over, "unused_pieces": unused_pieces, "unused_penalty": unused_penalty},
        )
        app.run_results.append(result)
        from friday_escape import FridayEscape
        from scenes import Interlude
        app.scenes.switch(Interlude(next_scene=FridayEscape(), last_result=result))

    def on_enter(self, app: "GameApp") -> None:
        self.started = False
        self.start_time = 0.0
        self.end_time = 0.0
        self.grid = [[0 for _ in range(self.GRID_W)] for _ in range(self.GRID_H)]
        # Create a random set of pieces (with replacement, so pieces can be reused)
        import random
        self.remaining = [random.choice(self.pieces) for _ in range(15)]
        self.cur_idx = 0
        self.cur_cells = self.remaining[0]["cells"] if self.remaining else []
        self.pos = [0, 0]

    def update(self, app: "GameApp", dt: float) -> None:
        app.toasts.update(dt)

    def draw(self, app: "GameApp", c) -> None:
        c.delete("all")
        c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=BG, width=0)
        
        # Header
        c.create_text(20, 20, text=self.name, fill=ACCENT, font=("TkDefaultFont", 18, "bold"), anchor="nw")
        
        # Instructions summary (top left)
        if self.started:
            c.create_text(
                20,
                50,
                text="Arrows: move • Z/X: rotate • Space: place • Return: finish",
                fill=MUTED,
                font=("TkDefaultFont", 10),
                anchor="nw",
            )
        
        c.create_text(CANVAS_W - 20, 20, text=f"Time: {self.elapsed():.2f}s", fill=FG, font=("TkDefaultFont", 14, "bold"), anchor="ne")
        c.create_text(CANVAS_W - 20, 44, text=f"Target: {CAL_TARGET_SECONDS:.0f}s", fill=MUTED, font=("TkDefaultFont", 12), anchor="ne")
        c.create_text(CANVAS_W - 20, 64, text=f"Pieces: {self.cur_idx}/{len(self.remaining)}", fill=GOOD, font=("TkDefaultFont", 12), anchor="ne")
        
        # Show penalty info
        unused_pieces = len(self.remaining) - self.cur_idx
        if unused_pieces > 0:
            penalty_text = f"Unused: {unused_pieces} (10s each)"
            c.create_text(CANVAS_W - 20, 84, text=penalty_text, fill=WARN, font=("TkDefaultFont", 12), anchor="ne")
        
        # Draw calendar grid
        for y in range(self.GRID_H):
            for x in range(self.GRID_W):
                gx = self.GRID_X + x * self.CELL_SIZE
                gy = self.GRID_Y + y * self.CELL_SIZE
                if self.grid[y][x] != 0:
                    # Draw placed meeting block with its original piece color
                    placed_piece = self.grid[y][x]
                    meeting_color = placed_piece.get("color", ACCENT)
                    
                    # Draw meeting block
                    c.create_rectangle(gx + 1, gy + 1, gx + self.CELL_SIZE - 1, gy + self.CELL_SIZE - 1, 
                                     fill=meeting_color, width=0)
                    c.create_rectangle(gx, gy, gx + self.CELL_SIZE, gy + self.CELL_SIZE, 
                                     fill="", width=1, outline=GRID)
                else:
                    # Draw empty calendar slot
                    c.create_rectangle(gx, gy, gx + self.CELL_SIZE, gy + self.CELL_SIZE, 
                                     fill=CARD, width=1, outline=GRID)
        
        # Draw current piece with meeting styling
        if self.cur_cells and self.cur_idx < len(self.remaining):
            current_piece = self.remaining[self.cur_idx]
            piece_color = current_piece.get("color", ACCENT)
            piece_name = current_piece.get("name", "Meeting")
            
            # Draw meeting blocks
            for dx, dy in self.cur_cells:
                px = self.pos[0] + dx
                py = self.pos[1] + dy
                if 0 <= px < self.GRID_W and 0 <= py < self.GRID_H:
                    gx = self.GRID_X + px * self.CELL_SIZE
                    gy = self.GRID_Y + py * self.CELL_SIZE
                    # Draw meeting block with rounded corners effect
                    c.create_rectangle(gx + 2, gy + 2, gx + self.CELL_SIZE - 2, gy + self.CELL_SIZE - 2, 
                                     fill=piece_color, width=0)
                    c.create_rectangle(gx, gy, gx + self.CELL_SIZE, gy + self.CELL_SIZE, 
                                     fill="", width=2, outline=piece_color)
            
            # Show current meeting name
            c.create_text(
                CANVAS_W // 2, 
                self.GRID_Y - 20, 
                text=f"Current: {piece_name}", 
                fill=piece_color, 
                font=("TkDefaultFont", 12, "bold")
            )
        
        # Instructions
        if not self.started:
            # BCG-style professional overlay
            c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill="#1a1a2e", stipple="gray25", width=0)
            
            # Header section
            c.create_rectangle(40, 80, CANVAS_W - 40, 120, fill="#0f3460", width=2, outline="#4a90e2")
            c.create_text(
                CANVAS_W // 2,
                100,
                text="BCG STRATEGIC CALENDAR OPTIMIZATION ASSESSMENT",
                fill="#4a90e2",
                font=("TkDefaultFont", 16, "bold"),
            )
            
            # Main content box
            c.create_rectangle(60, 140, CANVAS_W - 60, 400, fill="#2c3e50", width=2, outline="#34495e")
            
            lines = [
                "STRATEGIC PLANNING SCENARIO:",
                "Optimize your executive calendar by scheduling",
                "18 critical meetings without conflicts.",
                "",
                "STRATEGIC OBJECTIVES:",
                "• Maximize meeting utilization efficiency",
                "• Demonstrate strategic time management",
                "• Optimize executive calendar allocation",
                "",
                "OPERATIONAL INSTRUCTIONS:",
                "Arrow keys: navigate, Z/X: rotate, Space: place",
                "Return: finish early (10s penalty per unscheduled meeting)",
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
                text="BEGIN CALENDAR ASSESSMENT",
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
        
        # Active controls
        if e.keysym in ("Left", "Right", "Up", "Down"):
            dx = (e.keysym == "Right") - (e.keysym == "Left")
            dy = (e.keysym == "Down") - (e.keysym == "Up")
            nx, ny = self.pos[0] + dx, self.pos[1] + dy
            # Allow moving even if invalid; placement will check
            self.pos = [clamp(nx, 0, self.GRID_W - 1), clamp(ny, 0, self.GRID_H - 1)]
            return
        
        if e.keysym.lower() == "z":
            self.cur_cells = self._rot_ccw(self.cur_cells)
            return
        
        if e.keysym.lower() == "x":
            self.cur_cells = self._rot_cw(self.cur_cells)
            return
        
        # Removed skip functionality - must place all pieces
        
        if e.keysym == "space":
            if self._can_place(self.pos[0], self.pos[1], self.cur_cells):
                self._place()
                self._advance_piece()
                # Check if all pieces have been used
                if self.cur_idx >= len(self.remaining):
                    self._finish(app)
            else:
                app.toasts.add("Doesn't fit here")
            return
        
        if e.keysym == "Return":
            # Finish early with penalty for unused pieces
            self._finish(app, forced=True)
            return
