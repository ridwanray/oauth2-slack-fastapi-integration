import secrets
from urllib.parse import urlencode

import aiohttp
from fastapi import HTTPException


class SlackIntegration:
    slack_api_base_url = "https://slack.com/api/"
    access_token = None

    def __init__(self, client_id, client_secret, redirect_uri):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def build_authorization_url(self, scopes: list):
        authorization_url = f"https://slack.com/oauth/v2/authorize"
        params = {
            "client_id": self.client_id,
            "user_scope": ",".join(scopes),
            "state": self.generate_state(),
            "redirect_uri": self.redirect_uri,
        }
        return f"{authorization_url}?{urlencode(params)}"

    def generate_state(self) -> str:
        return secrets.token_urlsafe(20)

    async def post_authorize_call(self, code: str):
        token_url = f"{self.slack_api_base_url}oauth.v2.access"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=payload) as response:
                response_data: dict = await response.json()

        if response.status == 200 and response_data.get("ok"):
            self.access_token = response_data.get("authed_user").get("access_token")
            return {
                "protected_data": response_data.get("authed_user"),
                "metadata": response_data.get("team"),
                "consent_user": response_data.get("authed_user").get("id"),
                "access_token": response_data.get("authed_user").get("access_token"),
            }

        raise HTTPException(status_code=400, detail=response_data.get("error"))

    async def make_slack_api_request(self, method: str, token=None, params=None):
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {str(token)}",
            "Content-Type": "application/json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.slack_api_base_url}{method}", headers=headers, params=params
            ) as response:
                response_data = await response.json()
        if response.status == 200 and response_data.get("ok"):
            return response_data
        raise HTTPException(status_code=400, detail=response_data.get("error"))

    async def verify_authorization_connection(self, code: str):
        token_url = "https://slack.com/api/oauth.v2.access"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=payload) as response:
                response_data = await response.json()
        if response.status == 200 and response_data.get("ok"):
            return True
        return False

    async def handle_event(self, event_data: dict):
        """Handle an incoming file event from slack"""
        event_data = event_data.get("event")
        if event_data.get("type") == "file_shared":
            file_id = event_data.get("file_id")
            print(
                f"FileID: {file_id}, UserID: {event_data.get('user_id')}, Timestamp: {event_data.get('event_ts')}"
            )

            # Only fetch file data if a valid token from a previous authentication request is available
            if self.access_token:
                # Get file info
                file_response = await self.make_slack_api_request(
                    "files.info", self.access_token, params={"file": file_id}
                )
                file_data: dict = file_response.get("file")

                print(
                    "User:",
                    file_data.get("user"),
                    "FileSize:",
                    file_data.get("size"),
                    "FileType:",
                    file_data.get("filetype"),
                    "TimeStamp",
                    file_data.get("timestamp"),
                )

                # Download and save file
                private_download_url: str = file_response["file"][
                    "url_private_download"
                ]
                headers = {"Authorization": f"Bearer {self.access_token}"}
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        private_download_url, headers=headers
                    ) as response:
                        if response.status == 200:
                            file_content = await response.read()
                            file_path = f"app/{file_id}.{file_data.get('filetype')}"
                            with open(file_path, "wb") as file:
                                file.write(file_content)
                            print(f"File saved to: {file_path}")
                        else:
                            print(
                                f"Failed to download file with status code: {response.status}"
                            )
