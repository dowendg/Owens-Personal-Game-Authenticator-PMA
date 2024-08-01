from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import uuid
import time
import urllib.parse
import os
from typing import Optional

app = FastAPI()

# Configuration and in-memory storage
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENTNT_ID = os.getenv("TENTNT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")  # New environment variable for redirect URI

access_token: Optional[str] = None
refresh_token: Optional[str] = None
xbox_live_token: Optional[str] = None
xsts_token: Optional[str] = None
user_hash: Optional[str] = None
mc_token: Optional[str] = None
mc_info: Optional[dict] = None

device_codes = {}

class AuthResponse(BaseModel):
    minecraft_info: Optional[dict] = None
    error: Optional[str] = None

@app.post("/device/code")
async def generate_device_code():
    """Generate a device code and provide a URL for the user to authenticate."""
    device_code = str(uuid.uuid4())
    verification_uri = "https://minecraftauth.example.com/auth/start"  # Corrected URL

    # Store the device code info
    device_codes[device_code] = {
        "status": "pending",
        "expires_at": time.time() + 3600  # 1 hour expiration time
    }

    return JSONResponse({
        "device_code": device_code,
        "verification_uri": verification_uri,
        "expires_in": 3600,
        "interval": 5
    })

@app.get("/device/status")
async def check_device_code_status(device_code: str):
    """Check the status of the device code."""
    if device_code not in device_codes:
        raise HTTPException(status_code=400, detail="Invalid device code")

    code_info = device_codes[device_code]

    if time.time() > code_info["expires_at"]:
        del device_codes[device_code]
        raise HTTPException(status_code=400, detail="Device code expired")

    if code_info["status"] == "complete":
        return JSONResponse({
            "status": "complete",
            "auth_info": code_info.get("auth_info")
        })
    else:
        return JSONResponse({"status": "pending"})

@app.post("/device/complete")
async def complete_authentication(device_code: str):
    """Complete the authentication and store the auth info."""
    if device_code not in device_codes:
        raise HTTPException(status_code=400, detail="Invalid device code")

    code_info = device_codes[device_code]

    if time.time() > code_info["expires_at"]:
        del device_codes[device_code]
        raise HTTPException(status_code=400, detail="Device code expired")

    # Poll the auth server to complete the authentication process
    try:
        response = requests.post("https://minecraftauth.example.com/auth/device_code", json={"device_code": device_code})
        response.raise_for_status()
        auth_response = response.json()

        if "error" in auth_response:
            raise RuntimeError(auth_response["error"])

        # Mark the device code as complete and store the authentication info
        code_info["status"] = "complete"
        code_info["auth_info"] = auth_response

        return JSONResponse({
            "status": "complete",
            "auth_info": auth_response
        })
    except Exception as e:
        code_info["status"] = "error"
        return JSONResponse({
            "status": "error",
            "error": str(e)
        })

@app.get('/auth/start')
async def start_auth():
    """Start the authentication process by providing the authorization URL."""
    url = "https://login.live.com/oauth20_authorize.srf?"
    url += urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,  # Use environment variable
        'scope': 'XboxLive.signin offline_access',
        'state': 'NOT_NEEDED'
    })

    return JSONResponse({'auth_url': url})

@app.get('/auth/callback')
async def handle_callback(code: str):
    """Handle the callback from the authentication provider."""
    if code:
        try:
            await process_authentication(code)
            return JSONResponse({'status': 'success', 'message': 'Authentication successful'})
        except Exception as e:
            return JSONResponse({'status': 'error', 'message': str(e)}, status_code=500)
    else:
        return JSONResponse({'status': 'error', 'message': 'No code parameter provided.'}, status_code=400)

@app.post('/auth/device_code')
async def device_code(device_code: str):
    """Provide the device code with authentication info."""
    if not access_token:
        raise HTTPException(status_code=400, detail="Authentication process not completed.")

    # Return the authentication info to the device code server
    return JSONResponse({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'xbox_live_token': xbox_live_token,
        'xsts_token': xsts_token,
        'user_hash': user_hash,
        'mc_token': mc_token,
        'mc_info': mc_info
    })

async def process_authentication(code: str) -> None:
    """Complete the authentication process using the provided code."""
    global access_token, refresh_token, xbox_live_token, xsts_token, user_hash, mc_token, mc_info

    if refresh_token:
        access_token = await refresh_access_token()
    else:
        access_token = await get_access_token(code)

    xbox_live_token = await get_xbox_live_token()
    xsts_token, user_hash = await get_xsts_token()
    mc_token = await get_mc_token()
    await get_mc_info()

async def get_access_token(login_code: str) -> str:
    """Obtain access token from the authentication code."""
    global access_token
    response = requests.post("https://login.live.com/oauth20_token.srf", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': login_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,  # Use environment variable
        'tentnt_id': TENTNT_ID
    }).json()

    access_token = response.get('access_token')
    refresh_token = response.get('refresh_token')
    if not access_token:
        raise RuntimeError('Failed to obtain access token.')

    return access_token

async def refresh_access_token() -> str:
    """Refresh the access token using the refresh token."""
    global access_token
    global refresh_token
    if not refresh_token:
        raise RuntimeError('No refresh token available.')

    response = requests.post("https://login.live.com/oauth20_token.srf", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'redirect_uri': REDIRECT_URI,  # Use environment variable
        'tentnt_id': TENTNT_ID
    }).json()

    access_token = response.get('access_token')
    if not access_token:
        raise RuntimeError('Failed to refresh access token.')

    return access_token

async def get_xbox_live_token() -> str:
    """Obtain Xbox Live token using the access token."""
    global xbox_live_token
    response = requests.post('https://user.auth.xboxlive.com/user/authenticate', json={
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": 'd=' + access_token
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "TentntId": TENTNT_ID
    }).json()

    xbox_live_token = response.get('Token')
    if not xbox_live_token:
        raise RuntimeError('Failed to obtain Xbox Live token.')

    return xbox_live_token

async def get_xsts_token() -> tuple[str, str]:
    """Obtain XSTS token and user hash using Xbox Live token."""
    global xsts_token
    global user_hash
    response = requests.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [xbox_live_token]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT",
        "TentntId": TENTNT_ID
    }).json()

    xsts_token = response.get('Token')
    user_hash = response.get('DisplayClaims', {}).get('xui', [{}])[0].get('uhs')
    if not xsts_token or not user_hash:
        raise RuntimeError('Failed to obtain XSTS token or user hash.')

    return xsts_token, user_hash

async def get_mc_token() -> str:
    """Obtain Minecraft token using the XSTS token and user hash."""
    global mc_token
    payload = {
        "identityToken": f"XBL3.0 x={user_hash};{xsts_token}",
        "ensureLegacyEnabled": True,
        "TentntId": TENTNT_ID
    }
    response = requests.post('https://api.minecraftservices.com/authentication/login_with_xbox', json=payload).json()

    mc_token = response.get('access_token')
    if not mc_token:
        raise RuntimeError('Failed to obtain Minecraft token.')

    return mc_token

async def get_mc_info() -> None:
    """Obtain Minecraft user information using the Minecraft token."""
    global mc_info
    response = requests.get('https://api.minecraftservices.com/minecraft/profile', headers={
        'Authorization': f'Bearer {mc_token}'
    }).json()

    mc_info = response
    if not mc_info:
        raise RuntimeError('Failed to obtain Minecraft user information.')
