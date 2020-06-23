var board = null;
var $board = $('#myBoard');
var game = new Chess();
var $status = $('#status');
var $current_fen = $('#current_fen');
var $pgn = $('#pgn');
var squareToHighlight = null;
var squareClass = 'square-55d63';


function makeRandomMove () {
  var possibleMoves = game.moves();

  // game over
  if (possibleMoves.length === 0) return;

  var randomIdx = Math.floor(Math.random() * possibleMoves.length);
  var move = possibleMoves[randomIdx];
  game.move(move);
  board.position(game.fen());
  debugger;
  $.get('/move/' + move);
}
function computerMoveBtn() {
  let e = document.getElementById("depth");
  let depth = e.options[e.selectedIndex].value;
  let timeout = depth === '1' || depth === '2' ? 50 : 10;
  window.setTimeout(makeComputerMove, timeout, depth);
}

function makeComputerMove(depth) {
  let fen = game.fen();
  let e = document.getElementById("engineControl");
  e = e.options[e.selectedIndex].value;
  let e2 = document.getElementById("engineType");
  e2 = e2.options[e2.selectedIndex].value;
  //send move to server, get back a move
  $.post("/best_move", {'fen': fen, 'depth': depth, 'verbose': e, 'type': e2}).done(function (data) {
    console.log(data);
    let turn = game.turn();
    let move = game.move(data['move']);
    updateStatus();
    board.position(game.fen());
    removeHighlights(turn);
    $board.find('.square-' + move.from).addClass('highlight-'+turn);
    squareToHighlight = move.to;
    if (game.game_over()) alertGameOverStatus();

  });
}

var setFen = function (new_fen) {
 console.log(game.fen());
 console.log(new_fen);
 let loaded = game.load(new_fen);
 if(loaded) {
   updateStatus();
   board.position(new_fen);
   $.get('/load_fen/' + new_fen)
 } else {
   alert('Invalid FEN!')
 }
};

var alertGameOverStatus = function () {
  let GAMEOVER = 'Game Over! ';
  let msg = '';
  if (game.in_checkmate()){
    loser = game.turn() === 'b' ? "Black" : "White";
    msg = loser + ' is in checkmate!'
  } else if(game.in_stalemate()){
    msg = loser + ' is in stalemate!'
  } else if (game.in_threefold_repetition()){
    msg = 'Draw by Threefold Repetition!'
  } else if (game.insufficient_material()){
    msg = 'Draw by Insufficient Material!'
  } else {
      msg = "Draw by 50 move rule!"
  }
  $('#game_over_dialog').dialog({
    modal: true,
    title: GAMEOVER,
    open: function() {$(this).html(msg);},
    buttons: {OK: function() {$( this ).dialog( "close" );}}
  });
};

var takeBack = function() {
  if (game.history().length > 0) {
    $.get('/takeback').done(() => {
      game.undo();
      if (game.turn() != "w") {
        game.undo();
      }
      updateStatus();
      board.position(game.fen());

    });
  } else alert('No more moves to take back!')


};

