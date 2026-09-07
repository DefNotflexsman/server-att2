// 1. Instantiate the Terminal
const term = new Terminal({
  cursorBlink: true,
  fontSize: 14,
  fontFamily: 'Courier New, monospace',
  theme: {
    background: '#1e1e1e',
    foreground: '#ffffff'
  }
});

// 2. Attach xterm to the DOM container
term.open(document.getElementById('terminal'));

// 3. Construct WebSocket URL (handles http -> ws and https -> wss)
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const socket = new WebSocket(`${protocol}//${window.location.host}/ws/terminal`);

// 4. Handle incoming terminal output from server -> render in xterm
socket.onmessage = (event) => {
  term.write(event.data);
};

// 5. Handle user key inputs -> send data over WebSocket to backend shell
term.onData((data) => {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(data);
  }
});

// Connection state notifications
socket.onopen = () => term.write('\r\n*** Connected to Remote Shell ***\r\n\r\n');
socket.onclose = () => term.write('\r\n*** Connection Closed ***\r\n');