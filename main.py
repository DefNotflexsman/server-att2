import os
import httpx
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse

app = FastAPI(title="UUID Generator Site")

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
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


# API Route to pull and grab external UUID data
@app.get("/API/status/")
async def get_uuid_status(amount: int = Header(..., description="The amount of UUIDs requested")):
    # Safety verification: ensure users ask for at least 1 and don't overwhelm the thread
    if amount <= 0:
        raise HTTPException(status_code=400, detail="The 'amount' header must be a positive integer greater than 0.")
    if amount > 100:
        raise HTTPException(status_code=400, detail="To prevent timeouts, you can pull a maximum of 100 UUIDs per request.")
        
    external_url = f"https://www.uuidtools.com/api/generate/v1/count/{amount}"
    
    # Asynchronously grab data from the external API safely
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_url)
            
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to retrieve data from the upstream UUID engine.")
                
            uuids_list = response.json()
            
            # Map the response out into clean JSON format for client rendering
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
    # Render sets the PORT environment variable automatically dynamically
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
