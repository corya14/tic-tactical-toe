(function() {

const gameName = JSON.parse(document.getElementById('game-name').textContent);
const requestingUser = JSON.parse(document.getElementById('requesting_user').textContent);

var ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
console.log( `${ws_scheme}${window.location.host}/${gameName}/${requestingUser}/room` )
const userSocket = new WebSocket(
   `${ws_scheme}${window.location.host}/${gameName}/${requestingUser}/room`
);

userSocket.onmessage = function(e) {
   console.log(e.data)
   const data = JSON.parse(e.data);
   const player1 = data.player1
   document.querySelector('#player1').innerHTML = player1
   const player2 = data.player2
   document.querySelector('#player2').innerHTML = player2
   const current_turn = data.current_turn
   const cur_turn_ele = `#${current_turn}`
   document.querySelector('#player1').style.backgroundColor = ''
   document.querySelector('#player2').style.backgroundColor = ''
   document.querySelector(cur_turn_ele).style.backgroundColor = 'yellow'

   const gamelogs = data.log
   document.querySelector('#game-log').value = ''
   for (i in gamelogs) {
      document.querySelector('#game-log').value += (gamelogs[i] + '\n');
   }
};

userSocket.onclose = function(e) {
   console.error('Game socket closed unexpectedly');
};

document.querySelector('#game-message-input').focus();
document.querySelector('#game-message-input').onkeyup = function(e) {
   if (e.keyCode === 13) {  // enter, return
      document.querySelector('#game-message-submit').click();
   }
};

document.querySelector('#game-message-submit').onclick = function(e) {
   const numTacks = document.querySelector('#game-message-input').value;
   const srcSquare = document.querySelector('#origin-square').value
   const dstSquare = document.querySelector('#dest-square').value
   const move = `(${numTacks})|(${srcSquare},${dstSquare})`;
   userSocket.send(JSON.stringify({
      'game': gameName,
      'move': move
   }));
};

})();
