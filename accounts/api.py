from ninja import Router
from typing import List, Optional
from django.shortcuts import get_object_or_404
from allauth.headless.contrib.ninja.security import jwt_token_auth

from .models import CustomUser, Role, RoleName
from .schemas import UserOutSchema, UserPatchSchema, RoleOutSchema

router = Router(tags=["Accounts, Roles & User Directory"])


# --- SEED & LIST ROLES ---
@router.get("/roles/", response=List[RoleOutSchema])
def list_roles(request):
    """Lists all system roles (e.g. Author, Freelancer, Translator, Illustrator, Editor, Reviewer)."""
    # Seed default roles if table is empty
    if Role.objects.count() == 0:
        default_roles = [
            (RoleName.AUTHOR, "Primary or contributing manuscript author"),
            (RoleName.FREELANCER, "General freelance contractor"),
            (RoleName.ILLUSTRATOR, "Illustrator and graphic asset designer"),
            (RoleName.TRANSLATOR, "Language translator and localized text adapter"),
            (RoleName.EDITOR, "Content editor and manuscript reviewer"),
            (RoleName.REVIEWER, "Peer reviewer and quality approver"),
            (RoleName.PROJECT_MANAGER, "Publishing lead and project coordinator"),
        ]
        for name, desc in default_roles:
            Role.objects.get_or_create(name=name, defaults={"description": desc})
    return Role.objects.all()


# --- PROFILE CRUD ENDPOINTS ---

# 1. READ Profile Info
@router.get("/get_profile/", auth=[jwt_token_auth], response=UserOutSchema)
def get_my_profile(request):
    return request.user


# 2. UPDATE Profile Info & Selected Roles
@router.patch("/update_profile/", auth=[jwt_token_auth], response=UserOutSchema)
def update_my_profile(request, data: UserPatchSchema):
    user = request.user
    patch_dict = data.dict(exclude_unset=True)

    # Handle roles selection
    if "role_ids" in patch_dict:
        role_ids = patch_dict.pop("role_ids")
        if role_ids is not None:
            user.roles.set(Role.objects.filter(id__in=role_ids))

    # Update all scalar fields
    for attr, value in patch_dict.items():
        if value is not None:
            setattr(user, attr, value)

    user.save()
    return user


# 3. DIRECTORY OF USERS (Filter by Role, e.g., finding translators or authors)
@router.get("/users/", response=List[UserOutSchema])
def list_users(request, role: Optional[str] = None, search: Optional[str] = None):
    qs = CustomUser.objects.prefetch_related('roles').all()
    if role:
        qs = qs.filter(roles__name=role)
    if search:
        qs = qs.filter(
            username__icontains=search
        ) | qs.filter(
            pen_name__icontains=search
        ) | qs.filter(
            email__icontains=search
        ) | qs.filter(
            specialties_or_languages__icontains=search
        )
    return qs


@router.get("/users/{user_id}/", response=UserOutSchema)
def get_user_detail(request, user_id: int):
    return get_object_or_404(CustomUser.objects.prefetch_related('roles'), id=user_id)


# 4. DELETE Account 
@router.delete("/delete_account/", auth=[jwt_token_auth], response={200: dict})
def delete_my_account(request):
    user = request.user
    user.delete()
    return 200, {"message": "Account successfully removed from database records."}