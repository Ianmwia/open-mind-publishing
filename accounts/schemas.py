# accounts/schemas.py
from ninja import Schema
from pydantic import EmailStr
from typing import Optional, List
from datetime import datetime


class RoleOutSchema(Schema):
    id: int
    name: str
    description: str


# Schema tracking what we return back to the user
class UserOutSchema(Schema):
    id: int
    username: str
    email: Optional[EmailStr] = None
    pen_name: str
    phone: str
    bio: str
    address: str
    specialties_or_languages: str
    portfolio_url: str
    emergency_or_agent_contact: str
    timezone: str
    is_custom: bool
    roles: List[RoleOutSchema] = []
    created_at: datetime
    updated_at: datetime


# Schema controlling granular updates (PATCH)
class UserPatchSchema(Schema):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    pen_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    address: Optional[str] = None
    specialties_or_languages: Optional[str] = None
    portfolio_url: Optional[str] = None
    emergency_or_agent_contact: Optional[str] = None
    timezone: Optional[str] = None
    role_ids: Optional[List[int]] = None
