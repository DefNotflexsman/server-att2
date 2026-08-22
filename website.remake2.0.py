import subprocess
import os
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

app = FastAPI(title="Python UUID Portal")

# Global CSS variables matching your modern dark dashboard theme
CSS_CONTENT = """
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
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    background-color: var(--bg-primary);
    color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    padding: 3rem 1rem;
}
.container { max-width: 700px; margin: 0 auto; }
header { margin-bottom: 2.5rem; }
h1 { font-size: 2.2rem; font-weight: 700; margin-bottom: 0.75rem; letter-spacing: -0.025em; }
p { color: var(--text-secondary); margin-bottom: 1.25rem; font-size: 1.05rem; }
.box {
    background-color: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
}
h3 { font-size: 1.3rem; margin-bottom: 1.25rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
.box p { color: var(--text-secondary); margin-bottom: 0.75rem; font-size: 1rem; }
code {
    font-family: monospace;
    font-size: 0.9rem;
    color: #e2e8f0;
    background-color: var(--code-bg);
    border: 1px solid var(--border);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
}
.nav-link {
    display: inline-block;
    background-color: var(--bg-secondary);
    color: var(--text-primary);
    text-decoration: none;
    padding: 0.6rem 1.2rem;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    font-weight: 500;
    transition: var(--transition);
}
.nav-link:hover {
    background-color: var(--accent);
    border-color: var(--accent);
    transform: translateY(-1px);
}
@media (max-width: 640px) {
    body { padding: 1.5rem 0.5rem; }
    h1 { font-size: 1.8rem; }
}
"""

# 1. Plain Text Route to cleanly serve the CSS stylesheet
@app.get("/style.css", response_class=PlainTextResponse)
async def get_style():
    return PlainTextResponse(content=CSS_CONTENT, media_type="text/css")

# 2. Main Root Endpoint displaying your API info panel
@app.get("/", response_class=HTMLResponse)
async def home_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Python UUID Portal</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Welcome to the Python UUID Web Portal</h1>
                    <p>This entire platform is built natively using 100% Python.</p>
                </header>
                
                <div class="box">
                    <h3>API Endpoint Documentation</h3>
                    <p><strong>Route:</strong> <code>/API/status/</code></p>
                    <p><strong>Method:</strong> <code>GET</code></p>
                    <p><strong>Required Header:</strong> <code>amount</code> (Integer specifying how many UUIDs to pull)</p>
                </div>
                
                <p>To pull data, request the route using a tool like cURL or a local script by specifying your desired count value inside the request headers.</p>
                <p>Visit the new page layout here: <a href="/server" class="nav-link">/server</a></p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

# 3. Secure API Endpoint using Header validation
@app.get("/API/status/")
async def get_status(amount: int = Header(default=None)):
    if amount is None:
        raise HTTPException(status_code=400, detail="Missing required header: 'amount'")
    
    # Generate UUID strings using a subprocess shell loop as requested
    try:
        uuids = []
        for _ in range(min(amount, 100)):  # Guardrail capped at 100 items max
            result = subprocess.run(["uuidgen"], capture_output=True, text=True, check=True)
            uuids.append(result.stdout.strip())
        return {"status": "success", "requested_amount": amount, "data": uuids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal subprocess failure: {str(e)}")

# 4. Asynchronous Dashboard Proxy Route using httpx
@app.get("/server", response_class=HTMLResponse)
async def proxy_server_dashboard():
    target_url = "https://server-att2-tzvi.onrender.com/"
    
    async with httpx.AsyncClient() as client:
        try:
            # Attempt to fetch content from the external rendering server
            response = await client.get(target_url, timeout=5.0)
            if response.status_code == 200:
                return HTMLResponse(content=response.text, status_code=200)
        except Exception:
            pass  # Fallback to local layout below if external network is offline
            
    # Local fallback layout when rendering server is unavailable
    fallback_html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Server Dashboard - Fallback</title>
            <link rel="stylesheet" href="/style.css">
        </head>
        <body>
            <div class="container">
                <h1>Server Dashboard</h1>
                <div class="box">
                    <h3>System State: Offline</h3>
                    <p>Could not connect to external service proxy host at this moment.</p>
                </div>
                <a href="/" class="nav-link">Return Home</a>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=fallback_html, status_code=200)
