from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
def cookie_page():
    html = """<!DOCTYPE html>
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
            margin-top: 24px;
        }

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
                <!-- Buildings injected dynamically -->
            </div>
        </div>

        <!-- RIGHT PANEL -->
        <div id="right-panel">
            <div id="right-header">News / Log</div>
            <div id="log"></div>
        </div>
    </div>

    <script>
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

        /** @type {Building[]} */
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

        bigCookieEl.addEventListener("click", (event) => {
            cookies += cookiesPerClick;
            updateStatsDisplay();
            updateBuildingsUI();

            const rect = bigCookieEl.getBoundingClientRect();
            const x = event.clientX - rect.left - 10;
            const y = event.clientY - rect.top - 10;
            spawnFloatingText("+" + cookiesPerClick, x, y);
        });

        let lastFrameTime = performance.now();

        function gameLoop(timestamp) {
            const delta = (timestamp - lastFrameTime) / 1000;
            lastFrameTime = timestamp;

            cookies += cookiesPerSecond * delta;
            updateStatsDisplay();
            updateBuildingsUI();

            requestAnimationFrame(gameLoop);
        }

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

        setInterval(saveGame, 15000);

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
</html>"""
def server_page():
    html = """<!DOCTYPE html>
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
        <div id="status-log">Ready to bridge payloads...</div>
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
                const iframeWindow = frame.contentWindow;

                // 1. Simulate pressing 'T' key to open the in-game chat prompt inside Minecraft
                simulateKey(iframeWindow, 84, 't');

                // 2. Wait 150ms for the UI animation frame delay inside Minecraft, then type out and push the string
                setTimeout(() => {
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
</html>"""

    return HTMLResponse(content=custom_html_layout, status_code=200)
def front_page_view():
    html = """<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Python UUID Portal - Site Map</title>
            <style>
                :root {
                    --bg-primary: #121214;
                    --bg-secondary: #1a1a1e;
                    --bg-card: #232329;
                    --text-primary: #f4f4f6;
                    --text-secondary: #a1a1aa;
                    --accent: #6366f1;
                    --accent-hover: #4f46e5;
                    --border: #3f3f46;
                    --code-bg: #09090b;
                    --radius: 8px;
                    --transition: all 0.2s ease;
                }

                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }

                body {
                    background-color: var(--bg-primary);
                    color: var(--text-primary);
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    line-height: 1.6;
                    padding: 3rem 1rem;
                }

                .container {
                    max-width: 700px;
                    margin: 0 auto;
                }

                header {
                    margin-bottom: 2.5rem;
                }

                h1 {
                    font-size: 2.2rem;
                    font-weight: 700;
                    margin-bottom: 0.75rem;
                    letter-spacing: -0.025em;
                }

                p {
                    color: var(--text-secondary);
                    margin-bottom: 1.25rem;
                    font-size: 1.05rem;
                }

                .box {
                    background-color: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: var(--radius);
                    padding: 2rem;
                    margin: 2rem 0;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
                }

                h3 {
                    font-size: 1.3rem;
                    margin-bottom: 1.25rem;
                    border-bottom: 1px solid var(--border);
                    padding-bottom: 0.5rem;
                    color: var(--text-primary);
                }

                .route-list {
                    list-style: none;
                    display: flex;
                    flex-direction: column;
                    gap: 1rem;
                }

                .route-item {
                    background-color: var(--bg-secondary);
                    border: 1px solid var(--border);
                    border-radius: var(--radius);
                    padding: 1rem;
                    display: flex;
                    flex-direction: column;
                    gap: 0.4rem;
                }

                .route-item-header {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }

                .method-badge {
                    background-color: var(--accent);
                    color: #ffffff;
                    font-size: 0.75rem;
                    font-weight: 700;
                    padding: 0.15rem 0.5rem;
                    border-radius: 4px;
                    text-transform: uppercase;
                }

                code {
                    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                    font-size: 0.95rem;
                    color: #e2e8f0;
                    background-color: var(--code-bg);
                    border: 1px solid var(--border);
                    padding: 0.2rem 0.5rem;
                    border-radius: 4px;
                }

                .route-desc {
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                }

                .nav-link {
                    color: var(--accent);
                    text-decoration: none;
                    font-weight: 500;
                    transition: var(--transition);
                }

                .nav-link:hover {
                    text-decoration: underline;
                }

                @media (max-width: 640px) {
                    body {
                        padding: 1.5rem 0.5rem;
                    }
                    h1 {
                        font-size: 1.8rem;
                    }
                    .box {
                        padding: 1.25rem;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Python Web Portal - Endpoint Index</h1>
                    <p>Overview of all configured routes and API endpoints on this server.</p>
                </header>
                
                <div class="box">
                    <h3>Available Site Routes</h3>
                    <ul class="route-list">
                        <li class="route-item">
                            <div class="route-item-header">
                                <span class="method-badge">GET</span>
                                <code>/</code>
                            </div>
                            <p class="route-desc">Home page and server route directory (this page).</p>
                        </li>

                        <li class="route-item">
                            <div class="route-item-header">
                                <span class="method-badge">GET</span>
                                <code>/server</code>
                            </div>
                            <p class="route-desc">Main web application interface. <a href="/server" class="nav-link">Visit route &rarr;</a></p>
                        </li>

                        <li class="route-item">
                            <div class="route-item-header">
                                <span class="method-badge">GET</span>
                                <code>/API/status/</code>
                            </div>
                            <p class="route-desc">Retrieves UUID data. Requires the <code>amount</code> header specifying the count.</p>
                        </li>

                        <li class="route-item">
                            <div class="route-item-header">
                                <span class="method-badge">GET</span>
                                <code>/proxy/{dev_port}</code>
                            </div>
                            <p class="route-desc">Dynamic proxy route passing <code>dev_port</code> as a path parameter.</p>
                        </li>

                        <li class="route-item">
                            <div class="route-item-header">
                                <span class="method-badge">GET</span>
                                <code>/admindashboard/</code>
                            </div>
                            <p class="route-desc">Administrative interface managed via Django authentication views.</p>
                        </li>
                    </ul>
                </div>

                <p>To access API endpoints programmatically, send HTTP requests using <code>cURL</code> or your client application with the appropriate headers configured.</p>
            </div>
        </body>
    </html>"""

def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('/admindashboard/')
            else:
                messages.error(request, "Invalid credentials or unauthorized access.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

@staff_member_required
def admin_dashboard(request):
    # Fetch summary metrics or stats to display on the dashboard
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    recent_users = User.objects.order_by('-date_joined')[:5]

    context = {
        'total_users': total_users,
        'active_users': active_users,
        'recent_users': recent_users,
    }
    return render(request, 'dashboard.html', context)