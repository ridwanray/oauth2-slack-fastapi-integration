from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List


@dataclass
class AuthorizationResponse:
    authorization_url: str


@dataclass
class UserResponse:
    id: str
    name: str
    real_name: str


@dataclass
class VerifyConnectionResponse:
    connection_verified: bool


@dataclass
class BodyResponse:
    token: str
    challenge: str
    type: str


@dataclass
class CallPostAuthorizeRes:
    protected_data: Dict
    consent_user: str
    metadata: Dict
    access_token: str


@dataclass
class IntGroupData:
    group_id: str
    group_name: str
    role: str
    type: str
    status: str
    delivery_settings: str


@dataclass(order=True)
class FileDTO:
    container_name: str
    file_name: str
    file_type: Optional[str] = None


@dataclass
class UserEmail:
    address: str
    primary: Optional[bool] = None


@dataclass
class UserName:
    givenName: str
    familyName: str
    fullName: str


@dataclass
class UserMailData:
    is_enabled: Optional[bool] = None
    emails_sent: Optional[int] = None
    spam_emails_received: Optional[int] = None
    emails_received: Optional[int] = None
    reason: Optional[str] = None


@dataclass
class UserRecord:
    org_id: str
    user_id: str
    primary_email: str
    is_admin: bool
    name: UserName | Dict
    int_name: Optional[str] = None
    admin_extra_info: Optional[Dict] = None
    suspended: Optional[bool] = None
    archived: Optional[bool] = None
    org_unit_path: Optional[str] = None
    is_enrolled_in_2_sv: Optional[bool] = None
    is_enforced_in_2_sv: Optional[bool] = None
    emails: Optional[List[UserEmail]] = None
    mail_data: Optional[UserMailData] = None
    password_strength: Optional[str] = None
    password_length_compliance: Optional[str] = None
    record_creation_time: Optional[datetime] = None
    record_last_update_time: Optional[datetime] = None
    last_login_time: Optional[datetime] = None
    creation_time: Optional[datetime] = None
    last_mail_fetch: Optional[datetime] = None
    groups: List[str] = field(default_factory=list)
    recovery_email: Optional[str] = field(default=None)
    user_photo: Optional[FileDTO | Dict] = None
    int_groups: List[IntGroupData] = field(default_factory=list)
    extra_data: Dict = field(default_factory=dict)


@dataclass
class AppRecord:
    id: str
    name: str
    description: str
    is_internal: bool
    scopes: List
    org_id: str = None
    int_name: str = None
    user_name: str = None
    user_id: str = None
    client_id: str = None
    display_text: str = None
    native_app: bool = None
    is_grant_app: bool = None
    record_creation_time: Optional[datetime] = None
    record_last_update_time: Optional[datetime] = None
    user_key: Optional[str] = None
    verified: Optional[bool] = None


@dataclass
class GetAppsRes:
    apps: List[AppRecord] = None
    page_token: Optional[str] = None


@dataclass
class GetUsersPageRes:
    users: List[UserRecord]
    page_token: Optional[str] = None
    next_page_token: Optional[str] = None


@dataclass
class SlackEventReq:
    data: Dict = field(default_factory=dict)


@dataclass
class SlackEventRes:
    ok: bool
