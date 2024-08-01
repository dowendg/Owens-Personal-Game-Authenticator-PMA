from __future__ import annotations

import json
import time
import urllib.parse
import webbrowser
from pathlib import Path
from threading import Thread
from typing import Optional, Dict, Any

import requests
import uvicorn
from fastapi import FastAPI
from hypy_utils import printc

__version__ = "1.0.5"

# Set base and data directories
base_path = Path('./config')

# In-memory storage for tokens and other data
access_token: Optional[str] = None
refresh_token: Optional[str] = None
xbox_live_token: Optional[str] = None
xsts_token: Optional[str] = None
user_hash: Optional[str] = None
mc_token: Optional[str] = None
mc_info: Optional[dict] = None

# Hardcoded credentials
CLIENT_ID = "YOUR CLIENT ID"
CLIENT_SECRET = "YOUR CLIENT SCERECT"
TENTNT_ID = "YOUR tentnt_id"  # Updated tentnt_id

def get_login_code() -> str:
    app = FastAPI()
    result = {}

    @app.get('/')
    def callback(code: str):
        printc('&a> Login code received!')
        result['code'] = code
        return 'Login success! You can close this window now.'

    def run():
        uvicorn.run(app, host="0.0.0.0", port=18275, reload=False, log_level='error')

    th = Thread(target=run, daemon=True)
    th.start()

    # Open URL in browser
    url = "https://login.live.com/oauth20_authorize.srf?"
    url += urllib.parse.urlencode({
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': '[your api domain]/auth/callback',
        'scope': 'XboxLive.signin offline_access',
        'state': 'NOT_NEEDED'
    })
    print(f'Opening {url} in the browser...')
    if not webbrowser.open(url):
        printc(f'&cFailed to open the link automatically, please open it manually.')

    while 'code' not in result:
        time.sleep(0.01)

    return result['code']

def get_access_token(login_code: str) -> str:
    global access_token
    printc('&6Getting access token with login code...')

    r = requests.post("https://login.live.com/oauth20_token.srf", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': login_code,
        'grant_type': 'authorization_code',
        'redirect_uri': '[your api domain]/auth/callback',
        'tentnt_id': TENTNT_ID  # Include tentnt_id in the request
    }).json()

    printc(f'&6Response: {json.dumps(r, indent=2)}')

    access_token = r.get('access_token')
    refresh_token = r.get('refresh_token')
    if not access_token:
        raise ValueError('Request failed. Access token is not in the response.')

    printc(f'&a> Success! Access token received.')
    return access_token

def refresh_access_token() -> str:
    global access_token
    global refresh_token
    if not refresh_token:
        raise ValueError('No refresh token available.')

    printc('&6Refreshing access token with refresh token...')

    r = requests.post("https://login.live.com/oauth20_token.srf", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'redirect_uri': '[your api domain]/auth/callback',
        'tentnt_id': TENTNT_ID  # Include tentnt_id in the request
    }).json()

    printc(f'&6Response: {json.dumps(r, indent=2)}')

    access_token = r.get('access_token')
    if not access_token:
        raise ValueError('Request failed. Access token is not in the response.')

    printc(f'&a> Success! Access token refreshed.')
    return access_token

def get_xbox_live_token() -> str:
    global xbox_live_token
    printc('&6Logging into Xbox Live with access token...')

    r = requests.post('https://user.auth.xboxlive.com/user/authenticate', json={
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": 'd=' + access_token
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT",
        "TentntId": TENTNT_ID  # Include tentnt_id in the request
    }).json()

    printc(f'&6Response: {json.dumps(r, indent=2)}')

    xbox_live_token = r.get('Token')
    if not xbox_live_token:
        raise ValueError('Request failed. Xbox Live token is not in the response.')

    printc(f'&a> Success! Xbox Live token received.')
    return xbox_live_token

def get_xsts_token() -> tuple[str, str]:
    global xsts_token
    global user_hash
    printc('&6Logging into XSTS with Xbox Live token...')

    r = requests.post('https://xsts.auth.xboxlive.com/xsts/authorize', json={
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [xbox_live_token]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT",
        "TentntId": TENTNT_ID  # Include tentnt_id in the request
    }).json()

    printc(f'&6Response: {json.dumps(r, indent=2)}')

    xsts_token = r.get('Token')
    user_hash = r.get('DisplayClaims', {}).get('xui', [{}])[0].get('uhs')
    if not xsts_token or not user_hash:
        raise ValueError('Request failed. XSTS token or user hash is not in the response.')

    printc(f'&a> Success! XSTS token received.')
    return xsts_token, user_hash

def get_mc_token() -> str:
    global mc_token
    printc('&6Logging into Minecraft with XSTS token...')

    # Prepare the JSON payload
    payload = {
        "identityToken": f"XBL3.0 x={user_hash};{xsts_token}",
        "ensureLegacyEnabled": True,
        "TentntId": TENTNT_ID  # Include tentnt_id in the request
    }

    # Make the POST request
    r = requests.post(
        'https://api.minecraftservices.com/authentication/login_with_xbox',
        json=payload,
        headers={'Content-Type': 'application/json'}
    ).json()

    printc(f'&6Response: {json.dumps(r, indent=2)}')

    # Extract the access token from the response
    mc_token = r.get('access_token')
    if not mc_token:
        raise ValueError('Request failed. Minecraft token is not in the response.')

    printc(f'&a> Success! Minecraft token received.')
    return mc_token

def get_mc_info() -> None:
    global mc_info
    printc('&6Getting Minecraft username and UUID...')

    r = requests.get('https://api.minecraftservices.com/minecraft/profile',
                     headers={'Authorization': f'Bearer {mc_token}', 'TentntId': TENTNT_ID}).json()

    printc(f'&6Response: {json.dumps(r, indent=2)}')

    mc_info = r
    if 'id' not in r or 'name' not in r:
        raise ValueError('Request failed. Minecraft UUID or name is not in the response.')

    printc(f'&a> Success! Logged in as {r["name"]}')

def full_login():
    printc(f'&3mc-authn {__version__} by HyDEV')
    print()

    global access_token
    global refresh_token
    global xbox_live_token
    global xsts_token
    global user_hash
    global mc_token
    global mc_info

    refresh_token = None
    access_token = None
    xbox_live_token = None
    xsts_token = None
    user_hash = None
    mc_token = None
    mc_info = None

    try:
        if refresh_token:
            access_token = refresh_access_token()
        else:
            code = get_login_code()
            access_token = get_access_token(code)

        xbox_live_token = get_xbox_live_token()
        xsts_token, user_hash = get_xsts_token()
        mc_token = get_mc_token()
        get_mc_info()

    except Exception as e:
        printc(f'&cError: {e}')

if __name__ == '__main__':
    full_login()
