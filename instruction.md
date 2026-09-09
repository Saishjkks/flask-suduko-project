# Flask Sudoku Project Guidance

## Project architecture
- Keep Flask/backend responsibilities separate from Sudoku game logic.
- Keep frontend HTML, CSS, and JavaScript responsibilities reasonably separated.
- Prefer small, focused, maintainable functions.
- Avoid unnecessary global mutable state.
- Keep business/game logic testable independently from Flask routes.
- Preserve the existing working behavior unless a requirement explicitly requires changing it.

## Python/backend standards
- Follow PEP 8.
- Use clear, descriptive names.
- Add useful docstrings and type hints where appropriate.
- Validate request data and handle malformed input safely.
- Do not expose internal errors to users.
- Avoid duplicated logic.
- Keep the backend logic deterministic and easy to test.
- Prefer explicit validation over implicit assumptions.

## Sudoku correctness
- Every generated puzzle must have exactly one valid solution.
- Difficulty levels must produce appropriately different numbers of prefilled cells.
- Prefilled cells must remain locked on the client.
- Sudoku validation must correctly enforce row, column, and 3x3 box constraints.
- User moves should receive immediate invalid-move feedback.
- Hints must fill a correct cell and lock that cell.
- Completion must only be reported when the puzzle is correctly solved.
- Do not accept logic that passes the UI but violates Sudoku rules.

## Application state
- Avoid shared global game state between users.
- Keep game state isolated appropriately.
- Do not rely on client-side data for security-sensitive correctness decisions.
- Use server-side checks for correctness-sensitive logic when needed.

## Frontend standards
- Use semantic, readable HTML.
- Keep JavaScript modular and understandable.
- Keep CSS organized and maintainable.
- The interface must work on desktop and mobile.
- Support both light mode and dark mode.
- Sudoku 3x3 regions must have alternating visual styling.
- Controls and text must remain readable and consistent.
- Prefilled cells should be visually distinct from editable cells.

## Game features
- Difficulty selection: Easy, Medium, Hard.
- Timer.
- Hint functionality.
- Check functionality that identifies incorrect entries.
- Completion/win message.
- Top 10 fastest times.
- Leaderboard records must persist using browser localStorage.
- Leaderboard records must include player name, time, difficulty, and hints used.

## Testing
- Use pytest.
- Run the relevant tests after every backend refactor or feature.
- Add tests for every new backend behavior.
- Test Sudoku correctness, uniqueness, difficulty behavior, routes, validation, and error handling.
- Do not remove or weaken existing tests simply to make the suite pass.
- Keep tests deterministic and independent.
- Prefer small, focused tests for specific behavior.

## GitHub Copilot usage
- Analyze the existing implementation before making substantial changes.
- Make one focused change at a time.
- Explain proposed changes before implementing them when practical.
- Do not blindly accept generated code.
- Check generated code for correctness, maintainability, security, and compliance with project requirements.
- Prefer minimal, understandable implementations over unnecessary complexity.
- When requirements conflict with the existing legacy implementation, prioritize the explicit project requirements while preserving unrelated working behavior.

## Documentation
- Keep README.md updated with setup instructions, test commands, and important project usage information.
- Keep implementation behavior consistent with the documented requirements.

## General rule
- The project must remain runnable throughout development.
- Do not introduce unnecessary dependencies.
- Do not change unrelated functionality.
- Keep changes scoped to the task at hand.
- Validate with the smallest relevant test run after changes.
