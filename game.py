"""Pure Tic Tac Toe game logic, no I/O and no GUI dependencies.

The board is a flat list of 9 cells, indexed 0-8, laid out left-to-right,
top-to-bottom:

    0 | 1 | 2
    3 | 4 | 5
    6 | 7 | 8

Each cell holds "X", "O", or "" (empty). Keeping this module free of any
tkinter or print/input calls means the win/draw detection (and the AI
opponent's move selection) can be unit tested directly, independent of
any UI.
"""

import math

EMPTY = ""

# All 8 ways to win: 3 rows, 3 columns, 2 diagonals.
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # columns
    (0, 4, 8), (2, 4, 6),             # diagonals
]


def new_board():
    """Return a fresh, empty 9-cell board."""
    return [EMPTY] * 9


def make_move(board, index, mark):
    """Place `mark` ("X" or "O") at `index` if the cell is empty.

    Returns True if the move was applied, False if the cell was already
    occupied (or index out of range).
    """
    if index < 0 or index > 8 or board[index] != EMPTY:
        return False
    board[index] = mark
    return True


def check_winner(board):
    """Check both X and O against all 8 win lines.

    Returns (winner_mark, winning_line_tuple) if either player has
    completed a line, otherwise None. This is the fix for the original
    bug, which only ever compared cells against " X ", so O could never
    be declared the winner.
    """
    for line in WIN_LINES:
        a, b, c = line
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a], line
    return None


def is_draw(board):
    """A draw is a full board with no winner."""
    return EMPTY not in board and check_winner(board) is None


def is_game_over(board):
    """True if someone has won or the board is full."""
    return check_winner(board) is not None or is_draw(board)


def available_moves(board):
    """Indices of every empty cell, in board order."""
    return [i for i, cell in enumerate(board) if cell == EMPTY]


def other_mark(mark):
    """The opposing mark: 'X' -> 'O', 'O' -> 'X'."""
    return "O" if mark == "X" else "X"


def _score_terminal(board, ai_mark, depth):
    """Score a finished board from the AI's point of view.

    A win for the AI scores positive, a win for the opponent scores
    negative, and a draw scores zero. Subtracting/adding `depth` makes
    the AI prefer winning sooner and losing later (if a loss were ever
    forced, which minimax guarantees it never is against best play).
    """
    result = check_winner(board)
    if result is None:
        return 0
    winner = result[0]
    return (10 - depth) if winner == ai_mark else (depth - 10)


def minimax(board, current_mark, ai_mark, depth=0, alpha=-math.inf, beta=math.inf):
    """Exhaustively search the game tree and return (best_score, best_move).

    `current_mark` is whoever is about to move on `board`. The search
    always evaluates outcomes relative to `ai_mark`: it maximizes on the
    AI's turns and minimizes on the opponent's turns, which is exactly
    the classic minimax algorithm. Alpha-beta pruning cuts off branches
    that can't change the final decision; it doesn't change the result,
    only how much of the tree gets visited.

    Returns (score, None) for an already-finished board, or
    (best_score, best_move_index) otherwise. `board` is left unchanged
    on return (moves are tried and undone in place).
    """
    if is_game_over(board):
        return _score_terminal(board, ai_mark, depth), None

    moves = available_moves(board)
    best_move = moves[0]

    if current_mark == ai_mark:
        best_score = -math.inf
        for move in moves:
            board[move] = current_mark
            score, _ = minimax(board, other_mark(current_mark), ai_mark, depth + 1, alpha, beta)
            board[move] = EMPTY
            if score > best_score:
                best_score, best_move = score, move
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
    else:
        best_score = math.inf
        for move in moves:
            board[move] = current_mark
            score, _ = minimax(board, other_mark(current_mark), ai_mark, depth + 1, alpha, beta)
            board[move] = EMPTY
            if score < best_score:
                best_score, best_move = score, move
            beta = min(beta, best_score)
            if beta <= alpha:
                break

    return best_score, best_move


def best_ai_move(board, ai_mark):
    """Return the index of the AI's optimal move on `board`, or None if full.

    This is the only function the GUI needs to call: give it the current
    board and which mark the AI is playing, get back where to move.
    Because minimax searches the entire remaining game tree, the move
    returned is always at least as good as any alternative, which is
    what makes the AI unbeatable (it can lose only to a mistake in this
    function, which the unit tests and the simulations in tests/ rule out).
    """
    if is_game_over(board):
        return None
    _, move = minimax(board, current_mark=ai_mark, ai_mark=ai_mark)
    return move
