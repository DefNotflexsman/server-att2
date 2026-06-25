import os
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="UUID Generator Site")

@app.get("/controllerempt", response_class=HTMLResponse)
async def server_page():
    # Insert your custom layout details inside this multi-line string variable
    custom_html_layout = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eaglercraft Embedded Client & Terminal Controller</title>
    <style>
        body {
            background-color: #121212;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 95vh;
        }
        h2 {
            margin-top: 0;
            margin-bottom: 10px;
            color: #39ff14;
        }
        #game-container {
            width: 854px;
            height: 480px;
            border: 3px solid #333;
            background-color: #000;
            box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
        #terminal-panel {
            width: 854px;
            margin-top: 15px;
            background-color: #1e1e1e;
            border: 2px solid #39ff14;
            padding: 15px;
            box-sizing: border-box;
            border-radius: 4px;
        }
        .instruction {
            font-size: 13px;
            color: #aaa;
            margin-bottom: 10px;
        }
        #input-row {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex-grow: 1;
            background-color: #000;
            border: 1px solid #39ff14;
            color: #39ff14;
            padding: 10px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 14px;
        }
        button {
            background-color: #39ff14;
            color: #000;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            cursor: pointer;
            font-family: inherit;
        }
        button:hover {
            background-color: #fff;
        }
        #status-log {
            margin-top: 8px;
            font-size: 12px;
            color: #ffcc00;
            font-family: monospace;
        }
    </style>
