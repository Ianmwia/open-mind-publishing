from ninja import Schema
from typing import Optional, List
from datetime import datetime, date


# ====================================
# SUB-SCHEMAS (ASSIGNMENTS, MILESTONES, ASSETS)
# ====================================

class AssignmentInSchema(Schema):
    user_id: int
    role: str  # author, co_author, translator, illustrator, editor, reviewer, typesetter, project_manager
    deliverable_notes: Optional[str] = ""


class AssignmentOutSchema(Schema):
    id: int
    project_id: int
    user_id: int
    user_name: str
    user_email: Optional[str] = ""
    role: str
    assigned_date: date
    deliverable_notes: str

    @staticmethod
    def resolve_user_name(obj):
        return obj.user.pen_name or obj.user.username

    @staticmethod
    def resolve_user_email(obj):
        return obj.user.email or ""


class MilestoneInSchema(Schema):
    title: str
    due_date: Optional[date] = None
    is_completed: bool = False
    notes: Optional[str] = ""
    order: int = 1


class MilestonePatchSchema(Schema):
    title: Optional[str] = None
    due_date: Optional[date] = None
    is_completed: Optional[bool] = None
    notes: Optional[str] = None
    order: Optional[int] = None


class MilestoneOutSchema(Schema):
    id: int
    project_id: int
    title: str
    due_date: Optional[date] = None
    is_completed: bool
    completed_at: Optional[datetime] = None
    notes: str
    order: int


class AssetInSchema(Schema):
    title: str
    asset_type: str = "manuscript"  # manuscript, illustration, cover_art, chart_grid, proof_pdf, final_export, other
    file_url: Optional[str] = ""
    version: str = "v1.0"


class AssetOutSchema(Schema):
    id: int
    project_id: int
    title: str
    asset_type: str
    file_url: str
    version: str
    created_at: datetime

    @staticmethod
    def resolve_file_url(obj):
        if obj.file:
            return obj.file.url
        return obj.file_url or ""


# ====================================
# PROJECT CORE SCHEMAS
# ====================================

class ProjectInSchema(Schema):
    title: str
    description: Optional[str] = ""
    category: str  # digital, language, chart
    project_type: str  # english_storybook, french_storybook, bilingual_reader, alphabet_chart, etc.
    status: Optional[str] = "idea"
    primary_language: str = "English"
    secondary_language: Optional[str] = ""
    target_age_group: Optional[str] = ""
    dimensions: Optional[str] = ""
    isbn_or_sku: Optional[str] = ""
    is_published: bool = False


class ProjectPatchSchema(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    project_type: Optional[str] = None
    status: Optional[str] = None
    primary_language: Optional[str] = None
    secondary_language: Optional[str] = None
    target_age_group: Optional[str] = None
    dimensions: Optional[str] = None
    isbn_or_sku: Optional[str] = None
    is_published: Optional[bool] = None


class ProjectOutSchema(Schema):
    id: int
    title: str
    description: str
    category: str
    project_type: str
    status: str
    primary_language: str
    secondary_language: str
    target_age_group: str
    dimensions: str
    isbn_or_sku: str
    is_published: bool
    created_at: datetime
    updated_at: datetime


class ProjectDetailOutSchema(ProjectOutSchema):
    assignments: List[AssignmentOutSchema] = []
    milestones: List[MilestoneOutSchema] = []
    assets: List[AssetOutSchema] = []
