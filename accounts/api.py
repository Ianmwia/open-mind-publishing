from ninja import Router
from allauth.headless.contrib.ninja.security import jwt_token_auth  # <-- Allauth native JWT helper

from accounts.schemas import UserOutSchema, UserPatchSchema

router = Router(tags=["Accounts & Profiles, login logout handled by allauth headless"])

# --- PROFILE CRUD ENDPOINTS ---

# 1. READ Profile Info
@router.get("/me", auth=[jwt_token_auth], response=UserOutSchema)
def get_my_profile(request):
    return request.user

# 2. UPDATE Profile Info (1-by-1 Patching)
@router.patch("/me", auth=[jwt_token_auth], response=UserOutSchema)
def update_my_profile(request, data: UserPatchSchema):
    user = request.user
    
    if data.username is not None:
        user.username = data.username
    if data.email is not None:
        user.email = data.email
    if data.bio is not None:
        user.bio = data.bio
    if data.timezone is not None:
        user.timezone = data.timezone
        
    user.save()
    return user

# 3. DELETE Account 
@router.delete("/me", auth=[jwt_token_auth], response={200: dict})
def delete_my_account(request):
    user = request.user
    user.delete()
    return 200, {"message": "Account successfully removed from database records."}