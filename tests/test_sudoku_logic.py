import pytest

import sudoku_logic


SIZE = sudoku_logic.SIZE


def is_complete_valid_board(board):
    if len(board) != SIZE:
        return False

    for row in board:
        if len(row) != SIZE:
            return False
        values = [value for value in row if value != sudoku_logic.EMPTY]
        if set(values) != set(range(1, SIZE + 1)):
            return False

    for col in range(SIZE):
        values = [board[row][col] for row in range(SIZE) if board[row][col] != sudoku_logic.EMPTY]
        if set(values) != set(range(1, SIZE + 1)):
            return False

    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            values = []
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    value = board[row][col]
                    if value != sudoku_logic.EMPTY:
                        values.append(value)
            if set(values) != set(range(1, SIZE + 1)):
                return False

    return True


def test_generate_puzzle_returns_9x9_board_and_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert isinstance(puzzle, list)
    assert isinstance(solution, list)
    assert len(puzzle) == SIZE
    assert len(solution) == SIZE
    assert all(len(row) == SIZE for row in puzzle)
    assert all(len(row) == SIZE for row in solution)


def test_generated_solution_is_complete_and_valid():
    _, solution = sudoku_logic.generate_puzzle(35)

    assert is_complete_valid_board(solution)


def test_generated_puzzle_contains_valid_clues_and_empty_cells():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert any(value == sudoku_logic.EMPTY for row in puzzle for value in row)
    for row in range(SIZE):
        for col in range(SIZE):
            value = puzzle[row][col]
            if value != sudoku_logic.EMPTY:
                assert value == solution[row][col]


def test_is_safe_accepts_valid_number_in_empty_cell():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.is_safe(board, 0, 0, 5) is True
    assert sudoku_logic.is_safe(board, 4, 4, 9) is True


def test_is_safe_rejects_duplicate_in_row():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 2

    assert sudoku_logic.is_safe(board, 0, 2, 1) is False


def test_is_safe_rejects_duplicate_in_column():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[1][0] = 2

    assert sudoku_logic.is_safe(board, 2, 0, 1) is False


def test_is_safe_rejects_duplicate_in_3x3_box():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 2
    board[1][0] = 3

    assert sudoku_logic.is_safe(board, 2, 2, 1) is False