var newGame = function() {

    game.reset();
    board.start();
    updateStatus();
    removeHighlights('w');
    //removeHighlights('b');
    $.get('/reset')
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

function promotion(){
  return new Promise(resolve => {
    $('#dialog').show();
  $('#dialog').dialog({modal: true, closeText: "hide", buttons: {Okay: function() {$(this).dialog("close");}
               }}).on('dialogclose', function(event) {
                 var e = document.getElementById("promotion");
                  e = e.options[e.selectedIndex].value;
                  console.log(e);
                  resolve(e);
                  })
  } )
  //  $('#dialog').show();
  //     console.log('coo');
  // $('#dialog').dialog({modal: true, closeText: "hide", buttons: {Okay: function() {$(this).dialog("close");}}});
  // let e = document.getElementById("promotion");
  // e = e.options[e.selectedIndex].value;
  // return e
}


function onDrop (source, target, piece) {
  if ((piece === 'wP' && target.slice(-1) === '8') || (piece === 'bP' && target.slice(-1) === '1')) {
    console.log(target.slice(-1));
    let temp = Chess(game.fen());
    let move = temp.move({
      from: source,
      to: target,
      promotion: 'q'
    });
    if (move === null) return 'snapback';
    else {
      console.log('trying to promote');
      promotion().then(result =>{
         console.log(result);
         return onDropContinuation(source, target, piece, result, true)
      });
      // let p = promotion();
      // return onDropContinuation(source, target, piece, p, true);


    }

  } else {
    return onDropContinuation(source, target, piece, '', false);
  }
}

function onDropContinuation(source, target, piece, promotion, isascync){
  var move = game.move({
    from: source,
    to: target,
    promotion: promotion // NOTE: always promote to a queen for example simplicity
  });
  if (isascync) board.position(game.fen());


  // illegal move
  if (move === null) return 'snapback';

  let turn = game.turn() === 'b' ? 'w': 'b';
  updateStatus();


  removeHighlights(turn);
  $board.find('.square-' + source).addClass('highlight-' + turn);
  $board.find('.square-' + target).addClass('highlight-' + turn);

  $.get('/move/' + move['san']);
  if (!game.game_over()) {



    var e = document.getElementById("responseType");
    var type = e.options[e.selectedIndex].value;
    // make random legal move for black
    if (type === 'R') window.setTimeout(makeRandomMove, 50);
    else if (type === 'C') {
      var e2 = document.getElementById("depth");
      var depth = e2.options[e2.selectedIndex].value;
      let timeout = depth === '1' || depth === '2' ? 50 : 10;
      window.setTimeout(makeComputerMove, timeout, depth);
    }
  } else{
    alertGameOverStatus();
  }

}


var createTable = function() {
  $('#moveTable2 tr').not(':first').remove();
    let hist = game.history();
    var html = '';
    for (var i = 0; i < hist.length; i+=2) {
      let a = hist[i]? hist[i]: '';
      let b = hist[i + 1] ? hist[i + 1] : '';
                html += '<tr><td>' + (i / 2 + 1).toString() +'.' + '</td><td>'
                + a + '</td><td>'
                + b + '</td></tr>';

    }

    $('#moveTable2 tr').first().after(html);
};


// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
  board.position(game.fen())
}

function updateStatus () {
  var status = '';

  var moveColor = game.turn() === 'b' ? 'Black' :'White';

  // checkmate?
  if (game.game_over()) {
    if (game.in_checkmate()) {
      let score = moveColor === 'Black'? '1-0' : '0-1';

      status = 'Game over! ' + score
    } else if (game.in_draw()) {
      //
      // if (game.in_stalemate()) {
      //   status = "<b>Game over!</b><br>" + moveColor + "is in stalemate!"
      status = 'Game over! 1/2 - 1/2'
      }
  }

  else {
    status = moveColor + ' to move';

    // check?
    if (game.in_check()) {
      status += ', ' +'<br><b>'+ moveColor + ' is in check' + '</b>'
    }
  }
  createTable();


  $status.html(status);
  $current_fen.html(game.fen());
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

function onMoveEnd () {
  let turn = game.turn() === 'b' ? 'w': 'b';
  $board.find('.square-' + squareToHighlight)
    .addClass('highlight-' + turn)
}

function removeHighlights (color) {
  $board.find('.' + squareClass)
    .removeClass('highlight-' + color)
}

function addPieces() {
  board.sparePieces = board.sparePieces ? false : true
}

var config = {
  draggable: true,
  sparePieces: false,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
  onMoveEnd: onMoveEnd
};


board = Chessboard('myBoard', config);

newGame();

$('#dialog').hide();
$('#game_over_dialog').hide();
$('#target').click(function() {

});
$('#flipOrientationBtn').on('click', board.flip);
// $('#addPieces').on('click', board.flip);
