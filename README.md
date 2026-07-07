# Tic Tac Toe (tkinter GUI)

A Tic Tac Toe game with a real graphical interface, built with tkinter. Play
two-player hot-seat, or switch to single-player against a minimax AI opponent
that is provably unbeatable. Click cells on a 3x3 grid to play; the game
tracks wins, losses, and draws across rounds without closing the window.

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
- A single-player mode against a minimax AI opponent. Pick whether you play X
  (first) or O (second); the AI replies automatically after a short, deliberate
  delay so it doesn't feel instantaneous. The AI is unbeatable: it always wins
  or draws, never loses. This is verified, not just claimed; see Verification
  below for the actual numbers.
- Win detection across all 8 lines (3 rows, 3 columns, 2 diagonals) for **both**
  X and O, plus draw detection when the board fills with no winner.
- The winning line is highlighted in place on the board when a game ends.
- A status label shows whose turn it is, and the result when a round ends.
- A "Play again" button resets the board without closing the window.
- A running score tracker, kept separately for each mode: X wins / O wins /
  draws in two-player mode, and your wins / AI wins / draws in AI mode, both
  persisting across rounds in the same session.

## Architecture

Two files, plus a `tests/` folder:

- `game.py`: pure game logic and the AI, no tkinter, no I/O. A flat 9-cell list
  represents the board. `check_winner` compares both marks against all 8 win
  lines and returns the winner and the winning line; `is_draw` checks for a
  full board with no winner; `make_move` applies a move if the target cell is
  empty. `minimax` searches the full remaining game tree (with alpha-beta
  pruning) to score every possible outcome from the AI's perspective, and
  `best_ai_move` wraps it into a single "give me a board, get back a move"
  call the GUI can use without knowing anything about the search itself.
  Because this module has no GUI dependency, its win/draw logic and its AI
  can both be (and are) unit tested directly.
- `main.py`: the tkinter GUI. Builds the window, the 3x3 button grid, the mode
  toggle (two player / vs AI), the mark-choice control, the status label,
  score label, and "Play again" button, and wires clicks (and the AI's
  scheduled move) to the functions in `game.py`. It holds only display state
  (colors, labels, the running score dicts, which mode is active); it does not
  duplicate any win/draw/AI logic.
- `tests/`: `test_ai.py` unit-tests specific AI decisions (blocking a threat,
  taking a win, the empty-board opening); `verify_unbeatable.py` is a
  standalone script that plays out hundreds of full games to prove the AI
  never loses.

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

Run `python3 main.py` to open the game window. Two radio buttons at the top
switch between **Two player** and **Vs AI**. In two-player mode, Player 1 is
X, Player 2 is O, and you take turns clicking. In Vs AI mode, a second row
lets you choose whether you play X (first) or O (second); after your move the
AI replies automatically (there's a short, deliberate pause before it moves,
long enough to see it happen but not so long it feels laggy). Click any empty
cell to place your mark; the status label at the top shows whose turn it is
(or "AI is thinking..." during the AI's short pause). When a player completes
a line, the three winning cells are highlighted and the status label
announces the winner. If all 9 cells fill with no line completed, the status
label announces a draw. Either way, the score line at the bottom updates for
the current mode, and the "Play again" button clears the board for another
round without closing the window.

## Verification

The AI is built on minimax, which searches the entire remaining game tree
before choosing a move, so "unbeatable" is a specific, checkable claim, not
marketing language. `tests/verify_unbeatable.py` checks it three ways, each
run with the human moving first and with the AI moving first:

- **Exhaustive search over every human move sequence** (a complete
  enumeration, not a sample): 569 distinct games when the human moves first,
  73 when the AI moves first. The AI lost 0 of them.
- **1000 games per starting order with the human playing uniformly random
  legal moves.** Human-first: AI won 789, drew 211, lost 0. AI-first: AI won
  996, drew 4, lost 0.
- **Both sides playing optimally** (the human side also runs minimax): both
  starting orders end in a draw, which is the game-theoretically correct
  result for perfect play on both sides.

Run it yourself with `python3 tests/verify_unbeatable.py`. Six unit tests in
`tests/test_ai.py` cover specific tactical situations directly (taking an
immediate win, blocking an immediate threat, preferring a win over a block
when both exist, the empty-board opening); run them with
`python3 -m unittest discover -s tests`.

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
- **Drawing the all-8-win-lines diagram for the explainer PDFs.** My first
  attempt tried to overlay all eight winning lines on one board using
  hardcoded pixel coordinates, and the diagonal lines came out shifted and
  overlapping the row lines because the coordinate math didn't account for
  the board's flipped y-axis. I rebuilt it as eight small side-by-side boards
  (one per line, grouped rows/columns/diagonals) instead of forcing everything
  onto a single board, which was easier to get right and easier to read.
- **Explaining alpha-beta pruning without overstating what it does.** It's
  tempting to describe pruning as part of "why the AI is unbeatable," but
  that's wrong: the unbeatability comes entirely from exhaustive minimax
  search, and pruning only cuts down how much of that already-decided tree
  gets visited. It took a couple of rewrites of that section in the deep dive
  to keep the two claims separate: minimax alone is correct even with
  pruning removed, and pruning alone would speed up a broken search just as
  happily as a correct one. Conflating them would have quietly overstated
  what the optimization actually contributes.

## What I learned

- Separating pure logic from the widget layer makes a GUI's core rules testable
  without a display; the game logic tests in this project run in isolation and
  don't touch tkinter at all.
- A bug like "only checks for X" is easy to miss when it's spelled out as 8
  near-identical lines of `or`-chained conditions; looping over a data
  structure of win lines instead makes the symmetry (and the gap) obvious.
- A claim like "unbeatable" is only worth writing down if there's a check
  behind it that would actually catch the claim being false. Random-play
  simulation alone can't do that (it can only fail to find a counterexample,
  never rule one out); an exhaustive search over every human move sequence
  can, because it doesn't sample, it enumerates.

## What I'd do differently

- Add keyboard support (arrow keys plus Enter/Space to place a mark) so the
  game doesn't require a mouse.
- Persist the running score to a file so it survives closing and reopening the
  window, instead of resetting each time the app starts.
- Add a difficulty setting that lets the AI occasionally play a suboptimal
  move on purpose, since a perfect opponent that can never be beaten is
  arguably less fun for a casual player than one that's merely very good.
