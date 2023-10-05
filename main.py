from fastapi import FastAPI
from app.config.slack_config import settings
from fastapi.middleware.cors import CORSMiddleware
from app.api import slack

app = FastAPI(
    title=settings.title,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(slack.router, tags=["Slack-integration"])
