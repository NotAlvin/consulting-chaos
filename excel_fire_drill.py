
"""
Excel Fire Drill minigame - quick math for Consulting Chaos.
"""
from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING

from game_common import Scene, MinigameResult, CANVAS_W, CANVAS_H, BG, FG, ACCENT, GOOD, WARN, MUTED, CARD, MATH_COUNT, MATH_WRONG_PENALTY

if TYPE_CHECKING:
    from main import GameApp


class ExcelFireDrill(Scene):
    name = "Excel Fire Drill"

    def __init__(self):
        self.started = False
        self.start_time = 0.0
        self.end_time = 0.0
        self.prompt = ""
        self.answer: int = 0
        self.input_buf = ""
        self.correct = 0
        self.wrong = 0

    def _new_problem(self, rng: random.Random) -> None:
        kind = rng.choice(["sum", "diff", "prod", "div"]) 
        if kind == "sum":
            a, b = rng.randint(5, 99), rng.randint(5, 99)
            self.prompt = f"{a} + {b} = ?"
            self.answer = a + b
        elif kind == "diff":
            a, b = rng.randint(5, 99), rng.randint(5, 99)
            self.prompt = f"{a} - {b} = ?"
            self.answer = a - b
        elif kind == "prod":
            a, b = rng.randint(3, 12), rng.randint(3, 12)
            self.prompt = f"{a} × {b} = ?"
            self.answer = a * b
        elif kind == "div":
            # Generate division problems as inverted multiplication
            # This ensures the result is always an integer
            a = rng.randint(3, 12)  # divisor
            b = rng.randint(3, 12)  # quotient
            dividend = a * b  # the number to be divided
            self.prompt = f"{dividend} ÷ {a} = ?"
            self.answer = b
        self.input_buf = ""

    def _draw_excel_interface(self, c) -> None:
        """Draw Excel spreadsheet interface"""
        # Excel window frame - use left side for spreadsheet
        excel_x = 20
        excel_y = 100
        excel_w = int(CANVAS_W * 0.8) - 10  # Use 80% of the width (much longer)
        excel_h = 600
        
        # Excel window background
        c.create_rectangle(excel_x, excel_y, excel_x + excel_w, excel_y + excel_h, 
                           fill="#ffffff", width=2, outline="#cccccc")
        
        # Excel header bar
        c.create_rectangle(excel_x, excel_y, excel_x + excel_w, excel_y + 30, 
                           fill="#f2f2f2", width=0)
        c.create_text(excel_x + 10, excel_y + 15, text="Financial Model - Q4 Forecast", 
                      fill="#333333", font=("TkDefaultFont", 12, "bold"), anchor="w")
        
        # Excel grid - 4 columns, 12 rows with wider answer column
        cell_size = 35
        answer_col_width = 60  # Wider answer column
        grid_x = excel_x + 10
        grid_y = excel_y + 40
        grid_w = 3 * cell_size + answer_col_width  # 3 regular columns + wider answer column
        grid_h = 12 * cell_size  # 12 rows
        
        # Draw grid lines with different column widths
        col_positions = [grid_x, grid_x + cell_size, grid_x + 2 * cell_size, grid_x + 3 * cell_size, grid_x + 3 * cell_size + answer_col_width]
        for i, x in enumerate(col_positions):
            c.create_line(x, grid_y, x, grid_y + grid_h, fill="#cccccc", width=1)
        
        for i in range(12):  # 12 rows + 1 border
            y = grid_y + i * cell_size
            c.create_line(grid_x, y, grid_x + grid_w, y, fill="#cccccc", width=1)
        
        # Column headers with proper positioning
        headers = ["Row", "A", "B", "Answer"]
        header_positions = [
            grid_x + cell_size // 2,
            grid_x + cell_size + cell_size // 2,
            grid_x + 2 * cell_size + cell_size // 2,
            grid_x + 3 * cell_size + answer_col_width // 2
        ]
        for i, (header, x) in enumerate(zip(headers, header_positions)):
            y = grid_y + cell_size // 2
            c.create_text(x, y, text=header, fill="#666666", font=("TkDefaultFont", 10, "bold"))
        
        # Fill in the sheet with progress - Row, A, B, and Answer columns
        for row in range(11):
            for col in range(4):
                if row == 0:  # Header row
                    continue
                    
                # Calculate cell positions with different column widths
                if col == 0:  # Row column
                    cell_x = grid_x + cell_size // 2
                elif col == 1:  # A column
                    cell_x = grid_x + cell_size + cell_size // 2
                elif col == 2:  # B column
                    cell_x = grid_x + 2 * cell_size + cell_size // 2
                else:  # Answer column (wider)
                    cell_x = grid_x + 3 * cell_size + answer_col_width // 2
                
                cell_y = grid_y + (row + 1) * cell_size + cell_size // 2
                
                # Calculate rectangle bounds for each column
                if col == 0:  # Row column
                    rect_x1 = grid_x + 2
                    rect_x2 = grid_x + cell_size - 2
                elif col == 1:  # A column
                    rect_x1 = grid_x + cell_size + 2
                    rect_x2 = grid_x + 2 * cell_size - 2
                elif col == 2:  # B column
                    rect_x1 = grid_x + 2 * cell_size + 2
                    rect_x2 = grid_x + 3 * cell_size - 2
                else:  # Answer column (wider)
                    rect_x1 = grid_x + 3 * cell_size + 2
                    rect_x2 = grid_x + 3 * cell_size + answer_col_width - 2
                
                rect_y1 = grid_y + (row + 1) * cell_size + 2
                rect_y2 = grid_y + (row + 2) * cell_size - 2
                
                # Fill cells based on progress
                if row <= self.correct:  # Fill cells for completed questions
                    if col == 0:  # Column 0 - Row number
                        c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                         fill="#f8f9fa", width=1, outline="#dee2e6")
                        c.create_text(cell_x, cell_y, text=str(row), 
                                    fill="#495057", font=("TkDefaultFont", 10, "bold"))
                    elif col == 1:  # Column A - first number
                        # Generate consistent numbers for each row
                        if row == 1:
                            value = "15"
                        elif row == 2:
                            value = "23"
                        elif row == 3:
                            value = "8"
                        elif row == 4:
                            value = "42"
                        elif row == 5:
                            value = "17"
                        elif row == 6:
                            value = "29"
                        elif row == 7:
                            value = "35"
                        else:
                            value = "12"
                        c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                         fill="#e8f5e8", width=1, outline="#4CAF50")
                        c.create_text(cell_x, cell_y, text=value, 
                                    fill="#2E7D32", font=("TkDefaultFont", 10, "bold"))
                    elif col == 2:  # Column B - second number
                        # Generate consistent numbers for each row
                        if row == 1:
                            value = "7"
                        elif row == 2:
                            value = "4"
                        elif row == 3:
                            value = "9"
                        elif row == 4:
                            value = "6"
                        elif row == 5:
                            value = "3"
                        elif row == 6:
                            value = "8"
                        elif row == 7:
                            value = "5"
                        else:
                            value = "11"
                        c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                         fill="#e8f5e8", width=1, outline="#4CAF50")
                        c.create_text(cell_x, cell_y, text=value, 
                                    fill="#2E7D32", font=("TkDefaultFont", 10, "bold"))
                    elif col == 3:  # Column Answer - calculated result
                        # Show the calculated answer for completed questions
                        c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                         fill="#e8f5e8", width=1, outline="#4CAF50")
                        c.create_text(cell_x, cell_y, text="✓", 
                                    fill="#2E7D32", font=("TkDefaultFont", 12, "bold"))
                elif row == self.correct + 1:  # Current question row
                    if col == 0:  # Column 0 - Row number
                        c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                         fill="#e3f2fd", width=2, outline="#2196f3")
                        c.create_text(cell_x, cell_y, text=str(row), 
                                    fill="#1976d2", font=("TkDefaultFont", 10, "bold"))
                    elif col == 1:  # Column A - show first number of current question
                        # Extract first number from prompt
                        if " + " in self.prompt:
                            value = self.prompt.split(" + ")[0]
                        elif " - " in self.prompt:
                            value = self.prompt.split(" - ")[0]
                        elif " × " in self.prompt:
                            value = self.prompt.split(" × ")[0]
                        elif " ÷ " in self.prompt:
                            value = self.prompt.split(" ÷ ")[0]
                        elif "% of " in self.prompt:
                            value = self.prompt.split("% of ")[0] + "%"
                        else:
                            value = "?"
                        c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                         fill="#e3f2fd", width=2, outline="#2196f3")
                        c.create_text(cell_x, cell_y, text=value, 
                                    fill="#1976d2", font=("TkDefaultFont", 10, "bold"))
                    elif col == 2:  # Column B - show second number of current question
                        # Extract second number from prompt
                        if " + " in self.prompt:
                            value = self.prompt.split(" + ")[1].split(" =")[0]
                        elif " - " in self.prompt:
                            value = self.prompt.split(" - ")[1].split(" =")[0]
                        elif " × " in self.prompt:
                            value = self.prompt.split(" × ")[1].split(" =")[0]
                        elif " ÷ " in self.prompt:
                            value = self.prompt.split(" ÷ ")[1].split(" =")[0]
                        elif "% of " in self.prompt:
                            value = self.prompt.split("% of ")[1].split(" =")[0]
                        else:
                            value = "?"
                        c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                         fill="#e3f2fd", width=2, outline="#2196f3")
                        c.create_text(cell_x, cell_y, text=value, 
                                    fill="#1976d2", font=("TkDefaultFont", 10, "bold"))
                    elif col == 3:  # Column Answer - show input or placeholder
                        if self.input_buf:
                            c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                             fill="#fff3cd", width=2, outline="#ffc107")
                            c.create_text(cell_x, cell_y, text=self.input_buf, 
                                        fill="#856404", font=("TkDefaultFont", 10, "bold"))
                        else:
                            c.create_rectangle(rect_x1, rect_y1, rect_x2, rect_y2,
                                             fill="#e3f2fd", width=2, outline="#2196f3")
                            c.create_text(cell_x, cell_y, text="?", 
                                        fill="#1976d2", font=("TkDefaultFont", 10, "bold"))
                else:
                    # Empty cells for future questions
                    if col == 0:  # Row numbers for future questions
                        c.create_text(cell_x, cell_y, text=str(row), 
                                    fill="#999999", font=("TkDefaultFont", 10))
                    else:
                        c.create_text(cell_x, cell_y, text="", fill="#999999", font=("TkDefaultFont", 10))
        
        # Right side - Question and input area (moved down to middle and further left)
        right_x = CANVAS_W // 2 - 60  # Moved further left
        right_y = excel_y + 150  # Moved down to middle
        
        # Main question box (larger to contain all sub-boxes)
        c.create_rectangle(right_x, right_y, CANVAS_W - 20, right_y + 300, 
                           fill="#f8f9fa", width=2, outline="#dee2e6")
        c.create_text(right_x + 10, right_y + 20, text="Current Calculation:", 
                      fill="#495057", font=("TkDefaultFont", 12, "bold"), anchor="w")
        c.create_text(right_x + 10, right_y + 50, text=self.prompt, 
                      fill="#212529", font=("TkDefaultFont", 16, "bold"), anchor="w")
        
        # Input area (fully contained within main box)
        input_y = right_y + 100
        c.create_rectangle(right_x + 20, input_y, CANVAS_W - 40, input_y + 60, 
                           fill="#ffffff", width=2, outline="#4CAF50")
        c.create_text(right_x + 30, input_y + 20, text="Your Answer:", 
                      fill="#4CAF50", font=("TkDefaultFont", 11, "bold"), anchor="w")
        c.create_text(right_x + 30, input_y + 40, text=self.input_buf or "Enter value", 
                      fill="#333333" if self.input_buf else "#999999", 
                      font=("TkDefaultFont", 14), anchor="w")
        
        # Progress indicator (fully contained within main box)
        progress_y = right_y + 180
        c.create_rectangle(right_x + 20, progress_y, CANVAS_W - 40, progress_y + 50, 
                           fill="#e9ecef", width=1, outline="#ced4da")
        c.create_text(right_x + 30, progress_y + 15, text=f"Progress: {self.correct}/{MATH_COUNT} calculations completed", 
                      fill="#495057", font=("TkDefaultFont", 11, "bold"), anchor="w")
        
        # Progress bar (fully contained within main box)
        progress_width = (CANVAS_W - 80 - right_x) * (self.correct / MATH_COUNT)
        c.create_rectangle(right_x + 30, progress_y + 30, right_x + 30 + progress_width, progress_y + 40, 
                           fill="#4CAF50", width=0)

    def elapsed(self) -> float:
        end = self.end_time if self.end_time else time.perf_counter()
        return max(0.0, end - self.start_time) if self.started else 0.0

    def on_enter(self, app: "GameApp") -> None:
        self.started = False
        self.correct = 0
        self.wrong = 0
        self.start_time = 0.0
        self.end_time = 0.0
        self._new_problem(app.rng)

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
                text="Type digits • Enter submits • Backspace edits",
                fill=MUTED,
                font=("TkDefaultFont", 10),
                anchor="nw",
            )
        
        c.create_text(CANVAS_W - 20, 20, text=f"Time: {self.elapsed():.2f}s", fill=FG, font=("TkDefaultFont", 14, "bold"), anchor="ne")
        c.create_text(CANVAS_W - 20, 44, text=f"Correct: {self.correct}/{MATH_COUNT}", fill=GOOD, font=("TkDefaultFont", 12), anchor="ne")
        c.create_text(CANVAS_W - 20, 64, text=f"Wrong pen: {self.wrong} x {MATH_WRONG_PENALTY:.1f}s", fill=WARN, font=("TkDefaultFont", 12), anchor="ne")
        
        # Excel spreadsheet interface
        self._draw_excel_interface(c)
        # Start/help overlay
        if not self.started:
            # BCG-style professional overlay
            c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill="#1a1a2e", stipple="gray25", width=0)
            
            # Header section
            c.create_rectangle(40, 80, CANVAS_W - 40, 120, fill="#0f3460", width=2, outline="#4a90e2")
            c.create_text(
                CANVAS_W // 2,
                100,
                text="BCG FINANCIAL MODELING CRISIS ASSESSMENT",
                fill="#4a90e2",
                font=("TkDefaultFont", 16, "bold"),
            )
            
            # Main content box
            c.create_rectangle(60, 140, CANVAS_W - 60, 400, fill="#2c3e50", width=2, outline="#34495e")
            
            lines = [
                "CRITICAL BUSINESS SCENARIO:",
                "Your financial models have crashed 2 hours before",
                "the client presentation. Manual calculations only!",
                "",
                "STRATEGIC OBJECTIVES:",
                "• Execute rapid-fire mathematical calculations",
                "• Maintain precision under extreme time pressure",
                "• Demonstrate analytical excellence without tools",
                "",
                "OPERATIONAL INSTRUCTIONS:",
                "Solve each problem quickly and accurately.",
                "Type digits (and -). Enter submits. Backspace edits.",
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
                text="BEGIN FINANCIAL ASSESSMENT",
                fill="#ffffff",
                font=("TkDefaultFont", 12, "bold"),
            )
        app.toasts.draw(c)

    def _submit(self, app: "GameApp") -> None:
        try:
            val = int(self.input_buf)
        except ValueError:
            app.toasts.add("Not a number")
            return
        if val == self.answer:
            self.correct += 1
            if self.correct >= MATH_COUNT:
                # finish
                self.end_time = time.perf_counter()
                pen = self.wrong * MATH_WRONG_PENALTY
                result = MinigameResult(
                    name=self.name,
                    elapsed=self.elapsed(),
                    penalty=pen,
                    detail={"wrong": self.wrong, "count": MATH_COUNT},
                )
                app.run_results.append(result)
                from puzzle_game import PuzzleGame
                from scenes import Interlude
                app.scenes.switch(Interlude(next_scene=PuzzleGame(), last_result=result))
                return
            else:
                app.toasts.add("Correct!")
                self._new_problem(app.rng)
        else:
            self.wrong += 1
            app.toasts.add(f"#REF! +{MATH_WRONG_PENALTY:.1f}s")
            # keep same problem
            self.input_buf = ""

    def handle_key(self, app: "GameApp", e) -> None:
        if e.keysym == "Escape":
            app.quit()
            return
        if not self.started:
            if e.keysym in ("Return", "space"):
                self.started = True
                self.start_time = time.perf_counter()
            return
        if e.keysym == "BackSpace":
            self.input_buf = self.input_buf[:-1]
            return
        if e.keysym == "Return":
            self._submit(app)
            return
        ch = e.char
        if ch and (ch.isdigit() or (ch == "-" and not self.input_buf)):
            self.input_buf += ch
