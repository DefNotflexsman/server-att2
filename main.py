import importlib
from pathlib import Path
import django
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent

# 1. INITIALIZE DJANGO SETTINGS
if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="scriptkey",
        ALLOWED_HOSTS=["*"],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        },
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [BASE_DIR / "templates"],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ],
    )
    django.setup()
from django.contrib.admin.views.decorators import staff_member_required
from my_views import front_page_view
from django.contrib.staticfiles.finders import find
from django.contrib import admin
from django.urls import path
from my_views import cookie_page
from my_views import fetch_metrics
from my_views import css_content
from my_views import server_page
import time
from fastapi import FastAPI, Request
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import sys
import asyncio
from utils import ensure_java_installed
from fastapi import APIRouter
from my_views import admin_dashboard
from fastapi import Header
from fastapi import WebSocket
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse
from fastapi import Depends
from fastapi.responses import JSONResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render
from fastapi import Request, HTTPException, status
from asgiref.sync import sync_to_async
# 2. DYNAMIC IMPORTS
imports_list = [
    ("asyncio", None),
    ("os", None),
    ("subprocess", None),
    ("sys", None),
    ("time", None),
    ("a2wsgi", "WSGIMiddleware"),
    ("asgiref.sync", "sync_to_async"),
    ("django.contrib.admin", "ModelAdmin"),
    ("django.contrib", "messages"),
    ("django.contrib.auth", "authenticate"),
    ("django.contrib.auth", "login"),
    ("django.contrib.auth.models", "User"),
    ("django.core.management", "call_command"),
    ("django.core.wsgi", "get_wsgi_application"),
    ("django.shortcuts", "redirect"),
    ("django.shortcuts", "render"),
    ("django.http", "HttpResponse"),
    ("django.http", "JsonResponse"),
    ("django.urls", "path"),
    ("httpx", None),
    ("uvicorn", None),
    ("fastapi", "FastAPI"),
    ("starlette.exceptions", "HTTPException", "StarletteHTTPException"),
    # Import admin handlers directly from my_views.py
    ("my_views", "admin_dashboard"),
    ("my_views", "admin_login_view"),
]
owner_ip = "47.158.31.28"
for item in imports_list:
    module_path = item[0]
    attr_name = item[1]
    alias = item[2] if len(item) > 2 else attr_name

    mod = importlib.import_module(module_path)
    if attr_name:
        globals()[alias] = getattr(mod, attr_name)
    else:
        top_level_name = module_path.split(".")[0]
        globals()[top_level_name] = importlib.import_module(top_level_name)
# 4. REGISTER URL PATTERNS
urlpatterns = [
    path("admindashboard/", admin_dashboard, name="admin_dashboard"),
    path("adminlogin/", admin_login_view, name="admin_login"),
    path("style.css", css_content, name="style_css"),
    path("page404/", css_content, name="page404"),
    path("cookie/", cookie_page, name="cookie"),
    path("server/", server_page, name="server"),
    path("controllerempt/", server_page, name="controllerempt"),
    path("items/<int:item_id>/", read_item, name="item_detail"),
    path("api/request/", fetch_metrics, name="api_request"),
    path("api/server/mc/", launch_minecraft_server, name="api_server_mc"),
    path("api/status/", api_status_view, name="api_status"),
    path("api/authentication/", api_authentication_view, name="api_authentication"),
    path("api/endpoint/test/", api_endpoint_test_view, name="api_endpoint_test"),
    path("proxy/25565/", proxy_stream_view, name="proxy_stream"),
]
# 3. DYNAMICALLY LOAD IMPORTS INTO GLOBAL SCOPE
for item in imports_list:
    module_path = item[0]
    attr_name = item[1]
    alias = item[2] if len(item) > 2 else attr_name

    mod = importlib.import_module(module_path)
    if attr_name:
        globals()[alias] = getattr(mod, attr_name)
    else:
        top_level_name = module_path.split(".")[0]
        globals()[top_level_name] = importlib.import_module(top_level_name)
