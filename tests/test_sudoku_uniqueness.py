import sudoku_logic
import pytest


def test_generated_puzzle_has_one_solution_and_matches_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    # solution must be a complete valid board
    assert sudoku_logic.SIZE == 9
    assert len(solution) == sudoku_logic.SIZE
    for row in solution:
        assert len(row) == sudoku_logic.SIZE
    # check solution is valid
    assert all(sorted(row) == list(range(1, sudoku_logic.SIZE + 1)) for row in solution)
    for col in range(sudoku_logic.SIZE):
        col_vals = [solution[r][col] for r in range(sudoku_logic.SIZE)]
        assert sorted(col_vals) == list(range(1, sudoku_logic.SIZE + 1))

    # puzzle must have exactly one solution
    count = sudoku_logic.count_solutions(puzzle, limit=3)
    assert count == 1

    # the puzzle's filled cells must match the solution
    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):
            if puzzle[r][c] != sudoku_logic.EMPTY:
                assert puzzle[r][c] == solution[r][c]


def test_solution_satisfies_sudoku_constraints():
    _, solution = sudoku_logic.generate_puzzle(35)
    # rows
    for row in solution:
        assert set(row) == set(range(1, sudoku_logic.SIZE + 1))
    # cols
    for c in range(sudoku_logic.SIZE):
        col_vals = [solution[r][c] for r in range(sudoku_logic.SIZE)]
        assert set(col_vals) == set(range(1, sudoku_logic.SIZE + 1))
    # boxes
    for br in range(0, sudoku_logic.SIZE, 3):
        for bc in range(0, sudoku_logic.SIZE, 3):
            vals = []
            for r in range(br, br + 3):
                for c in range(bc, bc + 3):
                    vals.append(solution[r][c])
            assert set(vals) == set(range(1, sudoku_logic.SIZE + 1))


def test_count_solutions_on_empty_board_is_multiple():
    empty = sudoku_logic.create_empty_board()
    assert sudoku_logic.count_solutions(empty, limit=2) >= 2


def test_count_solutions_single_missing_cell_is_one():
    # take a complete board and remove one cell -> should be uniquely solvable
    full = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]
    board = [row[:] for row in full]
    board[0][0] = sudoku_logic.EMPTY
    assert sudoku_logic.count_solutions(board, limit=2) == 1


def test_generated_puzzle_solution_matches_solve_one():
    puzzle, solution = sudoku_logic.generate_puzzle(35)
    solved = sudoku_logic.solve_one(puzzle)
    assert solved == solution
