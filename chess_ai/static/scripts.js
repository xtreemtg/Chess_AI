
var board = null;
var game = new Chess();
var $status = $('#status');
var $fen = $('#fen');
var $pgn = $('#pgn');


function makeRandomMove () {
  var possibleMoves = game.moves();

  // game over
  if (possibleMoves.length === 0) return;

  var randomIdx = Math.floor(Math.random() * possibleMoves.length);
  game.move(possibleMoves[randomIdx]);
  board.position(game.fen())
}

function makeComputerMove() {
  b = game.moves();
  fen = game.fen();
  var e = document.getElementById("depth");
  var depth = e.options[e.selectedIndex].value;
  $.post("/best_move", {'fen': fen, 'depth': depth}).done(function (data) {
    console.log(data);
    game.move(data);
    board.position(game.fen())
  })
}

var takeBack = function() {
    game.undo();
    if (game.turn() != "w") {
        game.undo();
    }
    board.position(game.fen());
};

var newGame = function() {
    game.reset();
    board.start();
};

function _selfRandomPlay () {
  var possibleMoves = game.moves();

  // exit if the game is over
  if (game.game_over()) return;

  var randomIdx = Math.floor(Math.random() * possibleMoves.length);
  game.move(possibleMoves[randomIdx]);
  board.position(game.fen());

  window.setTimeout(_selfRandomPlay, 300)
}
var selfRandomPlay = function() {
  window.setTimeout(_selfRandomPlay, 300)
};

function onDragStart (source, piece, position, orientation) {
  // do not pick up pieces if the game is over
  if (game.game_over()) return false;

  // only pick up pieces for the side to move
  if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
      (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
    return false
  }
}

function onDrop (source, target) {
  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  });

  // illegal move
  if (move === null) return 'snapback';

  var e = document.getElementById("responseType");
  var type = e.options[e.selectedIndex].value;
  // make random legal move for black
  if (type === 'R') window.setTimeout(makeRandomMove, 250);
  else if(type === 'C') makeComputerMove();
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
  board.position(game.fen())
}

function updateStatus () {
  var status = '';

  var moveColor = 'White';
  if (game.turn() === 'b') {
    moveColor = 'Black'
  }

  // checkmate?
  if (game.in_checkmate()) {
    status = 'Game over, ' + moveColor + ' is in checkmate.'
  }

  // draw?
  else if (game.in_draw()) {
    status = 'Game over, drawn position'
  }

  // game still on
  else {
    status = moveColor + ' to move';

    // check?
    if (game.in_check()) {
      status += ', ' + moveColor + ' is in check'
    }
  }

  $status.html(status);
  $fen.html(game.fen());
  $pgn.html(game.pgn())
}

var testButton = function () {
  console.log('testing!');
  //debugger;
  $.get("/test", function (data) {
     console.log(data);
  });
  console.log(game.fen());
};

var config = {
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd
};
board = Chessboard('myBoard', config);