</head>
<body>

    <h2>Eaglercraft 1.8.8 Terminal Client Bridge</h2>
    
    <!-- Embedded Full Eaglercraft Web client Instance -->
    <div id="game-container">
        <iframe id="eagler-frame" src="http://test.tuffis.online/" allow="autoplay; gamepad; keyboard;"></iframe>
    </div>

    <!-- The External Control Terminal -->
    <div id="terminal-panel">
        <div class="instruction">
            <strong>How to use:</strong> Join your server (e.g., ArchMC) inside the frame above. Once spawned in-game, type commands or chat strings below and press Send.
        </div>
        <div id="input-row">
            <input type="text" id="terminal-cmd" placeholder="Type /register, /login, or server chat commands here..." onkeydown="checkKey(event)">
            <button onclick="injectCommand()">Send to Client</button>
        </div>
        <div id="status-log" id="log">Ready to bridge payloads...</div>
    </div>

    <script>
        const frame = document.getElementById('eagler-frame');
        const cmdInput = document.getElementById('terminal-cmd');
        const statusLog = document.getElementById('status-log');

        function injectCommand() {
            const commandText = cmdInput.value.trim();
            if (!commandText) return;

            statusLog.textContent = `Processing packet transmission: "${commandText}"`;

            try {
                // Cross-Origin / Same-Origin Context Execution Check
                // Attempt direct pipeline injection into TeaVM runtime engine via the iframe window context
                const iframeWindow = frame.contentWindow;

                /* 
                  TECHNICAL EXPLANATION:
                  Eaglercraft 1.8.8 uses an asset package where JavaScript keyboard event hooks handle strings.
                  Instead of interacting with internal networking objects, we simulate the actual user opening 
                  the game's chat window ('t' key), pasting the command string, and hitting 'Enter'.
                */
                
                // 1. Simulate pressing 'T' key to open the in-game chat prompt inside Minecraft
                simulateKey(iframeWindow, 84, 't');

                // 2. Wait 150ms for the UI animation frame delay inside Minecraft, then type out and push the string
                setTimeout(() => {
                    // Injecting text characters sequentially or directly altering the clipboard cache if hooks are present
                    // For headless execution environments or local deployments:
                    if(iframeWindow.main && iframeWindow.main.arguments) {
                         // Alternate path if running a custom local unpack:
                         // iframeWindow.EaglercraftX.sendChat(commandText);
                    }
                    
                    // Fallback to firing keyboard input streams programmatically down into the active Canvas
                    for (let i = 0; i < commandText.length; i++) {
                        simulateCharInput(iframeWindow, commandText.charAt(i));
                    }

                    // 3. Fire the 'Enter' key event (KeyCode 13) to finalize submission over the WebSocket relay
                    setTimeout(() => {
                        simulateKey(iframeWindow, 13, 'Enter');
                        statusLog.textContent = `Command successfully dispatched to client instance.`;
                        cmdInput.value = '';
                        cmdInput.focus();
                    }, 100);

                }, 150);

            } catch (e) {
                // Browser Cross-Origin Resource Sharing (CORS) Security Catch
                statusLog.textContent = "Security Warning: Embed requires running locally or on the same domain deployment to pass window payloads.";
                console.error("CORS blocking window injection:", e);
            }
        }

        // Low-level DOM keyboard event generator targeting the embedded canvas engine
        function simulateKey(targetWindow, keyCode, keyName) {
            const targetDoc = targetWindow.document;
            const targetEl = targetDoc.querySelector('canvas') || targetDoc.body;

            const opts = { bubbles: true, cancelable: true, keyCode: keyCode, key: keyName, which: keyCode };
            targetEl.dispatchEvent(new KeyboardEvent('keydown', opts));
            targetEl.dispatchEvent(new KeyboardEvent('keypress', opts));
            setTimeout(() => {
                targetEl.dispatchEvent(new KeyboardEvent('keyup', opts));
            }, 20);
        }

        function simulateCharInput(targetWindow, char) {
            const targetDoc = targetWindow.document;
            const targetEl = targetDoc.querySelector('canvas') || targetDoc.body;
            const opts = { bubbles: true, cancelable: true, key: char, char: char };
            targetEl.dispatchEvent(new KeyboardEvent('keypress', opts));
        }

        function checkKey(e) {
            if (e.key === 'Enter') injectCommand();
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=custom_html_layout, status_code=200)
# Base landing page: Pure Python website rendering HTML response
@app.get("/", response_class=HTMLResponse)
async def home_page():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Python UUID Portal</title>
            <style>
                body { font-family: sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; line-height: 1.6; }
                code { background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-family: monospace; }
                .box { border: 1px solid #ddd; padding: 15px; border-radius: 5px; background: #fafafa; }
            </style>
        </head>
        <body>
            <h1>Welcome to the Python UUID Web Portal</h1>
            <p>This entire platform is built natively using 100% Python.</p>
            
            <div class="box">
                <h3>API Endpoint Documentation</h3>
                <p><strong>Route:</strong> <code>/API/status/</code></p>
                <p><strong>Method:</strong> <code>GET</code></p>
                <p><strong>Required Header:</strong> <code>amount</code> (Integer specifying how many UUIDs to pull)</p>
            </div>
            
            <p>To pull data, request the route using a tool like cURL or a local script by specifying your desired count value inside the request headers.</p>
            <p>Visit the new page layout here: <a href="/server">/server</a></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


# NEW ROUTE: Custom HTML layout endpoint for /server
@app.get("/server", response_class=HTMLResponse)
async def server_page():
    # Insert your custom layout details inside this multi-line string variable
    custom_html_layout = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WSS Connection Stream Client</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #121214; color: #e1e1e6; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: #202024; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        .input-group { display: flex; gap: 10px; margin-bottom: 15px; }
        input[type="text"] { flex: 1; padding: 10px; background: #121214; border: 1px solid #41414d; color: #fff; border-radius: 4px; font-size: 14px; }
        button { padding: 10px 20px; border: none; border-radius: 4px; font-weight: bold; cursor: pointer; transition: background 0.2s; }
        .btn-connect { background: #04d361; color: #000; }
        .btn-connect.connected { background: #f75a68; color: #fff; }
        .btn-send { background: #8257e5; color: #fff; }
        button:disabled { background: #41414d; color: #8d8d99; cursor: not-allowed; }
        #log { background: #121214; border: 1px solid #41414d; height: 350px; overflow-y: auto; padding: 15px; font-family: monospace; border-radius: 4px; font-size: 13px; line-height: 1.5; }
        .log-entry { margin-bottom: 5px; border-bottom: 1px solid #202024; padding-bottom: 5px; }
        .info { color: #61dafb; }
        .success { color: #04d361; }
        .error { color: #f75a68; }
        .incoming { color: #ffdb55; }
        .outgoing { color: #a482f4; }
    </style>
</head>
<body>

<div class="container">
    <h2>⚡️ Secure WebSocket (WSS) Client</h2>
    
    <!-- Connection Row -->
    <div class="input-group">
        <input type="text" id="wssUrl" value="wss://rubynetwork.com" placeholder="wss://address:port">
        <button id="connectBtn" class="btn-connect" onclick="toggleConnection()">Connect</button>
    </div>

    <!-- Data Injection Row -->
    <div class="input-group">
        <input type="text" id="messageInput" placeholder="Type data payload to send to server..." disabled>
        <button id="sendBtn" class="btn-send" onclick="sendMessage()" disabled>Send Packet</button>
    </div>

    <!-- Stream Terminal -->
    <h3>Console Stream Log</h3>
    <div id="log"></div>
</div>

<script>
    let ws = null;
    const wssUrlInput = document.getElementById('wssUrl');
    const connectBtn = document.getElementById('connectBtn');
    const messageInput = document.getElementById('messageInput');
    const sendBtn = document.getElementById('sendBtn');
    const logContainer = document.getElementById('log');

    function writeLog(text, type = 'info') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        entry.innerText = `[${new Date().toLocaleTimeString()}] ${text}`;
        logContainer.appendChild(entry);
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    function toggleConnection() {
        if (ws && ws.readyState === WebSocket.OPEN) {
            writeLog("Disconnecting client from server...", "info");
            ws.close();
            return;
        }

        const url = wssUrlInput.value.trim();
        if (!url) return alert("Please enter a valid target URL");

        writeLog(`Attempting handshake with: ${url}`, "info");
        
        try {
            ws = new WebSocket(url);
            
            ws.onopen = () => {
                writeLog("SUCCESS: Connection established and stream active!", "success");
                connectBtn.innerText = "Disconnect";
                connectBtn.classList.add('connected');
                messageInput.disabled = false;
                sendBtn.disabled = false;
                wssUrlInput.disabled = true;
            };

            ws.onmessage = (event) => {
                writeLog(`RCVD: ${event.data}`, "incoming");
            };

            ws.onerror = (error) => {
                writeLog("ERROR: Network handshake failed. Check endpoint parameters or Origin rules.", "error");
                console.error(error);
            };

            ws.onclose = (event) => {
                writeLog(`CLOSED: Connection broken. Code: ${event.code} | Reason: ${event.reason || 'None provided'}`, "error");
                connectBtn.innerText = "Connect";
                connectBtn.classList.remove('connected');
                messageInput.disabled = true;
                sendBtn.disabled = true;
                wssUrlInput.disabled = false;
                ws = null;
            };

        } catch (e) {
            writeLog(`CRITICAL: ${e.message}`, "error");
        }
    }

    function sendMessage() {
        if (!ws || ws.readyState !== WebSocket.OPEN) return;
        const msg = messageInput.value;
        if (!msg) return;
        
        ws.send(msg);
        writeLog(`SENT: ${msg}`, "outgoing");
        messageInput.value = '';
    }

    // Allow Enter key to trigger transmission
    messageInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
</script>

</body>
</html>
    """
    return HTMLResponse(content=custom_html_layout, status_code=200)
@app.get("/cookie", response_class=HTMLResponse)
async def server_page():
    # Insert your custom layout details inside this multi-line string variable
    custom_html_layout = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Cookie Clicker Offline Clone</title>
    <style>
        :root {
            --bg-color: #1b1b1b;
            --panel-color: #2b2b2b;
            --accent-color: #d3b26f;
            --text-color: #f5f5f5;
            --font-main: "Trebuchet MS", Arial, sans-serif;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background: url("bg_tile.png") repeat #000;
            color: var(--text-color);
            font-family: var(--font-main);
            overflow: hidden;
        }

        #game-container {
            display: grid;
            grid-template-columns: 1.2fr 1.2fr 1fr;
            height: 100vh;
        }

        /* Left panel: stats + big cookie */
        #left-panel {
            background: rgba(0, 0, 0, 0.4);
            padding: 10px;
            display: flex;
            flex-direction: column;
            align-items: center;
            border-right: 2px solid #000;
        }

        #stats {
            text-align: center;
            margin-bottom: 10px;
        }

        #stats h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }

        #stats .cookies-count {
            font-size: 20px;
        }

        #stats .cps {
            font-size: 14px;
            color: #ccc;
        }

        #big-cookie-container {
            margin-top: 20px;
            position: relative;
        }

        #big-cookie {
            width: 256px;
            height: 256px;
            background: url("big_cookie.png") center/cover no-repeat;
            border-radius: 50%;
            cursor: pointer;
            transition: transform 0.05s ease-out;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.8);
        }

        #big-cookie:active {
            transform: scale(0.95);
        }

        .floating-text {
            position: absolute;
            color: #fff;
            font-weight: bold;
            pointer-events: none;
            text-shadow: 0 0 5px #000;
            animation: floatUp 0.8s ease-out forwards;
        }

        @keyframes floatUp {
            0% {
                opacity: 1;
                transform: translateY(0);
            }
            100% {
                opacity: 0;
                transform: translateY(-40px);
            }
        }

        /* Middle panel: upgrades / buildings */
        #middle-panel {
            background: var(--panel-color);
            border-right: 2px solid #000;
            display: flex;
            flex-direction: column;
        }

        #upgrades-header {
            padding: 8px;
            background: #3b3b3b;
            border-bottom: 2px solid #000;
            text-align: center;
            font-weight: bold;
        }

        #buildings-list {
            flex: 1;
            overflow-y: auto;
        }

        .building {
            display: flex;
            align-items: center;
            padding: 8px;
            border-bottom: 1px solid #444;
            cursor: pointer;
            background: #2b2b2b;
            transition: background 0.1s ease-out;
        }

        .building:hover {
            background: #3b3b3b;
        }

        .building.disabled {
            opacity: 0.4;
            cursor: default;
        }

        .building-icon {
            width: 48px;
            height: 48px;
            margin-right: 8px;
            background-size: cover;
            background-position: center;
            border: 1px solid #000;
        }

        .building-info {
            flex: 1;
        }

        .building-name {
            font-size: 14px;
            font-weight: bold;
        }

        .building-cost {
            font-size: 12px;
            color: #d3b26f;
        }

        .building-cps {
            font-size: 11px;
            color: #aaa;
        }

        .building-amount {
            font-size: 16px;
            font-weight: bold;
            margin-left: 8px;
        }

        /* Right panel: log / info */
        #right-panel {
            background: #1f1f1f;
            display: flex;
            flex-direction: column;
        }

        #right-header {
            padding: 8px;
            background: #3b3b3b;
            border-bottom: 2px solid #000;
            text-align: center;
            font-weight: bold;
        }

        #log {
            flex: 1;
            padding: 8px;
            font-size: 12px;
            overflow-y: auto;
        }

        .log-entry {
            margin-bottom: 4px;
            color: #ccc;
        }

        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #111;
        }

        ::-webkit-scrollbar-thumb {
            background: #444;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #666;
        }

        /* Top bar */
        #top-bar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 24px;
            background: #000;
            color: #ccc;
            font-size: 12px;
            display: flex;
            align-items: center;
            padding: 0 8px;
            z-index: 10;
        }

        #top-bar span {
            margin-right: 16px;
        }

        #game-container {
            margin-top: 24px;
        }

        /* Responsive tweak */
        @media (max-width: 1000px) {
            #game-container {
                grid-template-columns: 1fr;
            }
            #left-panel, #middle-panel, #right-panel {
                border-right: none;
                border-bottom: 2px solid #000;
                height: auto;
            }
        }
    </style>
</head>
<body>
    <div id="top-bar">
        <span>Cookie Clicker Offline Clone</span>
        <span id="save-status">Autosaving...</span>
    </div>

    <div id="game-container">
        <!-- LEFT PANEL -->
        <div id="left-panel">
            <div id="stats">
                <h1>Cookies</h1>
                <div class="cookies-count" id="cookies-count">0</div>
                <div class="cps" id="cps-display">per second: 0</div>
            </div>
            <div id="big-cookie-container">
                <div id="big-cookie"></div>
            </div>
        </div>

        <!-- MIDDLE PANEL -->
        <div id="middle-panel">
            <div id="upgrades-header">Buildings</div>
            <div id="buildings-list">
                <!-- Buildings will be injected here -->
            </div>
        </div>

        <!-- RIGHT PANEL -->
        <div id="right-panel">
            <div id="right-header">News / Log</div>
            <div id="log"></div>
        </div>
    </div>

    <script>
        // -----------------------------
        // Core game state
        // -----------------------------
        type GameBuilding = {
            id: string;
            name: string;
            baseCost: number;
            cost: number;
            cps: number;
            amount: number;
            icon: string;
        };

        // Using JSDoc types for browsers (since TS types aren't compiled here)
        /**
         * @typedef {Object} Building
         * @property {string} id
         * @property {string} name
         * @property {number} baseCost
         * @property {number} cost
         * @property {number} cps
         * @property {number} amount
         * @property {string} icon
         */

        /**
         * @type {Building[]}
         */
        const buildings = [
            {
                id: "cursor",
                name: "Cursor",
                baseCost: 15,
                cost: 15,
                cps: 0.1,
                amount: 0,
                icon: "cursor.png"
            },
            {
                id: "grandma",
                name: "Grandma",
                baseCost: 100,
                cost: 100,
                cps: 1,
                amount: 0,
                icon: "grandma.png"
            },
            {
                id: "farm",
                name: "Farm",
                baseCost: 1100,
                cost: 1100,
                cps: 8,
                amount: 0,
                icon: "farm.png"
            },
            {
                id: "factory",
                name: "Factory",
                baseCost: 13000,
                cost: 13000,
                cps: 47,
                amount: 0,
                icon: "factory.png"
            }
        ];

        let cookies = 0;
        let cookiesPerClick = 1;
        let cookiesPerSecond = 0;

        const cookiesCountEl = document.getElementById("cookies-count");
        const cpsDisplayEl = document.getElementById("cps-display");
        const bigCookieEl = document.getElementById("big-cookie");
        const bigCookieContainerEl = document.getElementById("big-cookie-container");
        const buildingsListEl = document.getElementById("buildings-list");
        const logEl = document.getElementById("log");
        const saveStatusEl = document.getElementById("save-status");

        // -----------------------------
        // Utility functions
        // -----------------------------
        function formatNumber(value) {
            if (value >= 1_000_000_000) {
                return (value / 1_000_000_000).toFixed(2) + " billion";
            }
            if (value >= 1_000_000) {
                return (value / 1_000_000).toFixed(2) + " million";
            }
            if (value >= 1_000) {
                return value.toLocaleString();
            }
            return value.toString();
        }

        function logMessage(message) {
            const entry = document.createElement("div");
            entry.className = "log-entry";
            entry.textContent = message;
            logEl.prepend(entry);
        }

        function updateStatsDisplay() {
            cookiesCountEl.textContent = formatNumber(Math.floor(cookies));
            cpsDisplayEl.textContent = "per second: " + cookiesPerSecond.toFixed(1);
        }

        function recalculateCps() {
            let total = 0;
            for (const b of buildings) {
                total += b.cps * b.amount;
            }
            cookiesPerSecond = total;
        }

        function updateBuildingsUI() {
            for (const b of buildings) {
                const row = document.querySelector(`.building[data-id="${b.id}"]`);
                if (!row) continue;
                const costEl = row.querySelector(".building-cost");
                const cpsEl = row.querySelector(".building-cps");
                const amountEl = row.querySelector(".building-amount");

                costEl.textContent = "Cost: " + formatNumber(Math.floor(b.cost)) + " cookies";
                cpsEl.textContent = b.cps + " cps";
                amountEl.textContent = b.amount.toString();

                if (cookies >= b.cost) {
                    row.classList.remove("disabled");
                } else {
                    row.classList.add("disabled");
                }
            }
        }

        function createBuildingsUI() {
            buildingsListEl.innerHTML = "";
            for (const b of buildings) {
                const row = document.createElement("div");
                row.className = "building disabled";
                row.dataset.id = b.id;

                const icon = document.createElement("div");
                icon.className = "building-icon";
                icon.style.backgroundImage = `url("${b.icon}")`;

                const info = document.createElement("div");
                info.className = "building-info";

                const nameEl = document.createElement("div");
                nameEl.className = "building-name";
                nameEl.textContent = b.name;

                const costEl = document.createElement("div");
                costEl.className = "building-cost";
                costEl.textContent = "Cost: " + formatNumber(b.cost) + " cookies";

                const cpsEl = document.createElement("div");
                cpsEl.className = "building-cps";
                cpsEl.textContent = b.cps + " cps";

                info.appendChild(nameEl);
                info.appendChild(costEl);
                info.appendChild(cpsEl);

                const amountEl = document.createElement("div");
                amountEl.className = "building-amount";
                amountEl.textContent = "0";

                row.appendChild(icon);
                row.appendChild(info);
                row.appendChild(amountEl);

                row.addEventListener("click", () => {
                    buyBuilding(b.id);
                });

                buildingsListEl.appendChild(row);
            }
        }

        function buyBuilding(id) {
            const building = buildings.find(b => b.id === id);
            if (!building) return;
            if (cookies < building.cost) return;

            cookies -= building.cost;
            building.amount += 1;
            building.cost = Math.floor(building.baseCost * Math.pow(1.15, building.amount));

            recalculateCps();
            updateStatsDisplay();
            updateBuildingsUI();
            logMessage(`Bought 1 ${building.name}. You now own ${building.amount}.`);
        }

        function spawnFloatingText(text, x, y) {
            const el = document.createElement("div");
            el.className = "floating-text";
            el.textContent = text;
            el.style.left = x + "px";
            el.style.top = y + "px";
            bigCookieContainerEl.appendChild(el);

            setTimeout(() => {
                el.remove();
            }, 800);
        }

        // -----------------------------
        // Click handling
        // -----------------------------
        bigCookieEl.addEventListener("click", (event) => {
            cookies += cookiesPerClick;
            updateStatsDisplay();
            updateBuildingsUI();

            const rect = bigCookieEl.getBoundingClientRect();
            const x = event.clientX - rect.left - 10;
            const y = event.clientY - rect.top - 10;
            spawnFloatingText("+" + cookiesPerClick, x, y);
        });

        // -----------------------------
        // Game loop
        // -----------------------------
        let lastFrameTime = performance.now();

        function gameLoop(timestamp) {
            const delta = (timestamp - lastFrameTime) / 1000;
            lastFrameTime = timestamp;

            cookies += cookiesPerSecond * delta;
            updateStatsDisplay();
            updateBuildingsUI();

            requestAnimationFrame(gameLoop);
        }

        // -----------------------------
        // Save / Load
        // -----------------------------
        const SAVE_KEY = "cookie_clicker_offline_clone_save";

        function saveGame() {
            try {
                const data = {
                    cookies,
                    cookiesPerClick,
                    buildings: buildings.map(b => ({
                        id: b.id,
                        amount: b.amount,
                        cost: b.cost
                    }))
                };
                localStorage.setItem(SAVE_KEY, JSON.stringify(data));
                saveStatusEl.textContent = "Saved";
                setTimeout(() => {
                    saveStatusEl.textContent = "Autosaving...";
                }, 1500);
            } catch (error) {
                console.error("Error saving game:", error);
                saveStatusEl.textContent = "Save error";
            }
        }

        function loadGame() {
            try {
                const raw = localStorage.getItem(SAVE_KEY);
                if (!raw) {
                    logMessage("New game started.");
                    return;
                }
                const data = JSON.parse(raw);
                if (typeof data.cookies === "number") {
                    cookies = data.cookies;
                }
                if (typeof data.cookiesPerClick === "number") {
                    cookiesPerClick = data.cookiesPerClick;
                }
                if (Array.isArray(data.buildings)) {
                    for (const saved of data.buildings) {
                        const b = buildings.find(x => x.id === saved.id);
                        if (!b) continue;
                        if (typeof saved.amount === "number") {
                            b.amount = saved.amount;
                        }
                        if (typeof saved.cost === "number") {
                            b.cost = saved.cost;
                        }
                    }
                }
                recalculateCps();
                logMessage("Game loaded.");
            } catch (error) {
                console.error("Error loading game:", error);
                logMessage("Failed to load save, starting new game.");
            }
        }

        // Autosave every 15 seconds
        setInterval(saveGame, 15000);

        // -----------------------------
        // Init
        // -----------------------------
        function init() {
            createBuildingsUI();
            loadGame();
            updateStatsDisplay();
            updateBuildingsUI();
            requestAnimationFrame(gameLoop);
        }

        window.addEventListener("load", init);
    </script>
</body>
</html>
    """
    return HTMLResponse(content=custom_html_layout, status_code=200)

# API Route to pull and grab external UUID data
@app.get("/API/status/")
async def get_uuid_status(amount: int = Header(..., description="The amount of UUIDs requested")):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="The 'amount' header must be a positive integer greater than 0.")
    if amount > 100:
        raise HTTPException(status_code=400, detail="To prevent timeouts, you can pull a maximum of 100 UUIDs per request.")
        
    external_url = f"https://www.uuidtools.com/api/generate/v1/count/{amount}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_url)
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to retrieve data from the upstream UUID engine.")
                
            uuids_list = response.json()
            
            return {
                "status": "success",
                "requested_amount": amount,
                "data_type": "render_payload",
                "uuids": uuids_list
            }
            
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Network error trying to fetch upstream data: {exc}")

# Fallback runner for local execution outside of Render environment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
