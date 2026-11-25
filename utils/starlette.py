import html
import logging

from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route

from app import main
from app import publish_home
from utils.db import update_user_settings
from utils.env import env
from utils.lastfm_auth import CALLBACK_PATH
from utils.lastfm_auth import get_session
from utils.lastfm_auth import read_state
from utils.slack import app as slack_app

req_handler = AsyncSlackRequestHandler(slack_app)


async def endpoint(req: Request):
    return await req_handler.handle(req)


async def install(req: Request):
    return await req_handler.handle(req)


async def oauth_redirect(req: Request):
    return await req_handler.handle(req)


def lastfm_page(message: str, status_code: int = 200) -> HTMLResponse:
    html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>Slick Stats</title></head>"
        "<body style='font-family: sans-serif; text-align: center; padding: 4rem 1rem'>"
        f"<h1>Slick Stats</h1><p>{message}</p></body></html>"
    )
    return HTMLResponse(html, status_code=status_code)


async def lastfm_callback(req: Request):
    """Last.fm sends the user back here with ?token=... after they allow access"""
    if not env.lastfm_enabled:
        return lastfm_page("Last.fm isn't set up on this server.", 503)

    user_id = read_state(req.path_params.get("state", ""))
    if not user_id:
        return lastfm_page(
            "This link has expired. Open Slick Stats in Slack and press Connect Last.fm again.",
            400,
        )

    token = req.query_params.get("token")
    if not token:
        return lastfm_page(
            "Last.fm didn't send a sign in token. Please try again.", 400
        )

    session = await get_session(token)
    if not session or not session.get("name") or not session.get("key"):
        return lastfm_page("Couldn't connect to Last.fm. Please try again.", 502)

    await update_user_settings(
        user_id,
        {
            "lastfm_username": session["name"],
            "lastfm_session_key": session["key"],
            # Personal API keys stop working for free accounts from 1 Dec 2026
            "lastfm_api_key": None,
        },
    )
    try:
        await publish_home(user_id)
    except Exception as e:
        logging.error(f"Couldn't refresh home tab after Last.fm connect: {e}")

    return lastfm_page(
        f"Connected Last.fm as <b>{html.escape(session['name'])}</b>. You can close this tab and head back to Slack."
    )


app = Starlette(
    debug=True if env.environment != "production" else False,
    routes=[
        Route(path="/slack/events", endpoint=endpoint, methods=["POST"]),
        Route(path="/slack/install", endpoint=install, methods=["GET"]),
        Route(path="/slack/oauth_redirect", endpoint=oauth_redirect, methods=["GET"]),
        Route(
            path=CALLBACK_PATH + "/{state}", endpoint=lastfm_callback, methods=["GET"]
        ),
    ],
    lifespan=main,
)
