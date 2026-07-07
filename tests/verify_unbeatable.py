"""Exhaustive-and-simulation proof that the minimax AI never loses.

This is not a unittest; it's a standalone verification script, run with:

    python3 tests/verify_unbeatable.py

It does three separate checks and prints real aggregate numbers for each:

1. Exhaustive search over every possible human strategy (the human is
   played by every legal move at every one of its turns, branching into
   all of them, i.e. a full game-tree traversal of the human's choices)
   against the AI's minimax move at every AI turn, for both starting
   orders (AI first, human first). This does not sample; it visits every
   distinct game that can be produced by any human move sequence.
2. 1000 games with the human playing uniformly random legal moves, again
   for both starting orders.
3. The human playing minimax itself (i.e. two optimal players), which
   must always end in a draw by game theory, run for both starting orders.

If the AI ever loses a single game in any of these, this script exits
with a non-zero status and prints the losing board.
"""

import os
import random
import sys

# Allow running this script directly (python3 tests/verify_unbeatable.py)
# without needing the project root on PYTHONPATH already.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import (
    new_board,
    make_move,
    check_winner,
    is_draw,
    best_ai_move,
    available_moves,
    other_mark,
)


def play_out_random_human(ai_mark, human_mark, rng):
    """One full game: AI uses minimax, human picks uniformly at random."""
    board = new_board()
    current = "X"
    while True:
        if current == ai_mark:
            move = best_ai_move(board, ai_mark)
        else:
            move = rng.choice(available_moves(board))
        make_move(board, move, current)
        result = check_winner(board)
        if result is not None:
            return result[0], board
        if is_draw(board):
            return None, board
        current = other_mark(current)


def play_out_optimal_human(ai_mark, human_mark):
    """One full game: both sides use minimax (human plays optimally too)."""
    from game import minimax

    board = new_board()
    current = "X"
    while True:
        if current == ai_mark:
            move = best_ai_move(board, ai_mark)
        else:
            _, move = minimax(board, current_mark=human_mark, ai_mark=human_mark)
        make_move(board, move, current)
        result = check_winner(board)
        if result is not None:
            return result[0], board
        if is_draw(board):
            return None, board
        current = other_mark(current)


def exhaustive_all_human_strategies(ai_mark, human_mark):
    """Visit every game reachable by any human move choice at every human
    turn, with the AI always replying via minimax. Returns tallies."""
    tallies = {"ai": 0, "human": 0, "draw": 0}
    losing_boards = []

    def recurse(board, current):
        result = check_winner(board)
        if result is not None:
            winner = result[0]
            if winner == ai_mark:
                tallies["ai"] += 1
            else:
                tallies["human"] += 1
                losing_boards.append(list(board))
            return
        if is_draw(board):
            tallies["draw"] += 1
            return

        if current == ai_mark:
            move = best_ai_move(board, ai_mark)
            board[move] = current
            recurse(board, other_mark(current))
            board[move] = ""
        else:
            # Branch into every legal human move.
            for move in available_moves(board):
                board[move] = current
                recurse(board, other_mark(current))
                board[move] = ""

    recurse(new_board(), "X")
    return tallies, losing_boards


def main():
    failures = []

    print("=== 1. Exhaustive search over every human move sequence ===")
    for ai_mark, human_mark, label in [("O", "X", "human moves first"), ("X", "O", "AI moves first")]:
        tallies, losing_boards = exhaustive_all_human_strategies(ai_mark, human_mark)
        total = sum(tallies.values())
        print(
            f"  [{label}] {total} distinct games explored -> "
            f"AI won: {tallies['ai']}, draws: {tallies['draw']}, AI lost: {tallies['human']}"
        )
        if tallies["human"] > 0:
            failures.append((label, losing_boards[0]))

    print()
    print("=== 2. 1000 games, human plays uniformly random legal moves ===")
    rng = random.Random(42)
    for ai_mark, human_mark, label in [("O", "X", "human moves first"), ("X", "O", "AI moves first")]:
        results = {"ai": 0, "human": 0, "draw": 0}
        for _ in range(1000):
            winner, board = play_out_random_human(ai_mark, human_mark, rng)
            if winner is None:
                results["draw"] += 1
            elif winner == ai_mark:
                results["ai"] += 1
            else:
                results["human"] += 1
                failures.append((f"{label} (random)", board))
        print(
            f"  [{label}] 1000 games -> "
            f"AI won: {results['ai']}, draws: {results['draw']}, AI lost: {results['human']}"
        )

    print()
    print("=== 3. Both sides play optimally (human also uses minimax) ===")
    for ai_mark, human_mark, label in [("O", "X", "human moves first"), ("X", "O", "AI moves first")]:
        winner, board = play_out_optimal_human(ai_mark, human_mark)
        outcome = "draw" if winner is None else ("AI won" if winner == ai_mark else "AI LOST")
        print(f"  [{label}] outcome: {outcome}")
        if winner == human_mark:
            failures.append((f"{label} (optimal)", board))

    print()
    if failures:
        print(f"FAILURE: the AI lost in {len(failures)} case(s):")
        for label, board in failures:
            print(f"  {label}: {board}")
        sys.exit(1)
    else:
        print("RESULT: the AI never lost a single game across all checks above.")


if __name__ == "__main__":
    main()
