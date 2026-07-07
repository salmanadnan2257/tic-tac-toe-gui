"""Tic Tac Toe, a tkinter GUI.

Run with: python3 main.py

All board/win/draw/AI logic lives in game.py and is imported here unchanged.
This file is only responsible for drawing the window, wiring up clicks,
scheduling the AI's move, and tracking the running score across rounds.
"""

import tkinter as tk
from tkinter import font as tkfont

from game import (
    new_board,
    make_move,
    check_winner,
    is_draw,
    best_ai_move,
    other_mark,
)

BG = "#1e1e2e"
CELL_BG = "#2a2a3d"
CELL_BG_HOVER = "#33334a"
X_COLOR = "#5ec8f8"
O_COLOR = "#f87272"
WIN_COLOR = "#f7d774"
TEXT_COLOR = "#e6e6f0"
MUTED_COLOR = "#9a9ab0"

# Delay, in milliseconds, before the AI's move is applied after the human's
# turn ends. The move itself is computed instantly; this delay is purely a
# UX touch so the AI doesn't feel like it's snapping the board shut.
AI_MOVE_DELAY_MS = 400


class TicTacToeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.board = new_board()
        self.current_player = "X"
        self.game_over = False
        self.ai_thinking = False

        self.mode = tk.StringVar(value="two_player")  # "two_player" or "vs_ai"
        self.human_mark = tk.StringVar(value="X")      # only used in vs_ai mode

        self.scores_two_player = {"X": 0, "O": 0, "draws": 0}
        self.scores_vs_ai = {"human": 0, "ai": 0, "draws": 0}

        self.mark_font = tkfont.Font(family="Helvetica", size=36, weight="bold")
        self.status_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.score_font = tkfont.Font(family="Helvetica", size=11)
        self.mode_font = tkfont.Font(family="Helvetica", size=10, weight="bold")

        self._build_layout()
        self._update_status()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(padx=16, pady=(16, 8), fill="x")

        self.status_label = tk.Label(
            header, text="", font=self.status_font, bg=BG, fg=TEXT_COLOR
        )
        self.status_label.pack()

        mode_frame = tk.Frame(self.root, bg=BG)
        mode_frame.pack(padx=16, pady=(0, 4), fill="x")

        self._radio(
            mode_frame, "Two player", self.mode, "two_player", self._on_mode_change
        ).pack(side="left", expand=True)
        self._radio(
            mode_frame, "Vs AI", self.mode, "vs_ai", self._on_mode_change
        ).pack(side="left", expand=True)

        self.mark_frame = tk.Frame(self.root, bg=BG)
        self.mark_frame.pack(padx=16, pady=(0, 8), fill="x")

        tk.Label(
            self.mark_frame, text="You play:", font=self.score_font, bg=BG, fg=MUTED_COLOR
        ).pack(side="left", padx=(0, 8))
        self._radio(
            self.mark_frame, "X (first)", self.human_mark, "X", self._on_mode_change
        ).pack(side="left", expand=True)
        self._radio(
            self.mark_frame, "O (second)", self.human_mark, "O", self._on_mode_change
        ).pack(side="left", expand=True)
        self.mark_frame.pack_forget()  # hidden until "Vs AI" is selected

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

    def _radio(self, parent, text, variable, value, command):
        return tk.Radiobutton(
            parent,
            text=text,
            variable=variable,
            value=value,
            command=command,
            font=self.mode_font,
            bg=BG,
            fg=TEXT_COLOR,
            selectcolor=CELL_BG,
            activebackground=BG,
            activeforeground=TEXT_COLOR,
            highlightthickness=0,
            bd=0,
        )

    # ------------------------------------------------------------------
    # Mode handling
    # ------------------------------------------------------------------

    @property
    def ai_mark(self):
        return other_mark(self.human_mark.get())

    def _on_mode_change(self):
        if self.mode.get() == "vs_ai":
            self.mark_frame.pack(padx=16, pady=(0, 8), fill="x", before=self._grid_frame())
        else:
            self.mark_frame.pack_forget()
        self._update_score_label()
        self.reset_board()

    def _grid_frame(self):
        # The grid frame is the widget packed right after mark_frame's slot;
        # buttons[0]'s parent is exactly that frame.
        return self.buttons[0].master

    # ------------------------------------------------------------------
    # Gameplay
    # ------------------------------------------------------------------

    def on_cell_click(self, index):
        if self.game_over or self.ai_thinking:
            return
        if self.mode.get() == "vs_ai" and self.current_player != self.human_mark.get():
            return  # it's the AI's turn; ignore stray human clicks
        if not make_move(self.board, index, self.current_player):
            return

        self._render_cell(index)
        just_played = self.current_player

        if self._finish_turn_if_over(just_played):
            return

        self._switch_turn()

        if self.mode.get() == "vs_ai" and self.current_player == self.ai_mark:
            self._schedule_ai_move()
        else:
            self._update_status()

    def _schedule_ai_move(self):
        self.ai_thinking = True
        self._update_status(thinking=True)
        self.root.after(AI_MOVE_DELAY_MS, self._make_ai_move)

    def _make_ai_move(self):
        self.ai_thinking = False
        if self.game_over:
            return
        move = best_ai_move(self.board, self.ai_mark)
        if move is None:
            return
        make_move(self.board, move, self.ai_mark)
        self._render_cell(move)

        if self._finish_turn_if_over(self.ai_mark):
            return

        self._switch_turn()
        self._update_status()

    def _finish_turn_if_over(self, mark_just_played):
        """If the game ended on this move, update state/score/status and
        return True. Otherwise return False and change nothing."""
        result = check_winner(self.board)
        if result is not None:
            winner, line = result
            self.game_over = True
            self._record_result(winner=winner)
            self._highlight_line(line)
            self._update_status(winner=winner)
            self._update_score_label()
            return True

        if is_draw(self.board):
            self.game_over = True
            self._record_result(draw=True)
            self._update_status(draw=True)
            self._update_score_label()
            return True

        return False

    def _record_result(self, winner=None, draw=False):
        if self.mode.get() == "two_player":
            if draw:
                self.scores_two_player["draws"] += 1
            else:
                self.scores_two_player[winner] += 1
        else:
            if draw:
                self.scores_vs_ai["draws"] += 1
            elif winner == self.human_mark.get():
                self.scores_vs_ai["human"] += 1
            else:
                self.scores_vs_ai["ai"] += 1

    def _switch_turn(self):
        self.current_player = other_mark(self.current_player)

    def _render_cell(self, index):
        mark = self.board[index]
        color = X_COLOR if mark == "X" else O_COLOR
        self.buttons[index].config(text=mark, fg=color, state="disabled", disabledforeground=color)

    def _highlight_line(self, line):
        for idx in line:
            self.buttons[idx].config(bg=WIN_COLOR, fg=BG, disabledforeground=BG)

    def _update_status(self, winner=None, draw=False, thinking=False):
        if winner:
            if self.mode.get() == "vs_ai":
                who = "You" if winner == self.human_mark.get() else "The AI"
                self.status_label.config(text=f"{who} won!")
            else:
                self.status_label.config(text=f"Player {winner} wins!")
        elif draw:
            self.status_label.config(text="It's a draw!")
        elif thinking:
            self.status_label.config(text="AI is thinking...")
        else:
            if self.mode.get() == "vs_ai":
                turn = "Your" if self.current_player == self.human_mark.get() else "AI's"
                self.status_label.config(text=f"{turn} turn ({self.current_player})")
            else:
                self.status_label.config(text=f"Player {self.current_player}'s turn")

    def _update_score_label(self):
        if self.mode.get() == "two_player":
            s = self.scores_two_player
            text = f"X wins: {s['X']}    O wins: {s['O']}    Draws: {s['draws']}"
        else:
            s = self.scores_vs_ai
            text = f"You: {s['human']}    AI: {s['ai']}    Draws: {s['draws']}"
        self.score_label.config(text=text)

    def reset_board(self):
        self.board = new_board()
        self.current_player = "X"
        self.game_over = False
        self.ai_thinking = False
        for btn in self.buttons:
            btn.config(
                text="",
                bg=CELL_BG,
                fg=TEXT_COLOR,
                state="normal",
                disabledforeground=TEXT_COLOR,
            )
        self._update_status()

        if self.mode.get() == "vs_ai" and self.current_player == self.ai_mark:
            self._schedule_ai_move()


def main():
    root = tk.Tk()
    TicTacToeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
