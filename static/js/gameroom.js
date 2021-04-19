(function() {

const roomName = JSON.parse(document.getElementById('room-name').textContent);

const gameSocket = new WebSocket(
   `ws://${window.location.host}/game/${roomName}/`
);

gameSocket.onmessage = function(e) {
   const data = JSON.parse(e.data);
    console.log(data)

   const gameboard = Object.keys(data.gameboard).sort().map(item => data.gameboard[item]);

   console.log(gameboard);

};

gameSocket.onclose = function(e) {
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
   gameSocket.send(JSON.stringify({
      'message': message
   }));
   messageInputDom.value = '';
};

})();
