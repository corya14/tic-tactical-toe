(function() {

  const roomName = JSON.parse(document.getElementById('room-name').textContent);
  const requestingUser = JSON.parse(document.getElementById('requesting_user').textContent);


  // "..." deconstructs to create a copy of the array
  const getGameboardRow = (array, index) => [...array].splice(index, 5);

  const Gameboard = () => {

    const [gameboard, setGameboard] = React.useState();
    // example: https://stackoverflow.com/questions/58432076/websockets-with-functional-components
    const webSocket = React.useRef(null);


    React.useEffect(() => {
      var ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
      webSocket.current = new WebSocket(
        `${ws_scheme}${window.location.host}/user/${requestingUser}/`
      );

        webSocket.current.onmessage = function(e) {
          const data = JSON.parse(e.data);
          setGameboard(Object.keys(data.gameboard).sort().map(item => data.gameboard[item]));
        };

      webSocket.current.onclose = function(e) {
        console.error('Game socket closed unexpectedly');
      } ;

      return () => webSocket.current.close();

    }, [])


    if (!gameboard) return <div className="loading">Loading...</div>


    const rows = [getGameboardRow(gameboard, 0), getGameboardRow(gameboard, 5), getGameboardRow(gameboard, 10), getGameboardRow(gameboard, 15), getGameboardRow(gameboard, 20)];


    return <table id="gameboard-table">
    <tr id="row-0">
      <th id="0-header"><strong>#</strong></th>
      <th id="0a"><strong>a</strong></th>
      <th id="0b"><strong>b</strong></th>
      <th id="0c"><strong>c</strong></th>
      <th id="0d"><strong>d</strong></th>
      <th id="0e"><strong>e</strong></th>
    </tr>
    {rows.map((row, index) => {
      return (<tr key={index} id={`row-${index + 1}`}>
        <td><strong>{index + 1}</strong></td>
        {row.map(square => {
        return <td key={square.id} id={square.id} bgcolor={square.color}>{square.value}</td>})}
      </tr>);
    })}
    </table>
  }

  const domContainer = document.querySelector('#gameboard');
  if (domContainer) ReactDOM.render(<Gameboard />, domContainer);

})();
