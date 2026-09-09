from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}


def _ensure_game_state():
    # Initialize auxiliary game state if missing
    if 'hints_used' not in CURRENT:
        CURRENT['hints_used'] = 0
    if 'completed' not in CURRENT:
        CURRENT['completed'] = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    difficulty = request.args.get('difficulty')
    try:
        if difficulty:
            puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
        else:
            clues = int(request.args.get('clues', 35))
            puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        # Do not leak internal failures; return a generic error
        return jsonify({'error': 'Failed to generate puzzle'}), 500

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    # record difficulty/clues for this game and reset hint/completion state
    if difficulty:
        CURRENT['difficulty'] = difficulty
        # remove any explicit clues key
        CURRENT.pop('clues', None)
    else:
        # clues was used
        clues = int(request.args.get('clues', 35))
        CURRENT['clues'] = clues
        CURRENT['difficulty'] = None
    CURRENT['hints_used'] = 0
    CURRENT['completed'] = False
    return jsonify({'puzzle': puzzle})


@app.route('/hint', methods=['POST'])
def hint():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400
    # board must be provided by client to avoid leaking solution
    if board is None:
        return jsonify({'error': 'Missing board data'}), 400

    # find positions that are empty on the provided board and were originally empty
    empty_positions = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            try:
                val = board[i][j]
            except Exception:
                return jsonify({'error': 'Invalid board format'}), 400
            if (puzzle[i][j] == sudoku_logic.EMPTY) and (val == 0):
                empty_positions.append((i, j))

    if not empty_positions:
        return jsonify({'error': 'No empty cells available for a hint'}), 400

    # choose one empty position (simple strategy: first)
    r, c = empty_positions[0]
    value = solution[r][c]

    # update hint count
    _ensure_game_state()
    CURRENT['hints_used'] = CURRENT.get('hints_used', 0) + 1

    return jsonify({'hint': [r, c, value], 'hints_used': CURRENT['hints_used']})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)