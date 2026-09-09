# Flask Sudoku Game

A feature-rich Sudoku game built with Python Flask and enhanced with GitHub Copilot.

## Features

- 9×9 Sudoku board
- Three difficulty levels:
  - Easy — 45 prefilled cells
  - Medium — 35 prefilled cells
  - Hard — 25 prefilled cells
- Every generated puzzle has exactly one unique solution
- Prefilled cells are locked
- Immediate visual feedback for invalid moves
- Check Solution functionality
- Hint functionality that fills and locks one correct cell
- Puzzle completion detection and congratulations message
- Game timer
- Top 10 fastest-times leaderboard
- Player name, time, difficulty, and hint count recorded
- Leaderboard persistence using browser localStorage
- Light and dark modes
- Alternating styling for the 3×3 Sudoku blocks
- Responsive layout for different screen sizes

## Technology

- Python
- Flask
- JavaScript
- HTML
- CSS
- pytest

## Project Structure

```text
starter/
├── app.py
├── sudoku_logic.py
├── requirements.txt
├── instruction.md
├── pytest.ini
├── README.md
├── static/
│   ├── main.js
│   └── styles.css
├── templates/
│   └── index.html
├── tests/
└── Screenshots/



## Project Implementation

This project started as a legacy Flask Sudoku application and was progressively refactored and extended with GitHub Copilot.

### Sudoku Generation and Unique Solutions

The original application generated a completed Sudoku board and removed cells to create a puzzle, but it did not verify that the resulting puzzle had only one possible solution.

The Sudoku logic was refactored to include a solution-counting mechanism. During puzzle generation, cells are removed only when the resulting puzzle remains uniquely solvable. A puzzle is accepted only when exactly one solution exists.

The generator also uses retry logic with a maximum number of generation attempts. If a valid uniquely solvable puzzle with the required number of clues cannot be produced, generation fails explicitly instead of returning an invalid puzzle.

### Difficulty Levels

Three difficulty levels were added to the puzzle-generation system:

- **Easy:** 45 prefilled cells
- **Medium:** 35 prefilled cells
- **Hard:** 25 prefilled cells

Difficulty selection is connected to the Flask `/new` endpoint. The selected difficulty is applied when a new game is started, while the current puzzle remains unchanged if the selector is changed without starting a new game.

Tests verify the clue counts and unique-solution requirement for the different difficulty levels.

### Game Interaction

The frontend was enhanced to distinguish between prefilled Sudoku clues and cells that can be edited by the player.

Prefilled cells are disabled so they cannot be modified through the normal interface. User-entered cells are validated immediately against Sudoku row, column, and 3×3 block constraints. Invalid entries receive visual feedback as soon as a conflict is detected, and the feedback is removed when the conflict is corrected.

The existing server-side Check Solution functionality was preserved so that the authoritative Sudoku solution remains on the server.

### Hint System

A Hint feature was added using a dedicated Flask endpoint.

When requested, the server selects one currently empty editable cell and returns only that cell's position and correct value. The frontend inserts the value and locks the hinted cell so it cannot be changed.

The complete Sudoku solution is never sent to the browser through the Hint functionality. Hint usage is also tracked for the current game and later recorded in the leaderboard.

### Puzzle Completion

The application detects when the Sudoku has been completely and correctly solved.

After successful completion, a congratulations message is displayed and the board is locked to prevent further changes. The completion state is also used by the timer and leaderboard functionality.

### Timer and Game Sessions

A game timer was added to track the player's elapsed solving time.

The timer starts when a new puzzle is successfully loaded, resets for each new game, and stops when the puzzle is completed. Starting a new game also prevents the previous timer interval from continuing.

The selected difficulty and number of hints used remain associated with the active game so they can be included in the final leaderboard result.

### Leaderboard and Local Storage

A Top 10 leaderboard was implemented using browser `localStorage`.

When a puzzle is completed, the player's:

- Name
- Completion time
- Difficulty
- Number of hints used

are recorded as a score.

Scores are sorted by completion time, with the fastest results appearing first, and only the top 10 results are retained. Because the leaderboard is stored in `localStorage`, results remain available after refreshing or reopening the application in the same browser.

### Dark Mode and 3×3 Styling

A light/dark mode toggle was added to improve the visual experience.

The Sudoku board also uses alternating styling for its 3×3 blocks, making the individual Sudoku regions easier to distinguish while maintaining readability in both light and dark modes.

### Responsive Interface

The frontend styling was extended to adapt the Sudoku board and controls to different screen sizes. The layout is designed to remain usable on both desktop and smaller displays.

### Testing

A pytest-based testing framework was established before the application refactoring began.

The original application behavior was first covered by baseline tests. Subsequent changes added focused tests for Sudoku generation, unique solutions, difficulty levels, Flask routes, hints, and related game behavior.

The complete test suite was repeatedly executed throughout development to ensure that new functionality did not break existing functionality.

### GitHub Copilot Development Process

GitHub Copilot was used throughout the project as a development assistant rather than accepting changes blindly.

The development process included:

1. Asking Copilot to analyze the legacy application before making changes.
2. Establishing baseline tests before refactoring.
3. Creating `instruction.md` to provide project-specific development guidance.
4. Implementing individual features through focused Copilot prompts.
5. Reviewing Copilot's proposed changes before accepting them.
6. Running the complete test suite after significant changes.
7. Manually verifying frontend behavior in the browser.
8. Identifying and correcting an actual JavaScript issue introduced during development rather than accepting the broken implementation.
9. Re-running the tests after corrections.

The `Screenshots/` directory contains evidence of the development process, Copilot interactions, testing, and major implemented features.