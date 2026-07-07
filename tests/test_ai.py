"""Unit tests for the minimax AI in game.py.

Run with: python3 -m unittest tests/test_ai.py -v
(or just `python3 -m unittest discover` from the project root)

No tkinter import anywhere in this file: the AI is pure logic, so it's
tested the same way the win/draw detection is, without opening a window.
"""

import os
import sys
import unittest

# Allow running this file directly without the project root on PYTHONPATH.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import best_ai_move, minimax, new_board


class TestBestAiMove(unittest.TestCase):
    def test_takes_immediate_winning_move(self):
        # X X _
        # O O _
        # _ _ _
        # AI is X and can win at index 2 right now.
        board = ["X", "X", "", "O", "O", "", "", "", ""]
        move = best_ai_move(board, "X")
        self.assertEqual(move, 2)

    def test_blocks_immediate_human_win(self):
        # O O _
        # X _ _
        # _ _ _
        # AI is X; O threatens to win at index 2 and must be blocked there.
        board = ["O", "O", "", "X", "", "", "", "", ""]
        move = best_ai_move(board, "X")
        self.assertEqual(move, 2)

    def test_prefers_win_over_block_when_both_available(self):
        # X X _
        # O O _
        # _ _ _
        # AI is X: it can either win immediately (index 2) or block O's
        # threat (also index 2, coincidentally in this layout) -- use a
        # layout where winning and blocking are genuinely different cells.
        # X can win at 2; O also threatens to win at 8 (diagonal 0,4,8 is
        # not complete for O here, so build a cleaner case instead):
        board = [
            "X", "X", "",   # X threatens to win at 2
            "O", "O", "",   # O threatens to win at 5
            "", "", "",
        ]
        move = best_ai_move(board, "X")
        self.assertEqual(move, 2, "AI should take its own win instead of blocking")

    def test_empty_board_optimal_first_move(self):
        # On an empty board, the game-theoretically optimal first moves
        # for the first player are the center or a corner; a center-first
        # opening is the classic optimal choice and is what this specific
        # minimax tie-breaking (first move in enumeration order that
        # achieves the best score, corners scanned before center would
        # differ) should produce. We assert on the score, which is the
        # part that actually matters: an empty board is a proven draw
        # with perfect play from both sides.
        board = new_board()
        score, move = minimax(board, "X", "X")
        self.assertEqual(score, 0, "perfect play on an empty board is a draw")
        self.assertIn(move, [0, 2, 4, 6, 8], "optimal opening is a corner or the center")

    def test_returns_none_on_full_board(self):
        board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        self.assertIsNone(best_ai_move(board, "X"))

    def test_takes_center_when_it_is_the_only_strong_reply(self):
        # X in a corner, nothing else on the board: minimax should not
        # blunder by picking an edge.
        board = ["X", "", "", "", "", "", "", "", ""]
        move = best_ai_move(board, "O")
        self.assertEqual(move, 4)


if __name__ == "__main__":
    unittest.main()
