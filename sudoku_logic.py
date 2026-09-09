import copy
import random
from typing import Optional, Tuple, List

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1


# Difficulty mapping
_DIFFICULTY_TO_CLUES = {
    "easy": 45,
    "medium": 35,
    "hard": 25,
}


def _difficulty_to_clues(difficulty: str) -> int:
    if not isinstance(difficulty, str):
        raise ValueError(f"Invalid difficulty: {difficulty!r}")
    key = difficulty.strip().lower()
    if key not in _DIFFICULTY_TO_CLUES:
        raise ValueError(f"Invalid difficulty: {difficulty!r}")
    return _DIFFICULTY_TO_CLUES[key]


def generate_puzzle(clues: int = 35, difficulty: Optional[str] = None) -> Tuple[List[List[int]], List[List[int]]]:
    """
    Generate a puzzle and its solution.

    - Backwards-compatible: calling generate_puzzle(35) still works.
    - New interface: generate_puzzle(difficulty='easy') uses predefined clue counts.
    - Raises ValueError for invalid difficulty values.
    - Always verifies uniqueness and that the unique solution matches the generated solution.
    """
    if difficulty is not None:
        # Validate and map difficulty to clues; do not silently fallback.
        clues = _difficulty_to_clues(difficulty)

    # We'll try multiple full-solution generation attempts. Some filled boards
    # are harder to prune to the requested clue count while preserving
    # uniqueness; retrying with a fresh filled board improves robustness.
    MAX_GENERATION_ATTEMPTS = 10
    max_removal_attempts = 1000
    removals_needed = SIZE * SIZE - clues

    for gen_try in range(1, MAX_GENERATION_ATTEMPTS + 1):
        # Create a fresh filled solution
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)

        # Attempt removals for this filled board
        positions = [(r, c) for r in range(SIZE) for c in range(SIZE)]
        random.shuffle(positions)
        removed = 0
        attempts = 0
        idx = 0

        while removed < removals_needed and attempts < max_removal_attempts and idx < len(positions):
            r, c = positions[idx]
            idx += 1
            if board[r][c] == EMPTY:
                continue
            backup = board[r][c]
            board[r][c] = EMPTY

            attempts += 1
            sol_count = count_solutions(board, limit=2)
            if sol_count == 1:
                removed += 1
            else:
                # revert removal if uniqueness lost or no solution
                board[r][c] = backup

        if removed < removals_needed:
            # This filled board couldn't be pruned to target clues; try another full board
            continue

        puzzle = deep_copy(board)

        # Verify the unique solution corresponds to the original filled board
        solved = solve_one(puzzle)
        if solved is None:
            # Somehow no solution; try next generation
            continue
        if solved != solution:
            # Unique solution doesn't match original filled board; try next generation
            continue

        # Success
        return puzzle, solution

    # All generation attempts failed
    raise RuntimeError(f"Failed to generate unique puzzle with {clues} clues after {MAX_GENERATION_ATTEMPTS} generation attempts")


def get_candidates(board, row, col):
    if board[row][col] != EMPTY:
        return []
    candidates = []
    for num in range(1, SIZE + 1):
        if is_safe(board, row, col, num):
            candidates.append(num)
    return candidates


def find_least_candidates_cell(board):
    best = None
    best_count = 10
    for r in range(SIZE):
        for c in range(SIZE):
            if board[r][c] == EMPTY:
                candidates = get_candidates(board, r, c)
                if not candidates:
                    return (r, c, [])
                if len(candidates) < best_count:
                    best_count = len(candidates)
                    best = (r, c, candidates)
    return best


def count_solutions(board, limit=2):
    # Count solutions up to `limit` using backtracking with MRV heuristic.
    def backtrack(bd):
        nonlocal solutions
        if solutions >= limit:
            return
        cell = find_least_candidates_cell(bd)
        if cell is None:
            solutions += 1
            return
        r, c, candidates = cell
        if not candidates:
            return
        for val in candidates:
            bd[r][c] = val
            backtrack(bd)
            bd[r][c] = EMPTY
            if solutions >= limit:
                return

    solutions = 0
    board_copy = deep_copy(board)
    backtrack(board_copy)
    return solutions


def solve_one(board):
    # Return one solution board (deep copy) or None if no solution.
    found = None

    def backtrack(bd):
        nonlocal found
        if found is not None:
            return
        cell = find_least_candidates_cell(bd)
        if cell is None:
            found = deep_copy(bd)
            return
        r, c, candidates = cell
        if not candidates:
            return
        for val in candidates:
            bd[r][c] = val
            backtrack(bd)
            bd[r][c] = EMPTY
            if found is not None:
                return

    backtrack(deep_copy(board))
    return found
