Scrabble
========

There is two options to run the program with:
(1) with GUI: not designed for playing a complete game, because it will stuck until
    the game is over, which takes in non greedy agents about 30-40 minutes.
    to play the game turn by turn, you can enjoy using our humble GUI.
    Run the program with:
        % python3 Scrabble.py GUI

(2) without GUI: designed for playing a complete game, just prints the board in
    a suitable way for human viewing. Uses colors to highlight various squares.
    Run the program with:
        % python3 Scrabble.py

    then a menu will appear, and the program waits user input:

    choose your strategy: 1, 2 or 3
    (1) Greedy strategy.
    (2) MCTS strategy.
    (3) MiniMax strategy.

    choose the strategy and press enter, a complete game will be played, with printing
    every step results and board state.
