(function() {

const roomName = JSON.parse(document.getElementById('room-name').textContent);
const requestingUser = JSON.parse(document.getElementById('requesting_user').textContent);

var ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
const userSocket = new WebSocket(
   `${ws_scheme}${window.location.host}/user/${requestingUser}/`
);

userSocket.onmessage = function(e) {
   const data = JSON.parse(e.data);
   const gameboard = Object.keys(data.gameboard).sort().map(item => data.gameboard[item]);
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
   const messageInputDom = document.querySelector('#game-message-input');
   const message = messageInputDom.value;
   userSocket.send(JSON.stringify({
      'message': message
   }));
   messageInputDom.value = '';
};

})();
