import os
import pty
import select
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws/terminal")
async def terminal_websocket(websocket: WebSocket):
    await websocket.accept()
    
    # Fork a pseudo-terminal (master FD controls the terminal, slave FD is the shell process)
    master_fd, slave_fd = pty.openpty()
    pid = os.fork()

    if pid == 0:
        # Child Process: Execute shell and redirect standard streams to the slave PTY
        os.close(master_fd)
        os.login_tty(slave_fd)
        os.execv("/bin/bash", ["/bin/bash"])
    else:
        # Parent Process: Handle I/O between WebSocket and Master PTY
        os.close(slave_fd)
        loop = asyncio.get_running_loop()

        async def read_from_pty():
            """Read output from shell and send to WebSocket client."""
            while True:
                await asyncio.sleep(0.01)
                # Check if master_fd has data to read
                r, _, _ = select.select([master_fd], [], [], 0)
                if master_fd in r:
                    output = os.read(master_fd, 1024)
                    if not output:
                        break
                    await websocket.send_bytes(output)

        read_task = asyncio.create_task(read_from_pty())

        try:
            while True:
                # Receive input (keystrokes) from xterm.js and write to shell
                data = await websocket.receive_bytes()
                os.write(master_fd, data)
        except WebSocketDisconnect:
            read_task.cancel()
            os.close(master_fd)
            os.kill(pid, 9)