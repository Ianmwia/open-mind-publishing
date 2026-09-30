# accounts/schemas.py
from ninja import Schema
from pydantic import EmailStr
from typing import Optional

# The schema tracking what we return back to the user
class UserOutSchema(Schema):
    id: int
    username: str
    email: EmailStr
    bio: str
    timezone: str
    is_custom: bool

# The schema controlling granular 1-by-1 PATCH updates
class UserPatchSchema(Schema):
    username: Optional[str] = None
    email: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
