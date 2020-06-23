## Chess_AI
a basic chess AI complete with a chess engine (both convolutional neural network based or conventional), a server, and a front end UI.
The engine uses the famous Negamax algorithm with alpha-beta pruning, iterative deepening, and a transposition table to speed up the search process.
The leaf static positions are evaluated either by conventional ideas such as piece values/positions on the board, or by a CNN, trained on thousands of positions by the strongest players in the world.


## Installation and Usage:
Make sure to have Flask, python-chess, and Tensorflow 2.0 installed.

The entire program can be run with 
```bash
python server.py
```
As shown in the example below, the user can choose to play the computer or another human. The type of engine, depth, and
response type can all be adjusted at the bottom. Additionally, one can play from any position by entering the FEN at the bottom of the page. The
move order is displayed on the terminal; working on displaying it to the UI.


<img width="1379" alt="chess_AI_ex" src="https://user-images.githubusercontent.com/29835953/83353666-bf775480-a319-11ea-9108-5ef2c09a6959.png">


**as of June 23rd, 2020:**  
Code is a still rough draft, yet is a fully functioning engine and UI. The CNN is trained and technically works but does not output optimal moves. I am attempting to shift focus to Reinforcement learning as well.
The conventional engine works and has on occasion beat me. 


## Authors
Yonah Taurog

## Acknowledgments
- chessboard.js
- chess.js
- anytree
