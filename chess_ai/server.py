from flask import Flask,  request, render_template
import chess
import chess.svg
import traceback
from chess_engine import Chess_Engine

#engine= Chess_Engine()
app = Flask(__name__)
verbose = True


@app.route("/")
def landing():
    return render_template("index.html")

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

@app.route("/test")
def test():
    print('testing')
    return 'Works'

if __name__ == "__main__":
    app.run(debug=True)
