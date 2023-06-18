from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
from os import environ
from urllib.parse import urlencode
import aiohttp

load_dotenv()
app = FastAPI()


@app.get("/")
async def blah():
    return RedirectResponse("https://cataas.com/cat/says/not logged in!")


@app.get("/authorize")
async def authorize(
    redirect_uri: str, client_id: str, response_type: str, scope: str, state: str
):
    if redirect_uri != environ["REDIRECT_URI"]:
        raise HTTPException(status_code=400, detail="Invalid redirect_uri")
    if client_id != environ["CLIENT_ID"]:
        raise HTTPException(status_code=400, detail="Invalid client_id")
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Unsupported response_type")

    params = {
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "response_type": "code",
        "scope": "identify email",
        "state": state,
        "prompt": "none",
    }

    return RedirectResponse(
        "https://discord.com/api/oauth2/authorize?" + urlencode(params), status_code=302
    )


@app.post("/token")
async def token(code: str, state: str):
    params = {
        "client_id": environ["CLIENT_ID"],
        "client_secret": environ["CLIENT_SECRET"],
        "redirect_uri": environ["REDIRECT_URI"],
        "code": code,
        "grant_type": "authorization_code",
        "scope": "identify email",
    }

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://discord.com/api/oauth2/token", data=params, headers=headers
        ) as resp:
            token_data = await resp.json()

        token = token_data.get("access_token")
        auth_header = {"Authorization": "Bearer " + token}

        async with session.get(
            "https://discord.com/api/users/@me", data=params, headers=auth_header
        ) as resp:
            user_data = await resp.json()

            print(user_data)
