from ninja import Router
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.utils import timezone
from allauth.headless.contrib.ninja.security import jwt_token_auth

from .models import Project, ProjectAssignment, Milestone, ProjectAsset
from accounts.models import CustomUser
from .schemas import (
    ProjectInSchema, ProjectPatchSchema, ProjectOutSchema, ProjectDetailOutSchema,
    AssignmentInSchema, AssignmentOutSchema,
    MilestoneInSchema, MilestonePatchSchema, MilestoneOutSchema,
    AssetInSchema, AssetOutSchema,
)

router = Router(tags=["Projects Management (Digital, Language, Charts)"])


# =========================================================
# 1. CORE PROJECT CRUD ENDPOINTS
# =========================================================

@router.get("/", response=List[ProjectOutSchema])
def list_projects(
    request,
    category: Optional[str] = None,
    project_type: Optional[str] = None,
    status: Optional[str] = None,
    language: Optional[str] = None,
    search: Optional[str] = None,
):
    qs = Project.objects.all().order_by('-created_at')
    if category:
        qs = qs.filter(category=category)
    if project_type:
        qs = qs.filter(project_type=project_type)
    if status:
        qs = qs.filter(status=status)
    if language:
        qs = qs.filter(primary_language__icontains=language) | qs.filter(secondary_language__icontains=language)
    if search:
        qs = qs.filter(title__icontains=search) | qs.filter(description__icontains=search)
    return qs


@router.post("/", auth=[jwt_token_auth], response={201: ProjectOutSchema})
def create_project(request, payload: ProjectInSchema):
    data = payload.dict()
    project = Project.objects.create(created_by=request.user, **data)
    return 201, project


@router.get("/{project_id}/", response=ProjectDetailOutSchema)
def get_project(request, project_id: int):
    return get_object_or_404(
        Project.objects.prefetch_related('assignments__user', 'milestones', 'assets'),
        id=project_id
    )


@router.patch("/{project_id}/", auth=[jwt_token_auth], response=ProjectOutSchema)
def update_project(request, project_id: int, payload: ProjectPatchSchema):
    project = get_object_or_404(Project, id=project_id)
    for attr, value in payload.dict(exclude_unset=True).items():
        if value is not None:
            setattr(project, attr, value)
    project.save()
    return project


@router.delete("/{project_id}/", auth=[jwt_token_auth], response={200: dict})
def delete_project(request, project_id: int):
    project = get_object_or_404(Project, id=project_id)
    project.delete()
    return 200, {"message": f"Project '{project.title}' deleted successfully."}


# =========================================================
# 2. PROJECT TEAM ASSIGNMENTS (ASSIGN USERS WITH ROLES)
# =========================================================

@router.get("/{project_id}/assignments/", response=List[AssignmentOutSchema])
def list_assignments(request, project_id: int):
    project = get_object_or_404(Project, id=project_id)
    return project.assignments.select_related('user').all()


@router.post("/{project_id}/assignments/", auth=[jwt_token_auth], response={201: AssignmentOutSchema, 400: dict})
def assign_contributor(request, project_id: int, payload: AssignmentInSchema):
    project = get_object_or_404(Project, id=project_id)
    user = get_object_or_404(CustomUser, id=payload.user_id)

    assignment, created = ProjectAssignment.objects.get_or_create(
        project=project,
        user=user,
        role=payload.role,
        defaults={"deliverable_notes": payload.deliverable_notes or ""}
    )
    if not created and payload.deliverable_notes:
        assignment.deliverable_notes = payload.deliverable_notes
        assignment.save()

    return 201, assignment


@router.delete("/{project_id}/assignments/{assignment_id}/", auth=[jwt_token_auth], response={200: dict})
def remove_assignment(request, project_id: int, assignment_id: int):
    assignment = get_object_or_404(ProjectAssignment, id=assignment_id, project_id=project_id)
    assignment.delete()
    return 200, {"message": "Team assignment successfully removed."}


# =========================================================
# 3. MILESTONES & WORKFLOW STAGES
# =========================================================

@router.get("/{project_id}/milestones/", response=List[MilestoneOutSchema])
def list_milestones(request, project_id: int):
    project = get_object_or_404(Project, id=project_id)
    return project.milestones.all()


@router.post("/{project_id}/milestones/", auth=[jwt_token_auth], response={201: MilestoneOutSchema})
def create_milestone(request, project_id: int, payload: MilestoneInSchema):
    project = get_object_or_404(Project, id=project_id)
    data = payload.dict()
    if data.get('is_completed'):
        data['completed_at'] = timezone.now()
    milestone = Milestone.objects.create(project=project, **data)
    return 201, milestone


@router.patch("/{project_id}/milestones/{milestone_id}/", auth=[jwt_token_auth], response=MilestoneOutSchema)
def update_milestone(request, project_id: int, milestone_id: int, payload: MilestonePatchSchema):
    milestone = get_object_or_404(Milestone, id=milestone_id, project_id=project_id)
    patch_data = payload.dict(exclude_unset=True)

    if "is_completed" in patch_data:
        if patch_data["is_completed"] and not milestone.is_completed:
            milestone.completed_at = timezone.now()
        elif not patch_data["is_completed"]:
            milestone.completed_at = None

    for attr, value in patch_data.items():
        if value is not None or attr in ["completed_at"]:
            setattr(milestone, attr, value)
    milestone.save()
    return milestone


@router.delete("/{project_id}/milestones/{milestone_id}/", auth=[jwt_token_auth], response={200: dict})
def delete_milestone(request, project_id: int, milestone_id: int):
    milestone = get_object_or_404(Milestone, id=milestone_id, project_id=project_id)
    milestone.delete()
    return 200, {"message": f"Milestone '{milestone.title}' deleted."}


# =========================================================
# 4. PROJECT ASSETS (MANUSCRIPTS, ARTWORK, PROOF PDFS)
# =========================================================

@router.get("/{project_id}/assets/", response=List[AssetOutSchema])
def list_assets(request, project_id: int):
    project = get_object_or_404(Project, id=project_id)
    return project.assets.all()


@router.post("/{project_id}/assets/", auth=[jwt_token_auth], response={201: AssetOutSchema})
def create_asset(request, project_id: int, payload: AssetInSchema):
    project = get_object_or_404(Project, id=project_id)
    asset = ProjectAsset.objects.create(
        project=project,
        uploaded_by=request.user,
        **payload.dict()
    )
    return 201, asset


@router.delete("/{project_id}/assets/{asset_id}/", auth=[jwt_token_auth], response={200: dict})
def delete_asset(request, project_id: int, asset_id: int):
    asset = get_object_or_404(ProjectAsset, id=asset_id, project_id=project_id)
    asset.delete()
    return 200, {"message": f"Asset '{asset.title}' deleted."}
