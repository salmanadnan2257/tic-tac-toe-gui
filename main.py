"""Tic Tac Toe, a tkinter GUI.

Run with: python3 main.py

All board/win/draw logic lives in game.py and is imported here unchanged.
This file is only responsible for drawing the window, wiring up clicks,
and tracking the running score across rounds.
"""

import tkinter as tk
from tkinter import font as tkfont

from game import (
    new_board,
    make_move,
    check_winner,
    is_draw,
)

BG = "#1e1e2e"
CELL_BG = "#2a2a3d"
CELL_BG_HOVER = "#33334a"
X_COLOR = "#5ec8f8"
O_COLOR = "#f87272"
WIN_COLOR = "#f7d774"
TEXT_COLOR = "#e6e6f0"
MUTED_COLOR = "#9a9ab0"


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.board = new_board()
        self.current_player = "X"
        self.game_over = False
        self.scores = {"X": 0, "O": 0, "draws": 0}

        self.mark_font = tkfont.Font(family="Helvetica", size=36, weight="bold")
        self.status_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.score_font = tkfont.Font(family="Helvetica", size=11)

        self._build_layout()
        self._update_status()

    def _build_layout(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(padx=16, pady=(16, 8), fill="x")

        self.status_label = tk.Label(
            header, text="", font=self.status_font, bg=BG, fg=TEXT_COLOR
        )
        self.status_label.pack()

        grid_frame = tk.Frame(self.root, bg=BG)
        grid_frame.pack(padx=16, pady=8)

        self.buttons = []
        for i in range(9):
            row, col = divmod(i, 3)
            btn = tk.Button(
                grid_frame,
                text="",
                font=self.mark_font,
                width=3,
                height=1,
                bg=CELL_BG,
                fg=TEXT_COLOR,
                activebackground=CELL_BG_HOVER,
                relief="flat",
                bd=0,
                highlightthickness=1,
                highlightbackground=BG,
                command=lambda idx=i: self.on_cell_click(idx),
            )
            btn.grid(row=row, column=col, padx=4, pady=4, ipadx=8, ipady=8)
            self.buttons.append(btn)

        controls = tk.Frame(self.root, bg=BG)
        controls.pack(padx=16, pady=(4, 8), fill="x")

        self.play_again_btn = tk.Button(
            controls,
            text="Play again",
            font=self.score_font,
            bg=CELL_BG,
            fg=TEXT_COLOR,
            activebackground=CELL_BG_HOVER,
            relief="flat",
            bd=0,
            padx=10,
            pady=6,
            command=self.reset_board,
        )
        self.play_again_btn.pack(fill="x")

        score_frame = tk.Frame(self.root, bg=BG)
        score_frame.pack(padx=16, pady=(0, 16), fill="x")

        self.score_label = tk.Label(
            score_frame,
            text="",
            font=self.score_font,
            bg=BG,
            fg=MUTED_COLOR,
            justify="center",
        )
        self.score_label.pack()
        self._update_score_label()

    def on_cell_click(self, index):
        if self.game_over:
            return
        if not make_move(self.board, index, self.current_player):
            return

        self._render_cell(index)

        result = check_winner(self.board)
        if result is not None:
            winner, line = result
            self.game_over = True
            self.scores[winner] += 1
            self._highlight_line(line)
            self._update_status(winner=winner)
            self._update_score_label()
            return

        if is_draw(self.board):
            self.game_over = True
            self.scores["draws"] += 1
            self._update_status(draw=True)
            self._update_score_label()
            return

        self.current_player = "O" if self.current_player == "X" else "X"
        self._update_status()

    def _render_cell(self, index):
        mark = self.board[index]
        color = X_COLOR if mark == "X" else O_COLOR
        self.buttons[index].config(text=mark, fg=color, state="disabled", disabledforeground=color)

    def _highlight_line(self, line):
        for idx in line:
            self.buttons[idx].config(bg=WIN_COLOR, fg=BG, disabledforeground=BG)

    def _update_status(self, winner=None, draw=False):
        if winner:
            self.status_label.config(text=f"Player {winner} wins!")
        elif draw:
            self.status_label.config(text="It's a draw!")
        else:
            self.status_label.config(text=f"Player {self.current_player}'s turn")

    def _update_score_label(self):
        s = self.scores
        self.score_label.config(
            text=f"X wins: {s['X']}    O wins: {s['O']}    Draws: {s['draws']}"
        )

    def reset_board(self):
        self.board = new_board()
        self.current_player = "X"
        self.game_over = False
        for btn in self.buttons:
            btn.config(
                text="",
                bg=CELL_BG,
                fg=TEXT_COLOR,
                state="normal",
                disabledforeground=TEXT_COLOR,
            )
        self._update_status()


def main():
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
