from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks

from app.config.slack_config import settings
from app.schemas.slack_schemas import (
    AuthorizationResponse,
    GetAppsRes,
    GetUsersPageRes,
    SlackEventRes,
    UserRecord,
    VerifyConnectionResponse,
    CallPostAuthorizeRes,
)
from app.utils.dependencies import verify_token, verify_event
from app.utils.slack_utils import SlackIntegration

router = APIRouter()

slack_integration = SlackIntegration(
    client_id=settings.CLIENT_ID,
    client_secret=settings.CLIENT_SECRET,
    redirect_uri=settings.REDIRECT_URI,
)


@router.get("/authorize", response_model=AuthorizationResponse)
async def authorize():
    """Return the authorization url"""
    scopes = [
        "users:read",
        "files:read",
        "users:read.email",
    ]
    authorization_url = slack_integration.build_authorization_url(scopes)
    return {"authorization_url": authorization_url}


@router.get("/post-authorize", response_model=CallPostAuthorizeRes)
async def post_authorize(code: str):
    """Return the access token to access Slack along with metadata"""
    data = await slack_integration.post_authorize_call(code)
    return data


@router.get("/get-users", response_model=GetUsersPageRes)
async def get_users(page_token: str, auth_token: str = Depends(verify_token)):
    # Note: To retrieve a valid `page_token` for testing purposes, set only the `limit` parameter as params.
    # The `limit` should be a small value depending on the number of users in the integration.
    # The retrieved `page_token` can then be used for testing pagination.
    params = {"cursor": page_token}
    response: dict = await slack_integration.make_slack_api_request(
        "users.list", auth_token, params
    )
    users = [
        UserRecord(
            org_id=member.get("team_id"),
            user_id=member.get("id"),
            primary_email=member.get("profile").get("email"),
            is_admin=member.get("is_admin"),
            name={
                "givenName": member.get("profile").get("first_name"),
                "familyName": member.get("profile").get("last_name"),
                "fullName": member.get("profile").get("real_name"),
            },
            user_photo={
                "file_name": member.get("profile").get("image_24"),
            },
        )
        for member in response.get("members")
    ]
    return {
        "users": users,
        "page_token": page_token,
        "next_page_token": response.get("response_metadata").get("next_cursor"),
    }


@router.get("/get-apps/{org_id}", response_model=GetAppsRes)
async def get_apps_per_org(org_id: str):
    # This API requires that the app is created by an admin (admin scope).
    return {"apps": []}


@router.get("/verify-connection", response_model=VerifyConnectionResponse)
async def verify_connection(code: str):
    connection_verified = await slack_integration.verify_authorization_connection(code)
    return {"connection_verified": connection_verified}


@router.post("/slack-events", response_model=SlackEventRes)
async def slack_events(
    request: Request, background_tasks: BackgroundTasks, event_data: dict = {}
):
    """Receive and process Slack events."""
    slack_signature = request.headers.get("X-Slack-Signature", "")
    slack_timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    if not verify_event(slack_signature, slack_timestamp, event_data):
        raise HTTPException(status_code=403, detail="Event not from Slack!")

    background_tasks.add_task(
        slack_integration.handle_event,
        event_data,
    )
    return {"ok": True}
