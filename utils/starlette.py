from slack_bolt.adapter.starlette.async_handler import AsyncSlackRequestHandler
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

from app import main
from utils.env import env
from utils.slack import app as slack_app

req_handler = AsyncSlackRequestHandler(slack_app)


async def endpoint(req: Request):
    return await req_handler.handle(req)


async def install(req: Request):
    return await req_handler.handle(req)


async def oauth_redirect(req: Request):
    return await req_handler.handle(req)


app = Starlette(
    debug=True if env.environment != "production" else False,
    routes=[
        Route(path="/slack/events", endpoint=endpoint, methods=["POST"]),
        Route(path="/slack/install", endpoint=install, methods=["GET"]),
        Route(path="/slack/oauth_redirect", endpoint=oauth_redirect, methods=["GET"]),
    ],
    lifespan=main,
)
