import asyncio
import os
import subprocess
import sys
import time

# 1. INITIALIZE SETTINGS FIRST
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="scriptkey",
        ALLOWED_HOSTS=["*"],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
    )
    django.setup()

# 2. DJANGO & ASGI IMPORTS (AFTER django.setup())
from a2wsgi import WSGIMiddleware
from asgiref.sync import sync_to_async
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.asyncio import async_unsafe

# 3. FASTAPI & THIRD-PARTY IMPORTS
import httpx
import uvicorn
from fastapi import (
    Depends,
    FastAPI,
    Header,
    HTTPException,
    Request,
    WebSocket,
    status,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
)
from starlette.exceptions import HTTPException as StarletteHTTPException

# 4. LOCAL MODULE IMPORTS
from my_views import admin_dashboard, admin_login_view

app = FastAPI(debug=True, title="a massive portal that has been discovered")
def ice():
    print("connected")
    return 1
@staff_member_required
def admin_dashboard(request):
    context = {
        'total_users': User.objects.count(),
        'recent_users': User.objects.order_by('-date_joined')[:5],
    }
    # Renders template/dashboard.html directly
    return render(request, 'dashboard.html', context)
# Helper function to check if the current session user has admin/staff permissions
async def verify_admin_permission(request: Request):
    # Retrieve user ID stored in session (managed by Django session middleware)
    user_id = request.session.get("_auth_user_id") if hasattr(request, "session") else None
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required."
        )

    # Fetch user asynchronously from Django ORM
    @sync_to_async
    def get_staff_user(uid):
        try:
            user = User.objects.get(pk=uid)
            return user if user.is_staff or user.is_superuser else None
        except User.DoesNotExist:
            return None

    user = await get_staff_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to authorized admin personnel only."
        )
    return user
@app.get("/api/request", response_class=JSONResponse)
async def get_admin_statistics(admin_user: User = Depends(verify_admin_permission)):
    # Async database queries using sync_to_async
    @sync_to_async
    def fetch_metrics():
        return {
            "total_users": User.objects.count(),
            "active_users": User.objects.filter(is_active=True).count(),
            "staff_members": User.objects.filter(is_staff=True).count(),
            "superusers": User.objects.filter(is_superuser=True).count(),
        }

    stats = await fetch_metrics()

    return JSONResponse(
        content={
            "status": "success",
            "requested_by": admin_user.username,
            "data": stats
        },
        status_code=200
    )
