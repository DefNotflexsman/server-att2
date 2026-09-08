import os
import sys
import time
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Any, Dict

import httpx
import uvicorn
from fastapi import (
    FastAPI,
    Request,
    Header,
    Query,
    Path,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    status,
)
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

# --- CONFIGURATION & SECURITY ---
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-jwt-key-change-in-production")
API_KEY = os.environ.get("API_KEY", "default_secret_api_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(
    debug=False,
    title="Asynchronous Portal Engine",
    description="Clean, fully standardized FastAPI service",
)

# --- PYDANTIC MODELS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    full_name: Optional[str] = None
    is_admin: bool = False

class ItemResponse(BaseModel):
    item_id: int
    name: str

class StatusResponse(BaseModel):
    status: str
    message: str

class UUIDResponse(BaseModel):
    status: str
    requested_amount: int
    uuids: List[str]

class ProcessResponse(BaseModel):
    status: str
    message: str
    pid: int
    initiated_by: Optional[str] = None

class ParsedRequestDetails(BaseModel):
    path: str
    method: str
    client_ip: Optional[str]
    headers: Dict[str, str]
    query_params: Dict[str, str]
    timestamp: str

# --- MOCK USER DATABASE ---
fake_users_db = {
    "admin": {
        "username": "admin",
        "full_name": "Portal Admin",
        "hashed_password": pwd_context.hash("secret123"),
        "is_admin": True,
    }
}

# --- AUTHENTICATION HELPERS ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_dict = fake_users_db.get(username)
    if user_dict is None:
        raise credentials_exception

    return User(
        username=user_dict["username"],
        full_name=user_dict["full_name"],
        is_admin=user_dict["is_admin"],
    )

async def verify_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key header (X-API-Key).",
        )
    return x_api_key

# --- REQUEST PARSING PIPELINE ---
async def parse_api_request(request: Request) -> ParsedRequestDetails:
    """Utility function to extract and format request metadata."""
    return ParsedRequestDetails(
        path=request.url.path,
        method=request.method,
        client_ip=request.client.host if request.client else "Unknown",
        headers={k: v for k, v in request.headers.items()},
        query_params={k: v for k, v in request.query_params.items()},
        timestamp=datetime.utcnow().isoformat(),
    )

async def get_parsed_request(request: Request) -> ParsedRequestDetails:
    """Dependency injection to get parsed request context inside route handlers."""
    if hasattr(request.state, "parsed_request"):
        return request.state.parsed_request
    return await parse_api_request(request)

# --- CUSTOM EXCEPTIONS & MIDDLEWARE ---
class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": f"Item with ID {exc.item_id} does not exist."},
    )

@app.middleware("http")
async def process_performance_and_log_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Check if request path targets an API endpoint
    if request.url.path.startswith("/api/"):
        parsed = await parse_api_request(request)
        request.state.parsed_request = parsed
        print(f"[API PARSER] Method: {parsed.method} | Path: {parsed.path} | IP: {parsed.client_ip}")

    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# --- API ENDPOINTS ---

@app.post("/api/request", tags=["API Parser"])
async def inspect_request_endpoint(
    parsed: ParsedRequestDetails = Depends(get_parsed_request)
):
    """Explicit endpoint to view parsed metadata for the incoming request."""
    return {
        "status": "success",
        "parsed_request": parsed
    }


@app.post("/token", response_model=Token, tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Obtain an OAuth2 Bearer JWT token."""
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict or not verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_dict["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/items/{item_id}", response_model=ItemResponse, tags=["Items"])
async def read_item(item_id: int = Path(..., ge=1, description="The ID of the item to retrieve")):
    """Get item details by ID."""
    if item_id > 100:
        raise ItemNotFoundException(item_id=item_id)
    return {"item_id": item_id, "name": f"Sample Item #{item_id}"}


@app.get("/api/status", response_model=UUIDResponse, tags=["External APIs"])
async def get_uuid_status(
    amount: int = Query(10, ge=1, le=1000, description="Amount of UUIDs to generate")
):
    """Fetch generated UUIDs from upstream API."""
    external_url = f"https://www.uuidtools.com/api/generate/v1/count/{amount}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(external_url, timeout=10.0)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY, 
                    detail="Failed to retrieve data from the upstream UUID engine."
                )
            return {
                "status": "success",
                "requested_amount": amount,
                "uuids": response.json(),
            }
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail=f"Network error: {exc}"
            )


@app.get("/api/authentication", response_model=StatusResponse, tags=["Auth"])
async def get_auth_status(api_key: str = Depends(verify_api_key)):
    """Validate header-based API key authentication."""
    return {"status": "ok", "message": "Service authentication valid."}


@app.get("/api/endpoint/test", tags=["Testing"])
async def handle_api_get():
    """Handled GET status endpoint."""
    return {"message": "Retrieved endpoint status via GET"}


@app.post("/api/endpoint/test", status_code=status.HTTP_201_CREATED, tags=["Testing"])
async def handle_api_post():
    """Handled POST creation endpoint."""
    return {"message": "Resource created via POST"}


@app.get("/api/admin/metrics", tags=["Admin"])
async def get_admin_statistics(current_user: User = Depends(get_current_user)):
    """Protected admin metrics route (Requires JWT)."""
    return {
        "status": "success",
        "requested_by": current_user.username,
        "metrics": {"uptime": "99.9%", "active_nodes": 4, "requests_processed": 1024},
    }


@app.post("/api/server/mc", response_model=ProcessResponse, tags=["Admin"])
async def launch_minecraft_server(current_user: User = Depends(get_current_user)):
    """Trigger background server launch (Protected)."""
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, "-c", "import time; time.sleep(10)",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return {
            "status": "success",
            "message": "Background server process initiated successfully.",
            "pid": process.pid,
            "initiated_by": current_user.username,
        }
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to launch background process: {str(err)}",
        )


# --- HTML & WEBSOCKET ENDPOINTS ---

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home_endpoint():
    return HTMLResponse(content="<h1>Welcome to the Portal Service</h1>", status_code=200)


@app.get("/admindashboard", response_class=HTMLResponse, include_in_schema=False)
async def admin_dashboard():
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head><title>Admin Dashboard</title></head>
        <body style="font-family: sans-serif; background: #121214; color: #fff; padding: 40px;">
            <h1>Native FastAPI Control Panel</h1>
            <p>Status: All API routes structured and verified.</p>
        </body>
        </html>
        """,
        status_code=200,
    )


@app.websocket("/ws")
@app.websocket("/server/accept")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Server received: {data}")
    except WebSocketDisconnect:
        print("[WS] Client disconnected")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)