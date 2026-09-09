// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
// Leaderboard localStorage key and utilities
const LEADERBOARD_KEY = 'sudoku_leaderboard_v1';
const THEME_KEY = 'sudoku_theme_v1';

function applyTheme(theme) {
  try {
    if (theme === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
    else document.documentElement.removeAttribute('data-theme');
  } catch (e) {
    console.warn('Failed to apply theme', e);
  }
}

function loadTheme() {
  try {
    const raw = localStorage.getItem(THEME_KEY);
    if (!raw) return null;
    if (raw === 'dark' || raw === 'light') return raw;
    return null;
  } catch (e) {
    console.warn('Theme load failed', e);
    try { localStorage.removeItem(THEME_KEY); } catch(_){}
    return null;
  }
}

function saveTheme(theme) {
  try { localStorage.setItem(THEME_KEY, theme); } catch (e) { console.warn('Theme save failed', e); }
}

function loadLeaderboard() {
  try {
    const raw = localStorage.getItem(LEADERBOARD_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed;
  } catch (e) {
    // corrupt data — reset
    console.warn('Leaderboard parse error, resetting', e);
    try { localStorage.removeItem(LEADERBOARD_KEY); } catch(_){}
    return [];
  }
}

function saveLeaderboard(entries) {
  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(entries));
  } catch (e) {
    console.warn('Failed to save leaderboard', e);
  }
}

function formatTimeDisplay(seconds) {
  return formatTime(seconds);
}

function renderLeaderboard() {
  const tbody = document.querySelector('#leaderboard-table tbody');
  if (!tbody) return;
  tbody.innerHTML = '';
  const entries = loadLeaderboard();
  for (let i = 0; i < entries.length; i++) {
    const e = entries[i];
    const tr = document.createElement('tr');
    const rankTd = document.createElement('td'); rankTd.innerText = String(i+1);
    const nameTd = document.createElement('td'); nameTd.innerText = e.name || 'Anonymous';
    const timeTd = document.createElement('td'); timeTd.innerText = e.timeDisplay || formatTimeDisplay(e.timeSeconds || 0);
    const diffTd = document.createElement('td'); diffTd.innerText = e.difficulty || '';
    const hintsTd = document.createElement('td'); hintsTd.innerText = String(e.hints || 0);
    tr.appendChild(rankTd);
    tr.appendChild(nameTd);
    tr.appendChild(timeTd);
    tr.appendChild(diffTd);
    tr.appendChild(hintsTd);
    tbody.appendChild(tr);
  }
}

