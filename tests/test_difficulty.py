import pytest
import sudoku_logic
import app as app_module

EXPECTED = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}


def count_clues(board):
    return sum(1 for r in range(sudoku_logic.SIZE) for c in range(sudoku_logic.SIZE) if board[r][c] != sudoku_logic.EMPTY)


@pytest.mark.parametrize("difficulty,expected", list(EXPECTED.items()))
def test_generate_puzzle_difficulty_counts_and_uniqueness(difficulty, expected):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
    assert count_clues(puzzle) == expected
    # Ensure prefilled cells match solution
    for r in range(sudoku_logic.SIZE):
        for c in range(sudoku_logic.SIZE):
            if puzzle[r][c] != sudoku_logic.EMPTY:
                assert puzzle[r][c] == solution[r][c]
    # Ensure uniqueness
    assert sudoku_logic.count_solutions(puzzle, limit=3) == 1


def test_invalid_difficulty_raises_value_error():
    with pytest.raises(ValueError):
        sudoku_logic.generate_puzzle(difficulty='not-a-level')


def test_new_route_accepts_difficulty_and_returns_expected_clues(client):
    # test client fixture comes from tests/conftest.py
    for difficulty, expected in EXPECTED.items():
        response = client.get('/new', query_string={'difficulty': difficulty})
        assert response.status_code == 200
        payload = response.get_json()
        assert 'puzzle' in payload
        puzzle = payload['puzzle']
        assert count_clues(puzzle) == expected
        assert app_module.CURRENT['puzzle'] == puzzle
        assert app_module.CURRENT['solution'] is not None


def test_new_route_rejects_invalid_difficulty(client):
    response = client.get('/new', query_string={'difficulty': 'bad-level'})
    assert response.status_code == 400
    payload = response.get_json()
    assert 'Invalid difficulty' in payload['error']


@pytest.mark.parametrize("difficulty,expected", list(EXPECTED.items()))
def test_generate_puzzle_multiple_runs(difficulty, expected):
    # generate multiple times to exercise retry behavior and ensure stability
    for _ in range(3):
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
        assert count_clues(puzzle) == expected
        # Ensure prefilled cells match solution
        for r in range(sudoku_logic.SIZE):
            for c in range(sudoku_logic.SIZE):
                if puzzle[r][c] != sudoku_logic.EMPTY:
                    assert puzzle[r][c] == solution[r][c]
        # Ensure uniqueness
        assert sudoku_logic.count_solutions(puzzle, limit=3) == 1
