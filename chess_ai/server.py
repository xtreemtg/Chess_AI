from flask import Flask, request, render_template
from timeit import default_timer as timer
import traceback
import json
from chess_engine import ChessEngine

engine = ChessEngine()
app = Flask(__name__)


@app.route("/")
def landing():
    return render_template("index.html")


@app.route("/best_move", methods=['POST'])
def best_move():
    global engine
    fen = request.form.get('fen', default=None)
    depth = request.form.get('depth', default=2)
    verbose = request.form.get('verbose', default=None)
    type = request.form.get('type', default=False)
    type = True if type == 'n' else False
    #move = request.form.get('move', default=None)
    if fen and depth:
        depth = int(depth)
        #engine.move(move)
        start = timer()
        data = engine.computer_move(depth, verbose, depth_to_sort=1, nn=type)
        stop = timer()
        print(stop - start, 'seconds')
        print(data)
        return data, '200'


@app.route("/reset")
def reset():
    engine.reset()
    return '200'


@app.route("/takeback")
def takeback():
    engine.take_back()
    return '200'


@app.route("/move/<path:move>")
def update_move(move):
    engine.move(move)
    return '200'

@app.route("/load_fen/<path:fen>")
def load_fen(fen):
    engine.reset(fen)
    return '200'


@app.route("/test")
def test():
    print('testing')
    return 'Works'


if __name__ == "__main__":
    app.run(debug=True)
