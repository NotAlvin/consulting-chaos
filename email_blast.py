"""
Email Blast minigame - typing test for Consulting Chaos.
"""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

from game_common import Scene, MinigameResult, CANVAS_W, CANVAS_H, BG, FG, ACCENT, GOOD, BAD, WARN, MUTED, CARD, EMAIL_PENALTY_PER_MISS, JARGON

if TYPE_CHECKING:
    from main import GameApp


class EmailBlast(Scene):
    name = "Email Blast"

    def __init__(self):
        self.started = False
        self.start_time = 0.0
        self.end_time = 0.0
        self.target = ""
        self.typed = ""
        self.misses = 0

    # --- helpers ---
    def elapsed(self) -> float:
        end = self.end_time if self.end_time else time.perf_counter()
        return max(0.0, end - self.start_time) if self.started else 0.0

    def _generate_consulting_text(self, target_length: int, rng) -> str:
        """Generate consulting jargon text with approximately target_length characters"""
        # Consulting phrases of various lengths
        phrases = [
            "Let's circle back post-standup and align on next steps.",
            "Driving synergy for cross-functional KPIs and stakeholder buy-in.",
            "Deck alignment before EOD, thanks for the quick turnaround.",
            "Can we socialize the roadmap ASAP and get feedback?",
            "Low-hanging fruit for Q4 quick wins and revenue impact.",
            "Double-click the assumptions and de-risk the approach.",
            "Let's park this and revisit offline with the team.",
            "Push the deck to green for tomorrow's steerco meeting.",
            "Need to deep-dive the data and validate assumptions.",
            "Schedule a sync to discuss the strategic implications.",
            "Moving forward with the recommended approach and timeline.",
            "Stakeholder alignment is critical for project success.",
            "Let's prioritize the high-impact initiatives first.",
            "Need to socialize this with leadership before proceeding.",
            "Quick wins will help build momentum for larger changes.",
        ]
        
        # Sample 10 phrases without replacement
        selected_phrases = rng.sample(phrases, min(3, len(phrases)))
        
        # Build the string from the selected phrases
        text = " ".join(selected_phrases)
        
        # If we need to add more phrases to reach target length
        if len(text) < target_length - 20:  # If significantly under target
            # Add more phrases if we have room
            remaining_phrases = [p for p in phrases if p not in selected_phrases]
            while len(text) < target_length - 10 and remaining_phrases:
                next_phrase = rng.choice(remaining_phrases)
                text += " " + next_phrase
                remaining_phrases.remove(next_phrase)
        return text

    def finish(self, app: "GameApp") -> None:
        if not self.started:
            return
        self.end_time = time.perf_counter()
        pen = self.misses * EMAIL_PENALTY_PER_MISS
        result = MinigameResult(
            name=self.name,
            elapsed=self.elapsed(),
            penalty=pen,
            detail={"misses": self.misses, "target": self.target},
        )
        app.run_results.append(result)
        # NEXT: interlude → Excel Fire Drill
        from excel_fire_drill import ExcelFireDrill
        from scenes import Interlude
        app.scenes.switch(Interlude(next_scene=ExcelFireDrill(), last_result=result))

    # --- lifecycle ---
    def on_enter(self, app: "GameApp") -> None:
        rng = app.rng
        # Generate text with consistent length (150 ± 5 characters)
        target_length = rng.randint(145, 155)
        self.target = self._generate_consulting_text(target_length, rng)
        self.typed = ""
        self.misses = 0
        self.started = False
        self.start_time = 0.0
        self.end_time = 0.0

    def update(self, app: "GameApp", dt: float) -> None:
        app.toasts.update(dt)

    def draw(self, app: "GameApp", c) -> None:
        c.delete("all")
        c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill=BG, width=0)

        # Header
        c.create_text(
            20,
            20,
            text=f"{self.name}",
            fill=ACCENT,
            font=("TkDefaultFont", 18, "bold"),
            anchor="nw",
        )
        
        # Instructions summary (top left)
        if self.started:
            c.create_text(
                20,
                50,
                text="Type text • Backspace fixes • Enter submits",
                fill=MUTED,
                font=("TkDefaultFont", 10),
                anchor="nw",
            )
        # Timer HUD
        c.create_text(
            CANVAS_W - 20,
            20,
            text=f"Time: {self.elapsed():.2f}s",
            fill=FG,
            font=("TkDefaultFont", 14, "bold"),
            anchor="ne",
        )
        c.create_text(
            CANVAS_W - 20,
            44,
            text=f"Pen: {self.misses} x {EMAIL_PENALTY_PER_MISS:.1f}s",
            fill=WARN,
            font=("TkDefaultFont", 12),
            anchor="ne",
        )

        # Email composition window
        margin = 20
        email_x = margin
        email_y = 80
        email_w = CANVAS_W - margin * 2
        email_h = 400
        
        # Email window frame
        c.create_rectangle(email_x, email_y, email_x + email_w, email_y + email_h, 
                           fill="#ffffff", width=2, outline="#cccccc")
        
        # Email header bar
        c.create_rectangle(email_x, email_y, email_x + email_w, email_y + 30, 
                           fill="#f5f5f5", width=0)
        c.create_text(email_x + 10, email_y + 15, text="New Email", 
                      fill="#333333", font=("TkDefaultFont", 12, "bold"), anchor="w")
        
        # Email fields
        field_y = email_y + 50
        c.create_text(email_x + 10, field_y, text="To:", 
                      fill="#666666", font=("TkDefaultFont", 11, "bold"), anchor="w")
        c.create_text(email_x + 30, field_y, text="client@fortune500.com", 
                      fill="#333333", font=("TkDefaultFont", 11), anchor="w")
        
        field_y += 25
        c.create_text(email_x + 10, field_y, text="Subject:", 
                      fill="#666666", font=("TkDefaultFont", 11, "bold"), anchor="w")
        c.create_text(email_x + 70, field_y, text="Urgent: Q4 Strategy Update", 
                      fill="#333333", font=("TkDefaultFont", 11), anchor="w")
        
        # Email body separator
        field_y += 30
        c.create_line(email_x + 10, field_y, email_x + email_w - 10, field_y, 
                      fill="#cccccc", width=1)
        
        # Email body area
        body_y = field_y + 20
        c.create_text(email_x + 10, body_y, text="Email Body:", 
                      fill="#666666", font=("TkDefaultFont", 11, "bold"), anchor="w")
        
        # Target text (what they need to type)
        target_y = body_y + 30
        c.create_rectangle(email_x + 10, target_y, email_x + email_w - 10, target_y + 120, 
                           fill="#fafafa", width=1, outline="#dddddd")
        c.create_text(
            email_x + 15,
            target_y + 60,
            text=self.target,
            fill="#333333",
            font=("TkDefaultFont", 12),
            width=email_w - 30,
            justify="left",
            anchor="w"
        )
        
        # Typed text area (what they've typed so far)
        typed_y = target_y + 140
        c.create_rectangle(email_x + 10, typed_y, email_x + email_w - 10, typed_y + 120, 
                           fill="#ffffff", width=1, outline="#4CAF50")
        c.create_text(email_x + 10, typed_y - 15, text="Your Response:", 
                      fill="#4CAF50", font=("TkDefaultFont", 11, "bold"), anchor="w")
        # Colorize typed vs target
        correct_len = 0
        for i, ch in enumerate(self.typed):
            if i < len(self.target) and ch == self.target[i]:
                correct_len += 1
            else:
                break
        # Draw typed text in the email response area
        if self.typed:
            # Show the typed text in the response area
            text_color = "#4CAF50" if correct_len == len(self.typed) else "#f44336"
            c.create_text(
                email_x + 15,
                typed_y + 60,
                text=self.typed,
                fill=text_color,
                font=("TkDefaultFont", 12),
                width=email_w - 30,
                justify="left",
                anchor="w"
            )
        else:
            # Show placeholder text when nothing typed
            c.create_text(
                email_x + 15,
                typed_y + 60,
                text="Type your response here...",
                fill="#999999",
                font=("TkDefaultFont", 12, "italic"),
                width=email_w - 30,
                justify="left",
                anchor="w"
            )

        # Start/help overlay
        if not self.started:
            # BCG-style professional overlay
            c.create_rectangle(0, 0, CANVAS_W, CANVAS_H, fill="#1a1a2e", stipple="gray25", width=0)
            
            # Header section
            c.create_rectangle(40, 80, CANVAS_W - 40, 120, fill="#0f3460", width=2, outline="#4a90e2")
            c.create_text(
                CANVAS_W // 2,
                100,
                text="BCG STRATEGIC COMMUNICATION ASSESSMENT",
                fill="#4a90e2",
                font=("TkDefaultFont", 16, "bold"),
            )
            
            # Main content box
            c.create_rectangle(60, 140, CANVAS_W - 60, 400, fill="#2c3e50", width=2, outline="#34495e")
            
            lines = [
                "CLIENT CRISIS SCENARIO:",
                "Your Fortune 500 client needs 47 critical emails",
                "sent to stakeholders by 5:00 PM EST.",
                "",
                "STRATEGIC OBJECTIVES:",
                "• Demonstrate exceptional typing speed under pressure",
                "• Execute flawlessly in high-stakes environment",
                "",
                "OPERATIONAL INSTRUCTIONS:",
                "Type the sentence exactly as displayed.",
                "Backspace corrects mistakes. Enter submits when complete.",
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
                text="BEGIN EMAIL ASSESSMENT",
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
        # Active typing
        if e.keysym == "BackSpace":
            if self.typed:
                self.typed = self.typed[:-1]
            return
        if e.keysym == "Return":
            if self.typed == self.target:
                self.finish(app)
            else:
                app.toasts.add("Not matching yet")
            return
        ch = e.char
        if ch:
            idx = len(self.typed)
            if idx >= len(self.target) or ch != self.target[idx]:
                self.misses += 1
                app.toasts.add(f"Mismatch +{EMAIL_PENALTY_PER_MISS:.1f}s")
            self.typed += ch
            if self.typed == self.target:
                self.finish(app)
