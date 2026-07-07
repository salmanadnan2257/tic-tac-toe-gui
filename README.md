# Tic Tac Toe (tkinter GUI)

A two-player Tic Tac Toe game with a real graphical interface, built with tkinter.
Click cells on a 3x3 grid to play; the game tracks wins, losses, and draws across
rounds without closing the window.

## Why it exists

Originally a "Day 83" console-only practice script that just printed a numbered
board and read `input()`. It also had a real bug: the win check only ever tested
for player X, so O could complete a full line and the game would keep running as
if nothing happened. This rewrite keeps the original goal (represent a 3x3 board,
detect a win across all eight lines without a library) but fixes the bug properly
and replaces the terminal loop with an actual tkinter window, so the folder name
finally matches what the program does.

## Features

- Two-player hot-seat play on a clickable 3x3 grid of buttons.
- Win detection across all 8 lines (3 rows, 3 columns, 2 diagonals) for **both**
  X and O, plus draw detection when the board fills with no winner.
- The winning line is highlighted in place on the board when a game ends.
- A status label shows whose turn it is, and the result when a round ends.
- A "Play again" button resets the board without closing the window.
- A running score tracker (X wins / O wins / draws) that persists across rounds
  in the same session.

## Architecture

Two files:

- `game.py`: pure game logic, no tkinter, no I/O. A flat 9-cell list represents
  the board. `check_winner` compares both marks against all 8 win lines and
  returns the winner and the winning line; `is_draw` checks for a full board
  with no winner; `make_move` applies a move if the target cell is empty.
  Because this module has no GUI dependency, its win/draw logic can be (and is)
  unit tested directly.
- `main.py`: the tkinter GUI. Builds the window, the 3x3 button grid, the status
  label, score label, and "Play again" button, and wires button clicks to the
  functions in `game.py`. It holds only display state (colors, labels, the
  running score dict); it does not duplicate any win/draw logic.

## Setup

No dependencies beyond the Python standard library. tkinter ships with the
standard CPython installer on Windows and macOS; on some Linux distributions
it is a separate package (e.g. `sudo apt install python3-tk` on Debian/Ubuntu).
Requires Python 3.6 or newer (the code uses f-strings).

```bash
cd tic-tac-toe-gui
python3 main.py
```

No environment variables are read by this project, so no `.env.example` is included.

## Usage

Run `python3 main.py` to open the game window. Player 1 is X, Player 2 is O.
Click any empty cell to place your mark; the status label at the top shows
whose turn it is. When a player completes a line, the three winning cells are
highlighted and the status label announces the winner. If all 9 cells fill
with no line completed, the status label announces a draw. Either way, the
score line at the bottom updates and the "Play again" button clears the board
for another round without closing the window.

## Challenges

- **Fixing the win-check bug without breaking the original logic shape.** The
  console version hardcoded 8 `or`-chained comparisons, all against `" X "`.
  Rather than duplicating that 8 times for O, `check_winner` loops over a list
  of the 8 index triples (`WIN_LINES`) and checks whether all three cells match
  a non-empty mark, which handles X and O with one code path.
- **Keeping `game.py` free of any tkinter dependency.** The temptation with a
  small game like this is to check `board[i]` for wins directly inside the
  button click handler. Splitting the logic out means the button handler in
  `main.py` is just "make the move, ask game.py what happened, update the
  display," and the actual rules can be unit tested without spinning up a
  window.
- **Disabling cells after they're filled without visually flattening the mark
  color.** tkinter's default disabled state grays out button text, which would
  make X and O both look the same shade of gray once placed. Using
  `disabledforeground` explicitly keeps the mark's real color after the cell
  is disabled.

## What I learned

- Separating pure logic from the widget layer makes a GUI's core rules testable
  without a display; the game logic tests in this project run in isolation and
  don't touch tkinter at all.
- A bug like "only checks for X" is easy to miss when it's spelled out as 8
  near-identical lines of `or`-chained conditions; looping over a data
  structure of win lines instead makes the symmetry (and the gap) obvious.

## What I'd do differently

- Add keyboard support (arrow keys plus Enter/Space to place a mark) so the
  game doesn't require a mouse.
- Persist the running score to a file so it survives closing and reopening the
  window, instead of resetting each time the app starts.
- Add a simple AI opponent (even just "play a random empty cell") for
  single-player mode, since right now it's hot-seat only.
