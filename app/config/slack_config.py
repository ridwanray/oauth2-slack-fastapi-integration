from pydantic_settings import BaseSettings
from decouple import config


class Settings(BaseSettings):
    title: str = "Slack & OAUTH2 Integration"
    CLIENT_ID: str = config("CLIENT_ID")
    CLIENT_SECRET: str = config("CLIENT_SECRET")
    REDIRECT_URI: str = config("REDIRECT_URI")
    SIGNING_SECRET: str = config("SIGNING_SECRET")


settings = Settings()
