from flask import Flask, Response, request, render_template, flash
import time
import base64
import chess
import chess.svg
import traceback
from chess_engine import Chess_Engine

#engine= Chess_Engine()
app = Flask(__name__)
verbose = True


def to_svg():
    return base64.b64encode(chess.svg.board(board = engine.board).encode('utf-8')).decode('utf-8')

@app.route("/")
def landing():
    return render_template("index.html")
    # string = "<html><head>"
    # string += "<style>input {font-size: 30px;} button {font-size: 30px;}</style>"
    # string += '</head><body><img width = 600 height = 600 src="/board.svg?%f"></img><br/>'
    # string += '<form action = "/move"><input name = "move" type = "text"></input>'
    # string += '<input type = "submit" value = "Move"></form><br/>'
    # return string


@app.route("/board.svg")
def board():
    return Response(chess.svg.board(board=engine.board), mimetype='image/svg+xml')

@app.route("/best_move", methods=['POST'])
def best_move():
    fen = request.form.get('fen', default=None)
    depth = request.form.get('depth', default=2)

    if fen and depth:
        depth = int(depth)
        engine = Chess_Engine(fen)
        best = engine.computer_move(depth, verbose)
        return best


@app.route("/move")
def move():
    if not engine.is_game_over():
        move = request.args.get('move', default='')
        if move and move != '':
            print('human move', move)
            try:
                engine.push_san(move)
                if not engine.is_game_over():
                    engine.computer_move()
                else:
                    print('engine over!')
            except Exception:
                traceback.print_exc()
    else:
        print('engine over!')
    return landing()

@app.route("/self_play")
def self_play():
    if engine.is_game_over():
        engine.reset()
    ret = '<html><head>'
    while not engine.is_game_over():
        engine.computer_move(verbose=True)
        ret += '<img width=600 height=600 src="data:image/svg+xml;base64,%s"></img><br/>' % to_svg()
    return ret

@app.route("/test")
def test():
    print('testing')
    return 'Works'
# @app.route("/random_move")
# def random_move():
#     random_move()
#     return ''

if __name__ == "__main__":
    app.run(debug=True)
