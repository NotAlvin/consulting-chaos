"""
Menu, interlude, and results scenes for Consulting Chaos game.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from game_common import Scene, MinigameResult, CANVAS_W, CANVAS_H, BG, FG, ACCENT, GOOD, MUTED, CARD, GRID, WARN, BAD

if TYPE_CHECKING:
    from main import GameApp


class MainMenu(Scene):
    name = "Main Menu"

    def __init__(self):
        self.blink = 0.0

    def on_enter(self, app: "GameApp") -> None:
        self.blink = 0.0

    def update(self, app: "GameApp", dt: float) -> None:
        self.blink += dt

    def draw(self, app: "GameApp", c) -> None:
        c.delete("all")
        
        # BCG green theme background
        c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=BG, width=0)
        c.create_rectangle(0, 0, CANVAS_W, 80, fill=GRID, width=0)
        
        # BCG-style header with green theme
        c.create_rectangle(20, 20, CANVAS_W - 20, 60, fill=GOOD, width=2, outline=ACCENT)
        c.create_text(
            CANVAS_W // 2,
            40,
            text="BOSTON CONSULTING GROUP",
            fill=ACCENT,
            font=("TkDefaultFont", 14, "bold"),
        )
        
        # Main title with green styling
        c.create_text(
            CANVAS_W // 2,
            120,
            text="CONSULTING CHAOS",
            fill=GOOD,
            font=("TkDefaultFont", 36, "bold"),
        )
        
        # Subtitle with professional styling
        c.create_text(
            CANVAS_W // 2,
            150,
            text="Strategic Excellence Under Pressure",
            fill=MUTED,
            font=("TkDefaultFont", 16, "italic"),
        )
        
        # Professional description box with proper sizing
        c.create_rectangle(40, 180, CANVAS_W - 40, 360, fill=CARD, width=2, outline=ACCENT)
        lines = [
            "You are a BCG consultant racing against client deadlines.",
            "Complete the four strategic assessments as fast as you can to demonstrate your excellence.",
            "",
            "• Email Blast: Client communication under pressure",
            "• Excel Fire Drill: Financial modeling crisis",
            "• Calendar Tetris: Meeting optimization strategy", 
            "• Friday Escape: Office politics navigation",
            "",
            "Controls: Arrows, letters; Enter/Space = Continue; Esc = Quit at any time",
        ]
        c.create_text(
            CANVAS_W // 2,
            270,
            text="\n".join(lines),
            fill=FG,
            font=("TkDefaultFont", 11),
            justify="center",
            width=CANVAS_W - 100,
        )
        
        # Professional call-to-action with green theme
        hint = "Press Enter to Begin Strategic Assessment"
        if int(self.blink * 2) % 2 == 0:
            c.create_rectangle(CANVAS_W // 2 - 200, 390, CANVAS_W // 2 + 200, 430, fill=ACCENT, width=0)
            c.create_text(
                CANVAS_W // 2,
                410,
                text=hint,
                fill="#ffffff",
                font=("TkDefaultFont", 14, "bold"),
            )

        # Professional performance metrics with green theme
        if app.scores.best_total_seconds is not None:
            c.create_rectangle(40, 460, CANVAS_W - 40, 510, fill=GOOD, width=2, outline=ACCENT)
            c.create_text(
                CANVAS_W // 2,
                480,
                text="PERSONAL BEST PERFORMANCE",
                fill="#ffffff",
                font=("TkDefaultFont", 12, "bold"),
            )
            c.create_text(
                CANVAS_W // 2,
                500,
                text=f"Total Time: {app.scores.best_total_seconds:.2f}s",
                fill=ACCENT,
                font=("TkDefaultFont", 14, "bold"),
            )

    def handle_key(self, app: "GameApp", e) -> None:
        if e.keysym in ("Escape",):
            app.quit()
        if e.keysym in ("Return", "space"):
            app.toasts.add("Let's go!")
            app.reset_run()
            from email_blast import EmailBlast
            app.scenes.switch(Interlude(next_scene=EmailBlast()))


class Interlude(Scene):
    name = "Interlude"

    def __init__(self, next_scene: Scene, last_result: Optional[MinigameResult] = None):
        self.next_scene = next_scene
        self.last_result = last_result
        self.timer = 0.0

    def update(self, app: "GameApp", dt: float) -> None:
        self.timer += dt

    def draw(self, app: "GameApp", c) -> None:
        c.delete("all")
        c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=BG, width=0)
        y = 150
        c.create_text(
            CANVAS_W // 2,
            y,
            text="Interlude",
            fill=ACCENT,
            font=("TkDefaultFont", 28, "bold"),
        )
        y += 40
        if self.last_result is not None:
            c.create_text(
                CANVAS_W // 2,
                y,
                text=(
                    f"{self.last_result.name}: "
                    f"time {self.last_result.elapsed:.2f}s + penalty {self.last_result.penalty:.2f}s "
                    f"= {self.last_result.total:.2f}s"
                ),
                fill=FG,
                font=("TkDefaultFont", 14),
            )
            y += 30
        c.create_text(
            CANVAS_W // 2,
            y + 10,
            text="Press Enter to continue",
            fill=MUTED,
            font=("TkDefaultFont", 16, "bold"),
        )

    def handle_key(self, app: "GameApp", e) -> None:
        if e.keysym in ("Return", "space"):
            app.scenes.switch(self.next_scene)
        if e.keysym == "Escape":
            app.quit()


class Results(Scene):
    name = "Results"

    def __init__(self, results: list[MinigameResult]):
        self.results = results
        self.total = sum(r.total for r in results)
        self.individual_times = {r.name: r.total for r in results}
        self.is_best = False
        self.showing_input = False
        self.player_name = ""
        self.player_title = ""
        self.input_mode = "name"  # "name" or "title"
        self.leaderboard_position = None

    def on_enter(self, app: "GameApp") -> None:
        self.is_best = app.scores.maybe_update(self.total, self.individual_times)
        if self.is_best:
            self.showing_input = True

    def draw(self, app: "GameApp", c) -> None:
        c.delete("all")
        c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=BG, width=0)
        
        if self.showing_input:
            self._draw_input_screen(c)
        else:
            self._draw_results_screen(c)

    def _draw_input_screen(self, c) -> None:
        c.create_text(
            CANVAS_W // 2,
            100,
            text="NEW PERSONAL BEST!",
            fill=GOOD,
            font=("TkDefaultFont", 24, "bold"),
        )
        c.create_text(
            CANVAS_W // 2,
            150,
            text=f"Total Time: {self.total:.2f}s",
            fill=FG,
            font=("TkDefaultFont", 18, "bold"),
        )
        
        # Show individual times
        y = 200
        c.create_text(
            CANVAS_W // 2,
            y,
            text="Individual Times:",
            fill=ACCENT,
            font=("TkDefaultFont", 14, "bold"),
        )
        y += 30
        for r in self.results:
            c.create_text(
                CANVAS_W // 2,
                y,
                text=f"{r.name}: {r.total:.2f}s",
                fill=FG,
                font=("TkDefaultFont", 12),
            )
            y += 25
        
        # Input fields
        y += 20
        if self.input_mode == "name":
            c.create_text(
                CANVAS_W // 2,
                y,
                text="Enter your name:",
                fill=ACCENT,
                font=("TkDefaultFont", 16, "bold"),
            )
            c.create_text(
                CANVAS_W // 2,
                y + 30,
                text=self.player_name + "_",
                fill=FG,
                font=("TkDefaultFont", 14),
            )
        else:
            c.create_text(
                CANVAS_W // 2,
                y,
                text="Enter your title:",
                fill=ACCENT,
                font=("TkDefaultFont", 16, "bold"),
            )
            c.create_text(
                CANVAS_W // 2,
                y + 30,
                text=self.player_title + "_",
                fill=FG,
                font=("TkDefaultFont", 14),
            )
        
        c.create_text(
            CANVAS_W // 2,
            CANVAS_H - 60,
            text="[Enter] Continue    [Backspace] Edit",
            fill=MUTED,
            font=("TkDefaultFont", 12),
        )

    def _get_performance_rank(self) -> tuple[str, str, str]:
        """Get performance rank based on total time"""
        if self.total < 90:
            return "Fantastic Skills", ACCENT, "You're basically a consulting superhero! 🦸‍♂️"
        elif self.total < 120:
            return "Good", GOOD, "Solid performance - you'd survive a real client crisis! 💪"
        elif self.total < 150:
            return "Average", WARN, "Not bad, but maybe skip the coffee breaks next time ☕"
        elif self.total < 180:
            return "Room for Improvement", "#FF5722", "Time to hit the consulting gym! 🏋️‍♂️"
        else:
            return "Back to Training", BAD, "Even interns are faster than this... 😅"

    def _draw_results_screen(self, c) -> None:
        c.create_text(
            CANVAS_W // 2,
            90,
            text="RESULTS",
            fill=ACCENT,
            font=("TkDefaultFont", 30, "bold"),
        )
        y = 150
        for r in self.results:
            c.create_text(
                CANVAS_W // 2,
                y,
                text=f"{r.name:16s}  {r.elapsed:.2f}s + {r.penalty:.2f}s  =  {r.total:.2f}s",
                fill=FG,
                font=("TkDefaultFont", 14),
            )
            y += 28
        y += 10
        c.create_text(
            CANVAS_W // 2,
            y,
            text=f"TOTAL: {self.total:.2f}s",
            fill=GOOD if self.is_best else FG,
            font=("TkDefaultFont", 18, "bold"),
        )
        y += 40
        
        # Performance evaluation
        rank_text, rank_color, funny_description = self._get_performance_rank()
        c.create_text(
            CANVAS_W // 2,
            y,
            text="PERFORMANCE EVALUATION",
            fill=ACCENT,
            font=("TkDefaultFont", 16, "bold"),
        )
        y += 30
        c.create_text(
            CANVAS_W // 2,
            y,
            text=rank_text,
            fill=rank_color,
            font=("TkDefaultFont", 20, "bold"),
        )
        y += 30
        c.create_text(
            CANVAS_W // 2,
            y,
            text=funny_description,
            fill=MUTED,
            font=("TkDefaultFont", 14),
        )
        y += 40
        
        if self.leaderboard_position is not None:
            c.create_text(
                CANVAS_W // 2,
                y,
                text=f"Leaderboard Position: #{self.leaderboard_position + 1}",
                fill=GOOD,
                font=("TkDefaultFont", 16, "bold"),
            )
            y += 30
        
        c.create_text(
            CANVAS_W // 2,
            CANVAS_H - 60,
            text="[Enter] Play Again    [Esc] Quit",
            fill=MUTED,
            font=("TkDefaultFont", 14, "bold"),
        )

    def handle_key(self, app: "GameApp", e) -> None:
        if self.showing_input:
            if e.keysym == "BackSpace":
                if self.input_mode == "name":
                    self.player_name = self.player_name[:-1]
                else:
                    self.player_title = self.player_title[:-1]
            elif e.keysym == "Return":
                if self.input_mode == "name":
                    if self.player_name.strip():
                        self.input_mode = "title"
                else:
                    if self.player_title.strip():
                        # Add to leaderboard
                        self.leaderboard_position = app.scores.add_to_leaderboard(
                            self.player_name.strip(),
                            self.player_title.strip(),
                            self.total,
                            self.individual_times
                        )
                        self.showing_input = False
            elif e.char and e.char.isprintable():
                if self.input_mode == "name":
                    self.player_name += e.char
                else:
                    self.player_title += e.char
        else:
            if e.keysym in ("Return", "space"):
                app.reset_run()
                app.scenes.switch(MainMenu())
            elif e.keysym == "Escape":
                app.quit()
