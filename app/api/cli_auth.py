import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, UTC
from typing import Dict, Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from app.utils import load_users, save_users, normalize_username, verify_password

router = APIRouter()

# In-memory state for CLI authentication
auth_sessions: Dict[str, dict] = {}
failed_logins: Dict[str, dict] = {}

# Configuration
MAX_ACTIVE_SESSIONS = 100
CLI_TOKEN_TTL = 10  # minutes
MAX_FAILED_ATTEMPTS = 5
FAILED_ATTEMPTS_WINDOW = 10  # minutes

class AuthVerifyRequest(BaseModel):
    cli_token: str
    username: str
    password: str

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def is_rate_limited(ip: str) -> bool:
    """Check if IP is rate limited due to failed login attempts."""
    if ip not in failed_logins:
        return False
    
    attempt_data = failed_logins[ip]
    window_start = datetime.now(UTC) - timedelta(minutes=FAILED_ATTEMPTS_WINDOW)
    
    if attempt_data["last_attempt"] < window_start:
        # Reset if outside window
        del failed_logins[ip]
        return False
    
    return attempt_data["count"] >= MAX_FAILED_ATTEMPTS

def record_failed_attempt(ip: str):
    """Record a failed login attempt for rate limiting."""
    now = datetime.now(UTC)
    if ip not in failed_logins:
        failed_logins[ip] = {"count": 0, "last_attempt": now}
    
    failed_logins[ip]["count"] += 1
    failed_logins[ip]["last_attempt"] = now

def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_hex(32)

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()

def cleanup_expired_sessions():
    """Remove expired CLI tokens from memory."""
    now = datetime.now(UTC)
    expired_tokens = [
        token for token, session in auth_sessions.items()
        if session["expires_at"] < now
    ]
    for token in expired_tokens:
        del auth_sessions[token]

@router.post("/auth/init")
async def init_cli_auth(request: Request):
    """Initialize CLI authentication by generating a token."""
    cleanup_expired_sessions()
    
    if len(auth_sessions) >= MAX_ACTIVE_SESSIONS:
        raise HTTPException(status_code=429, detail="Too many active sessions")
    
    cli_token = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=CLI_TOKEN_TTL)
    
    auth_sessions[cli_token] = {
        "expires_at": expires_at,
        "username": None,
        "raw_api_key": None,
        "completed": False
    }
    
    base_url = str(request.base_url).rstrip("/")
    login_url = f"{base_url}/cli-login?cli_token={cli_token}"
    
    return {
        "cli_token": cli_token,
        "login_url": login_url
    }

@router.post("/auth/verify")
async def verify_cli_auth(request: Request, auth_data: AuthVerifyRequest):
    """Verify CLI authentication credentials and generate API key."""
    client_ip = get_client_ip(request)
    
    if is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Too many failed attempts")
    
    # Validate CLI token
    if auth_data.cli_token not in auth_sessions:
        record_failed_attempt(client_ip)
        raise HTTPException(status_code=400, detail="Invalid CLI token")
    
    session = auth_sessions[auth_data.cli_token]
    if session["expires_at"] < datetime.now(UTC):
        del auth_sessions[auth_data.cli_token]
        record_failed_attempt(client_ip)
        raise HTTPException(status_code=400, detail="CLI token expired")
    
    # Validate credentials
    username = normalize_username(auth_data.username)
    users = load_users()
    user_data = users.get(username)
    
    if not user_data or not verify_password(auth_data.password, user_data["password_hash"]):
        record_failed_attempt(client_ip)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate API key
    api_key = generate_api_key()
    api_key_hash = hash_api_key(api_key)
    
    # Store API key hash in user data
    if "api_keys" not in user_data:
        user_data["api_keys"] = []
    user_data["api_keys"].append(api_key_hash)
    save_users(users)
    
    # Update session
    session["username"] = username
    session["raw_api_key"] = api_key
    session["completed"] = True
    
    return {"message": "Authentication successful"}

@router.get("/auth/status")
async def get_auth_status(cli_token: str):
    """Get authentication status and return API key if completed."""
    if cli_token not in auth_sessions:
        raise HTTPException(status_code=400, detail="Invalid CLI token")
    
    session = auth_sessions[cli_token]
    if session["expires_at"] < datetime.now(UTC):
        del auth_sessions[cli_token]
        raise HTTPException(status_code=400, detail="CLI token expired")
    
    if not session["completed"]:
        raise HTTPException(status_code=401, detail="Authentication not completed")
    
    # Return API key and immediately delete session
    result = {
        "username": session["username"],
        "api_key": session["raw_api_key"]
    }
    
    del auth_sessions[cli_token]
    return result 