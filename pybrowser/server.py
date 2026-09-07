import os
import sys
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from a2wsgi import WSGIApp

# 1. Import your FastAPI app from main.py
from main import app as main_app

# 2. Import your WebSocket PTY router/app if separate
try:
    from web_terminal import app as terminal_app
    main_app.mount("/ws", terminal_app)
except ImportError:
    pass

# 3. Wrap legacy CGI handling into WSGI so ASGI servers can run it
class LegacyCGIWSGI:
    """Simple WSGI wrapper around Python's CGIHTTPRequestHandler."""
    def __init__(self, cgi_directories):
        self.cgi_directories = cgi_directories

    def __call__(self, environ, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [b"CGI Handler active"]

# Mount legacy CGI WSGI application
cgi_asgi_app = WSGIApp(LegacyCGIWSGI(cgi_directories=['/cgi-bin']))
main_app.mount("/cgi-bin", cgi_asgi_app)


# =====================================================================
# ADD YOUR EXPLICIT API / APPLICATION ROUTES HERE (BEFORE STATIC MOUNT)
# =====================================================================

@main_app.get("/")
def root():
    return {"status": "online", "message": "Python Browser & Web Terminal running"}

# Add any additional custom endpoints here so they are processed first:
# @main_app.get("/api/my-endpoint")
# def my_endpoint():
#     return {"data": "success"}


# =====================================================================
# 4. MOUNT STATIC DIRECTORY LAST
# =====================================================================
# Mounting this last ensures defined routes take priority over static file checks
if os.path.exists("static"):
    main_app.mount("/static", StaticFiles(directory="static"), name="static")

# Expose 'app' at module level for Uvicorn
app = main_app

if __name__ == '__main__':
    default_port = int(os.environ.get('PORT', 8440))
    
    parser = argparse.ArgumentParser(description='Run Combined ASGI Server.')
    parser.add_argument('--host', default='0.0.0.0', help='Host address')
    parser.add_argument('--port', type=int, default=default_port, help='Server port')
    args = parser.parse_args()

    uvicorn.run("server:app", host=args.host, port=args.port, reload=True)