function recordScoreIfNeeded() {
  // Prevent duplicate recordings for the same completion event
  if (window.leaderboardRecorded) return;
  // require finalElapsed and that the game was completed
  if (!window.gameCompleted) return;
  const final = window.finalElapsed;
  if (typeof final !== 'number') return;

  // gather metadata
  const nameEl = document.getElementById('player-name');
  let name = nameEl ? nameEl.value.trim() : '';
  if (!name) name = 'Anonymous';
  const difficulty = window.currentDifficulty || document.getElementById('difficulty-select')?.value || '';
  const hints = window.hintsUsed || 0;

  const entries = loadLeaderboard();
  // create new entry
  const entry = {
    name,
    timeSeconds: final,
    timeDisplay: formatTimeDisplay(final),
    difficulty,
    hints,
    ts: new Date().toISOString()
  };

  entries.push(entry);
  // sort ascending by timeSeconds
  entries.sort((a, b) => (a.timeSeconds || 0) - (b.timeSeconds || 0));
  // keep top 10
  const top = entries.slice(0, 10);
  saveLeaderboard(top);
  renderLeaderboard();
  window.leaderboardRecorded = true;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.inputMode = 'numeric';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      // add 3x3 block parity class for alternating block styling
      const blockParity = ((Math.floor(i/3) + Math.floor(j/3)) % 2 === 0) ? 'block-even' : 'block-odd';
      input.classList.add(blockParity);
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        validateBoard();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function getInputs() {
  return document.getElementById('sudoku-board').getElementsByTagName('input');
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      // clear any previous state
      inp.classList.remove('prefilled', 'incorrect');
      if (val !== 0) {
        inp.value = String(val);
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
  validateBoard();
}

function readBoardValues() {
  const board = [];
  const inputs = getInputs();
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function validateBoard() {
  const inputs = getInputs();
  // clear incorrect markers on editable cells
  for (let k = 0; k < inputs.length; k++) {
    if (!inputs[k].disabled) inputs[k].classList.remove('incorrect');
  }

  for (let r = 0; r < SIZE; r++) {
    for (let c = 0; c < SIZE; c++) {
      const idx = r * SIZE + c;
      const inp = inputs[idx];
      if (inp.disabled) continue; // only validate editable cells for marking
      const val = inp.value;
      if (!val) continue;

      let conflict = false;

      // Row check
      for (let cc = 0; cc < SIZE; cc++) {
        if (cc === c) continue;
        const other = inputs[r * SIZE + cc];
        if (other.value === val) { conflict = true; break; }
      }
      // Column check
      if (!conflict) {
        for (let rr = 0; rr < SIZE; rr++) {
          if (rr === r) continue;
          const other = inputs[rr * SIZE + c];
          if (other.value === val) { conflict = true; break; }
        }
      }
      // Box check
      if (!conflict) {
        const br = Math.floor(r / 3) * 3;
        const bc = Math.floor(c / 3) * 3;
        for (let rr = br; rr < br + 3 && !conflict; rr++) {
          for (let cc = bc; cc < bc + 3; cc++) {
            if (rr === r && cc === c) continue;
            const other = inputs[rr * SIZE + cc];
            if (other.value === val) { conflict = true; break; }
          }
        }
      }

      if (conflict) inp.classList.add('incorrect');
      else inp.classList.remove('incorrect');
    }
  }
  // After client-side validation, if board is full and no client-detected conflicts,
  // verify completion with server once.
  let hasEmpty = false;
  let hasClientConflict = false;
  for (let k = 0; k < inputs.length; k++) {
    if (!inputs[k].value) { hasEmpty = true; break; }
    if (inputs[k].classList.contains('incorrect')) { hasClientConflict = true; }
  }
  if (!hasEmpty && !hasClientConflict && !window.gameCompleted) {
    // verify authoritative correctness
    (async () => {
      const board = readBoardValues();
      const res = await fetch('/check', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({board})
      });
      const data = await res.json();
      if (!data.error && data.incorrect && data.incorrect.length === 0) {
        // mark completion
        window.gameCompleted = true;
        const msg = document.getElementById('message');
        msg.style.color = '#388e3c';
        msg.innerText = 'Congratulations! You solved it!';
        // lock all inputs (including editable ones)
        for (let k = 0; k < inputs.length; k++) inputs[k].disabled = true;
        // stop timer and record final elapsed time
        stopTimer();
        window.finalElapsed = window.elapsedSeconds || 0;
          // record leaderboard entry if appropriate
          try { recordScoreIfNeeded(); } catch (e) { console.warn('Leaderboard record failed', e); }
      }
    })();
  }
}

// Timer utilities
function formatTime(seconds) {
  const mm = String(Math.floor(seconds / 60)).padStart(2, '0');
  const ss = String(seconds % 60).padStart(2, '0');
  return `${mm}:${ss}`;
}

function updateTimerDisplay() {
  const el = document.getElementById('timer');
  if (!el) return;
  el.innerText = formatTime(window.elapsedSeconds || 0);
}

function stopTimer() {
  if (window.timerInterval) {
    clearInterval(window.timerInterval);
    window.timerInterval = null;
  }
}

function resetTimer() {
  stopTimer();
  window.elapsedSeconds = 0;
  updateTimerDisplay();
}

function startTimer() {
  // ensure single interval
  stopTimer();
  window.elapsedSeconds = 0;
  updateTimerDisplay();
  window.timerInterval = setInterval(() => {
    window.elapsedSeconds = (window.elapsedSeconds || 0) + 1;
    updateTimerDisplay();
  }, 1000);
}

async function newGame() {
  // Immediately stop any running timer when New Game is requested
  stopTimer();
  const select = document.getElementById('difficulty-select');
  const diff = select ? select.value : '';
  const url = diff ? `/new?difficulty=${encodeURIComponent(diff)}` : '/new';
  const msg = document.getElementById('message');
  try {
    const res = await fetch(url);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      msg.style.color = '#d32f2f';
      msg.innerText = err.error || 'Failed to start new game';
      // ensure timer is reset and stopped
      resetTimer();
      stopTimer();
      return;
    }
    const data = await res.json();
    renderPuzzle(data.puzzle);
    document.getElementById('message').innerText = '';
    // reset hint/completion state
    window.hintsUsed = 0;
    // allow leaderboard recording again for this new game
    window.leaderboardRecorded = false;
    // remember the difficulty for this game (so changing the selector later doesn't affect recorded difficulty)
    window.currentDifficulty = diff || null;
    window.gameCompleted = false;
    window.finalElapsed = undefined;
    // start the timer automatically as soon as the new puzzle is ready
    startTimer();
  } catch (err) {
    // Network/fetch error: stop and reset timer, show error
    msg.style.color = '#d32f2f';
    msg.innerText = 'Network error while starting new game';
    resetTimer();
    stopTimer();
    return;
  }
}

async function requestHint() {
  if (window.gameCompleted) return;
  const board = readBoardValues();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (!res.ok) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error || 'Unable to get hint';
    return;
  }
  const [r, c, val] = data.hint;
  const idx = r * SIZE + c;
  const inputs = getInputs();
  const inp = inputs[idx];
  // do not overwrite existing user entries
  if (inp.value) return;
  inp.value = String(val);
  inp.disabled = true;
  inp.classList.add('hinted');
  inp.classList.add('prefilled');
  window.hintsUsed = data.hints_used || (window.hintsUsed + 1);
  validateBoard();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  // determine whether the board is fully filled
  let hasEmpty = false;
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      if (board[i][j] === 0) { hasEmpty = true; break; }
    }
    if (hasEmpty) break;
  }
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    // preserve other classes (prefilled/hinted) and only toggle 'incorrect'
    inp.classList.remove('incorrect');
    if (incorrect.has(idx)) inp.classList.add('incorrect');
  }
  if (!hasEmpty && incorrect.size === 0) {
    // only treat as completion when board is full and server reports no incorrect cells
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    // lock inputs and stop timer
    window.gameCompleted = true;
    const boardInputs = document.getElementById('sudoku-board').getElementsByTagName('input');
    for (let k = 0; k < boardInputs.length; k++) boardInputs[k].disabled = true;
    stopTimer();
    window.finalElapsed = window.elapsedSeconds || 0;
    try { recordScoreIfNeeded(); } catch (e) { console.warn('Leaderboard record failed', e); }
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  const hintBtn = document.getElementById('hint-button');
  if (hintBtn) hintBtn.addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  // initialize
  // initialize leaderboard UI and game-scoped variables
  window.hintsUsed = 0;
  window.gameCompleted = false;
  window.leaderboardRecorded = false;
  window.currentDifficulty = document.getElementById('difficulty-select')?.value || null;
  renderLeaderboard();
  // initialize theme from localStorage and wire toggle
  const saved = loadTheme();
  if (saved) applyTheme(saved);
  const darkToggle = document.getElementById('dark-toggle');
  if (darkToggle) {
    darkToggle.checked = (saved === 'dark');
    darkToggle.addEventListener('change', (e) => {
      const t = e.target.checked ? 'dark' : 'light';
      applyTheme(t === 'dark' ? 'dark' : 'light');
      saveTheme(t === 'dark' ? 'dark' : 'light');
    });
  }
  newGame();
});
