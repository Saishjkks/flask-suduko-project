import pytest

import app as app_module


def build_complete_board():
    return [
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


def test_home_page_renders_html(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.content_type.startswith('text/html')
    assert b'<title>Sudoku Game</title>' in response.data


def test_new_game_route_returns_puzzle_and_stores_solution(client):
    response = client.get('/new', query_string={'clues': 35})

    assert response.status_code == 200
    payload = response.get_json()
    assert 'puzzle' in payload

    puzzle = payload['puzzle']
    assert isinstance(puzzle, list)
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert app_module.CURRENT['puzzle'] == puzzle
    assert app_module.CURRENT['solution'] is not None
    assert len(app_module.CURRENT['solution']) == 9
    assert all(len(row) == 9 for row in app_module.CURRENT['solution'])


def test_check_route_without_game_returns_error(client):
    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})

    assert response.status_code == 400
    payload = response.get_json()
    assert payload['error'] == 'No game in progress'


def test_check_route_accepts_correct_solution(client):
    solution = build_complete_board()
    app_module.CURRENT = {'puzzle': solution, 'solution': solution}

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['incorrect'] == []


def test_check_route_reports_incorrect_cells(client):
    solution = build_complete_board()
    wrong_board = [row[:] for row in solution]
    wrong_board[0][0] = 9

    app_module.CURRENT = {'puzzle': solution, 'solution': solution}
    response = client.post('/check', json={'board': wrong_board})

    assert response.status_code == 200
    payload = response.get_json()
    assert [0, 0] in payload['incorrect']


def test_hint_returns_one_cell_and_tracks_hints(client):
    # prepare a puzzle with two empty cells
    full = build_complete_board()
    puzzle = [row[:] for row in full]
    # make two empties
    puzzle[0][0] = 0
    puzzle[1][1] = 0
    app_module.CURRENT = {'puzzle': puzzle, 'solution': full}

    board = [row[:] for row in puzzle]
    response = client.post('/hint', json={'board': board})
    assert response.status_code == 200
    payload = response.get_json()
    assert 'hint' in payload
    r, c, val = payload['hint']
    # hinted position was originally empty
    assert puzzle[r][c] == 0
    # hinted value matches solution
    assert full[r][c] == val
    # ensure solution not leaked
    assert 'solution' not in payload


def test_hint_requires_game_and_board(client):
    app_module.CURRENT = {'puzzle': None, 'solution': None}
    response = client.post('/hint', json={'board': [[0]*9 for _ in range(9)]})
    assert response.status_code == 400
    payload = response.get_json()
    assert 'No game in progress' in payload['error']


def test_hint_no_empty_cells_returns_error(client):
    full = build_complete_board()
    puzzle = [row[:] for row in full]
    app_module.CURRENT = {'puzzle': puzzle, 'solution': full}
    board = [row[:] for row in full]
    response = client.post('/hint', json={'board': board})
    assert response.status_code == 400
    payload = response.get_json()
    assert 'No empty cells' in payload['error'] or 'No empty cells available' in payload['error']