@app.get("/", response_class=HTMLResponse)
async def home_page():
    html_content = """
    <!DOCTYPE html>
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
                                <code>/admin-dashboard/</code>
                            </div>
                            <p class="route-desc">Administrative interface managed via Django authentication views.</p>
                        </li>
                    </ul>
                </div>

                <p>To access API endpoints programmatically, send HTTP requests using <code>cURL</code> or your client application with the appropriate headers configured.</p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
dev_port = "25565"
def admin_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_staff:
                login(request, user)
                return redirect('/admin-dashboard/')  # Redirect to target page
            else:
                messages.error(request, "Invalid credentials or unauthorized access.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})
@app.exception_handler(StarletteHTTPException)
async def custom_404_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>404 - Page Not Found</title>
            <style>
                * {
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }

                body {
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    background-color: #0f172a;
                    color: #f8fafc;
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                    overflow: hidden;
                    position: relative;
                }

                .bg-glow {
                    position: absolute;
                    width: 300px;
                    height: 300px;
                    background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(15, 23, 42, 0) 70%);
                    border-radius: 50%;
                    animation: float 6s ease-in-out infinite alternate;
                }

                .bg-glow-1 {
                    top: 10%;
                    left: 15%;
                }

                .bg-glow-2 {
                    bottom: 10%;
                    right: 15%;
                    animation-delay: -3s;
                }

                @keyframes float {
                    0% { transform: translateY(0) scale(1); }
                    100% { transform: translateY(-20px) scale(1.05); }
                }

                .error-container {
                    position: relative;
                    z-index: 10;
                    text-align: center;
                    max-width: 520px;
                    width: 100%;
                    padding: 40px 30px;
                    background: rgba(30, 41, 59, 0.85);
                    backdrop-filter: blur(12px);
                    border: 1px solid #334155;
                    border-radius: 20px;
                    box-shadow: 0 20px 35px -10px rgba(0, 0, 0, 0.5);
                }

                .error-code {
                    font-size: 6.5rem;
                    font-weight: 900;
                    line-height: 1;
                    background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    letter-spacing: -3px;
                    margin-bottom: 12px;
                    animation: pulse 3s infinite;
                }

                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.85; }
                }

                .error-title {
                    font-size: 1.75rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    color: #ffffff;
                }

                .error-message {
                    font-size: 0.95rem;
                    color: #94a3b8;
                    line-height: 1.6;
                    margin-bottom: 28px;
                }

                .search-form {
                    display: flex;
                    gap: 8px;
                    margin-bottom: 28px;
                }

                .search-input {
                    flex: 1;
                    padding: 12px 16px;
                    background-color: #0f172a;
                    border: 1px solid #334155;
                    border-radius: 8px;
                    color: #f8fafc;
                    font-size: 0.95rem;
                    outline: none;
                    transition: border-color 0.2s ease;
                }

                .search-input:focus {
                    border-color: #6366f1;
                }

                .search-btn {
                    padding: 12px 20px;
                    background-color: #334155;
                    border: none;
                    border-radius: 8px;
                    color: #ffffff;
                    font-weight: 600;
                    cursor: pointer;
                    transition: background-color 0.2s ease;
                }

                .search-btn:hover {
                    background-color: #475569;
                }

                .btn-home {
                    display: inline-block;
                    width: 100%;
                    padding: 14px 0;
                    font-size: 1rem;
                    font-weight: 600;
                    color: #ffffff;
                    background-color: #6366f1;
                    text-decoration: none;
                    border-radius: 8px;
                    transition: background-color 0.2s ease, transform 0.1s ease;
                }

                .btn-home:hover {
                    background-color: #4f46e5;
                }

                .btn-home:active {
                    transform: scale(0.98);
                }

                @media (max-width: 480px) {
                    .error-code { font-size: 5rem; }
                    .error-title { font-size: 1.4rem; }
                    .search-form { flex-direction: column; }
                }
            </style>
        </head>
        <body>
            <div class="bg-glow bg-glow-1"></div>
            <div class="bg-glow bg-glow-2"></div>

            <div class="error-container">
                <h1 class="error-code">404</h1>
                <h2 class="error-title">Page Not Found</h2>
                <p class="error-message">
                    The link you followed might be broken, or the page may have been moved.
                </p>

                <form action="/search/" method="GET" class="search-form">
                    <input type="text" name="q" class="search-input" placeholder="Search the website..." required>
                    <button type="submit" class="search-btn">Search</button>
                </form>

                <a href="/" class="btn-home">Return to Home</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=404)

    return HTMLResponse(content=str(exc.detail), status_code=exc.status_code)
@app.get("/style.css", response_class=PlainTextResponse(media_type="text/css"))
async def get_style():
    css_content = """
    body { background-color: #121214; color: #f4f4f6; }
    """
    return css_content
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



# NEW ROUTE: Custom HTML layout endpoint for /server
@app.websocket("/server")
async def server_websocket_endpoint(websocket: WebSocket):
    # 1. Accept the incoming WebSocket connection request
    await websocket.accept()
    
    try:
        while True:
            # 2. Wait for incoming data from the client
            data = await websocket.receive_text()
            
            # 3. Send data back to the client
            await websocket.send_text(f"Server received: {data}")
            
    except WebSocketDisconnect:
        # Handle disconnects cleanly
        print("Client disconnected from /server")
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import sys
import asyncio
from utils import ensure_java_installed

app = FastAPI()

@app.post("/api/server/mc", response_class=JSONResponse)
async def launch_minecraft_server():
    # 1. Verify/Ensure Java is available on the host system
    has_java = await ensure_java_installed()
    if not has_java:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Java is not installed on the server and dynamic installation failed."
        )

    # 2. Trigger server.py as an asynchronous background subprocess
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "server.py",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Returns early while server.py runs independently in background
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "server.py process initiated successfully.",
                "pid": process.pid
            }
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to launch server.py: {str(err)}"
        )
@app.get("/server", response_class=HTMLResponse)
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive text from client
            data = await websocket.receive_text()
            # Send response back to client
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        print("Client disconnected")
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
@app.api_route("/api/status/")
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
# Register the route to accept standard and custom HTTP verbs
@app.get("/proxy/{$dev_port}", response_class=HTMLResponse)
async def page_404(dev_port: int):
    html_content = """
    <!doctype html>
    <html lang="en">
    <head>
        <title>404 Not Found</title>
    </head>
    <body>
        <h1>Not Found</h1>
        <p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=404)
@app.get("/FastAPI.example", response_class=HTMLResponse)
async def read_root():
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>My App</title>
        </head>
        <body>
            <h1>Welcome to my API</h1>
        </body>
    </html>
    """
import time
from fastapi import FastAPI, Request
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    # Process the request
    response = await call_next(request)
    
    # Calculate execution time and attach a custom header
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    return response
# Custom Exception Class
class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

# Register handler for the custom exception
@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item with ID {exc.item_id} does not exist."},
    )

# Route that triggers the exception
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id > 100:
        raise ItemNotFoundException(item_id=item_id)
    return {"item_id": item_id, "name": "Sample Item"}
API_KEY = os.environ.get("api_key")

@app.get("/api/authentication")
def get_status(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return {"status": "ok", "message": "Service is running"}
@app.get("/api/endpoint/test")
def handle_api():
    current_method = request.method.upper()

    if current_method == "POST":
        return jsonify({"message": "Resource created via POST"}), 201

    if current_method == "GET":
        # Handle GET as read-only or fetch
        return jsonify({"message": "Retrieved endpoint status via GET"}), 200

    return jsonify({"error": "Method not allowed"}), 405
try:
    # Run the 'ls' command and capture its output text
    result = ice()
    print(result)  # Outputs: 1
except Exception as e:
    print({e})
    pass
# 1. Ensure ROOT_URLCONF points to this module so Django finds `urlpatterns`
# Clean setup without orphaned try blocks
settings.ROOT_URLCONF = __name__
django_wsgi_app = get_wsgi_application()
app.mount("/", WSGIMiddleware(django_wsgi_app))
urlpatterns = [
    path('', lambda request: redirect('admin_dashboard')),  # Redirects / to /admin-dashboard/
    path('custom-login/', admin_login_view, name='custom_login'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
]
# 2. Get the Django WSGI application
django_wsgi_app = get_wsgi_application()

# 3. Mount the Django application BEFORE starting the Uvicorn server
# FastAPI will check its own /api routes first, and fall back to Django for /admin-dashboard/
app.mount("/", WSGIMiddleware(django_wsgi_app))

# 4. Run the server AT THE VERY END
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)