(function() {

const requestingUser = JSON.parse(document.getElementById('requesting_user').textContent);

var ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
console.log( `${ws_scheme}${window.location.host}/lobby/${requestingUser}` )
const userSocket = new WebSocket(
  `${ws_scheme}${window.location.host}/lobby/${requestingUser}`
);

userSocket.onmessage = function(e) {
  document.querySelector('#available-games').value = "";
  const data = JSON.parse(e.data);
  for( i in data) {
    document.querySelector('#available-games').value += (data[i] + '\n');
  }
};

userSocket.onclose = function(e) {
  console.error('Game socket closed unexpectedly');
};


document.querySelector('#game-name-input').focus();
document.querySelector('#game-name-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#game-name-submit').click();
    }
};

document.querySelector('#game-name-submit').onclick = function(e) {
    var roomName = document.querySelector('#game-name-input').value;
    window.location.pathname = '/game/' + roomName + '/';
};

})();
