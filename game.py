"""Pure Tic Tac Toe game logic, no I/O and no GUI dependencies.

The board is a flat list of 9 cells, indexed 0-8, laid out left-to-right,
top-to-bottom:

    0 | 1 | 2
    3 | 4 | 5
    6 | 7 | 8

Each cell holds "X", "O", or "" (empty). Keeping this module free of any
tkinter or print/input calls means the win/draw detection can be unit
tested directly, independent of any UI.
"""

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