router = APIRouter()
app = FastAPI(debug=False, title="a massive portal that has been discovered")
def ice():
    print(f".")
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from django.shortcuts import render
from fastapi import Request, HTTPException, status
from asgiref.sync import sync_to_async
User = get_user_model()
@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    user_ip = request.client.host if request.client else "Unknown"
    requested_path = request.url.path

    # Custom logging function
    print(f"Request from IP: {user_ip} to Path: {requested_path}")

    response = await call_next(request)
    return response
@staff_member_required
def admin_dashboard(request):
    context = {
        "total_users": User.objects.count(),
        "recent_users": User.objects.order_by("-date_joined")[:5],
    }
    return render(request, "admin-dashboard.html", context)


# --- FASTAPI DEPENDENCY ---
async def verify_admin_permission(request: Request):
    session_key = request.cookies.get("sessionid")

    if not session_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication cookie required.",
        )

    @sync_to_async
    def get_staff_user(key):
        try:
            session = Session.objects.get(session_key=key)
            uid = session.get_decoded().get("_auth_user_id")

            if not uid:
                return None

            user = User.objects.get(pk=uid)
            return user if (user.is_staff or user.is_superuser) else None
        except (Session.DoesNotExist, User.DoesNotExist):
            return None

    user = await get_staff_user(session_key)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to authorized admin personnel only.",
        )

    return user
@router.get("/api/request", response_class=JSONResponse)
async def get_admin_statistics(admin_user: User = Depends(verify_admin_permission)):
    # Call sync_to_async as a function wrapper and await it
    metrics = await sync_to_async(fetch_metrics)()
    
    return JSONResponse(content={"status": "success", "data": metrics})
@app.get("/", response_class=HTMLResponse)
async def home_endpoint(request: Request):
    django_response = front_page_view(request)
    return HTMLResponse(
        content=django_response.content.decode("utf-8"), 
        status_code=django_response.status_code
    )
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
       css_content()
@app.get("/controllerempt", response_class=HTMLResponse)
async def controller():
    server_page()
@app.websocket("/server/accept")
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
@app.websocket("/ws")
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

# HTTP Endpoint returning HTML
@app.get("/server", response_class=HTMLResponse)
async def server_page():
    custom_html_layout = """<!DOCTYPE html>
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
</html>"""
    
    return HTMLResponse(content=custom_html_layout, status_code=200)
@app.get("/cookie", response_class=HTMLResponse)
async def cookie():
    html_content = cookie_page()
    return HTMLResponse(content=html_content, status_code=200)

# API Route to pull and grab external UUID data
@app.api_route("/api/status/")
async def get_uuid_status(amount: int = Header(..., description="The amount of UUIDs requested")):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="The 'amount' header must be a positive integer greater than 0.")
    if amount > 10000000:
        raise HTTPException(status_code=400, detail="To prevent timeouts, you can pull a maximum of 10000000 UUIDs per request.")
        
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
@app.get("/proxy/{dev_port}", response_class=HTMLResponse)
async def page_404(dev_port: int):
    html = """<!doctype html>
    <html lang="en">
    <head>
        <title>404 Not Found</title>
    </head>
    <body>
        <h1>Not Found</h1>
        <p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
    </body>
    </html>"""
    
    return HTMLResponse(content=html, status_code=404)
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
        return jsonify({"message": "Retrieved endpoint status via GET"}), 200

    return jsonify({"error": "Method not allowed"}), 405
try:
    result = ice()
    print(result)  # Outputs: 1
except Exception as e:
    print({e})
    pass
settings.ROOT_URLCONF = __name__
django_wsgi_app = get_wsgi_application()
app.mount("/", WSGIMiddleware(django_wsgi_app))
django_wsgi_app = get_wsgi_application()

app.mount("/", WSGIMiddleware(django_wsgi_app))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)