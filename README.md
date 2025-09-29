# Consulting Chaos - Refactored Structure

This is a refactored version of the Consulting Chaos game, organized into separate modules for better maintainability and extensibility.

## File Structure

- **`main.py`** - Main game orchestrator and entry point
- **`game_common.py`** - Shared utilities, base classes, and common functionality
- **`scenes.py`** - Menu, interlude, and results scenes
- **`email_blast.py`** - Email Blast minigame (typing test)
- **`excel_fire_drill.py`** - Excel Fire Drill minigame (quick math)
- **`puzzle_game.py`** - Puzzle minigame (Tetris-like puzzle solving)
- **`friday_escape.py`** - Friday Escape minigame (Partner Pac-Man maze escape)
- **`consulting_chaos.py`** - Original single-file version (kept for reference)

## How to Run

```bash
python3.13 main.py
```

## Complete Game Flow

The game now features a complete sequence of 4 minigames:

1. **Email Blast** - Type consulting jargon as fast as possible
2. **Excel Fire Drill** - Solve quick math problems
3. **Puzzle Game** - Place Tetris-like pieces on a grid
4. **Friday Escape** - Navigate a maze while avoiding enemies

Each minigame has its own scoring system with time-based penalties and performance bonuses.

## Architecture

### Main Orchestrator (`main.py`)

- Contains the `GameApp` class that manages the overall game state
- Handles the main game loop, scene management, and user input
- Coordinates between different game components

### Shared Components (`game_common.py`)

- Base `Scene` class for all game scenes
- `SceneManager` for handling scene transitions
- `HighScoreManager` for persistent high scores
- `Clock` for game timing
- `Toasts` for temporary UI messages
- `MinigameResult` dataclass for game results
- Common constants, colors, and utilities

### Scene Management (`scenes.py`)

- `MainMenu` - Game start screen
- `Interlude` - Transition screen between minigames
- `Results` - Final results and high score display

### Minigames

- **`email_blast.py`** - Typing test minigame
- **`excel_fire_drill.py`** - Quick math minigame
- **`puzzle_game.py`** - Tetris-like puzzle solving minigame
- **`friday_escape.py`** - Partner Pac-Man maze escape minigame

## Benefits of This Structure

1. **Modularity** - Each component has a clear responsibility
2. **Extensibility** - Easy to add new minigames by creating new files
3. **Maintainability** - Changes to one minigame don't affect others
4. **Testability** - Individual components can be tested in isolation
5. **Code Reuse** - Common functionality is centralized

## Adding New Minigames

To add a new minigame:

1. Create a new file (e.g., `new_minigame.py`)
2. Import the base `Scene` class from `game_common`
3. Create a class that inherits from `Scene`
4. Implement the required methods: `on_enter`, `update`, `draw`, `handle_key`
5. Update the game flow in `scenes.py` to include your new minigame

## Dependencies

- Python 3.13
- tkinter (usually included with Python)
- No external dependencies required
