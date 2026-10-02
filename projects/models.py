from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField


class ProjectCategory(models.TextChoices):
    DIGITAL = 'digital', 'Digital Projects'
    LANGUAGE = 'language', 'Language Projects'
    CHART = 'chart', 'Charts'


class ProjectType(models.TextChoices):
    # 1. Digital projects
    ENGLISH_STORYBOOK = 'english_storybook', 'English Storybook'
    FRENCH_STORYBOOK = 'french_storybook', 'French Storybook'
    DIGITAL_STORYBOOK = 'digital_storybook', 'Storybook (General)'

    # 2. Language projects
    BILINGUAL_READER = 'bilingual_reader', 'Bilingual Reader'
    BILINGUAL_VOCABULARY = 'bilingual_vocabulary', 'Bilingual Vocabulary Book'

    # 3. Charts
    ALPHABET_CHART = 'alphabet_chart', 'Alphabet Chart'
    SYLLABLE_CHART = 'syllable_chart', 'Syllable Chart'


class ProjectStatus(models.TextChoices):
    IDEA = 'idea', 'Idea / Concept'
    DRAFTING = 'drafting', 'Manuscript Drafting'
    TRANSLATION = 'translation', 'Translating'
    ILLUSTRATION = 'illustration', 'Illustration / Graphic Design'
    EDITORIAL_REVIEW = 'editorial_review', 'Editorial Review & Proofreading'
    LAYOUT_APPROVAL = 'layout_approval', 'Layout & Pre-Press Approval'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=ProjectCategory.choices)
    project_type = models.CharField(max_length=50, choices=ProjectType.choices)
    status = models.CharField(
        max_length=50, 
        choices=ProjectStatus.choices, 
        default=ProjectStatus.IDEA
    )

    # Language specifications
    primary_language = models.CharField(max_length=50, default='English', help_text="e.g. English, French")
    secondary_language = models.CharField(
        max_length=50, 
        blank=True, 
        help_text="Target language for bilingual projects, e.g. French"
    )

    # Specifications
    target_age_group = models.CharField(max_length=50, blank=True, help_text="e.g. Ages 3-5, Grades 1-3")
    dimensions = models.CharField(max_length=50, blank=True, help_text="For charts or print size, e.g. A1, A2, 8.5x11")
    isbn_or_sku = models.CharField(max_length=100, blank=True)

    # Many-to-Many with CustomUser via ProjectAssignment
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ProjectAssignment',
        related_name='assigned_projects',
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_projects'
    )
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"


class AssignmentRole(models.TextChoices):
    AUTHOR = 'author', 'Author'
    CO_AUTHOR = 'co_author', 'Co-Author'
    TRANSLATOR = 'translator', 'Translator'
    ILLUSTRATOR = 'illustrator', 'Illustrator'
    EDITOR = 'editor', 'Editor'
    REVIEWER = 'reviewer', 'Reviewer'
    TYPESETTER = 'typesetter', 'Typesetter / Layout Artist'
    PROJECT_MANAGER = 'project_manager', 'Project Manager'


class ProjectAssignment(models.Model):
    """Assigns a registered user to a Project with a designated role."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assignments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='project_assignments'
    )
    role = models.CharField(max_length=50, choices=AssignmentRole.choices)
    assigned_date = models.DateField(auto_now_add=True)
    deliverable_notes = models.TextField(blank=True, help_text="Instructions, milestones, or scope for this contributor")

    class Meta:
        unique_together = ('project', 'user', 'role')

    def __str__(self):
        name = self.user.pen_name or self.user.username
        return f"{name} as {self.get_role_display()} on {self.project.title}"


class Milestone(models.Model):
    """Workflow checkpoints for a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255, help_text="e.g. English Draft, French Translation, Illustrations Complete")
    due_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order', 'due_date']

    def __str__(self):
        return f"{self.project.title} - {self.title} ({'Done' if self.is_completed else 'Pending'})"


class AssetType(models.TextChoices):
    MANUSCRIPT = 'manuscript', 'Manuscript (Doc/Text)'
    ILLUSTRATION = 'illustration', 'Illustration / Graphic'
    COVER_ART = 'cover_art', 'Cover Art'
    CHART_GRID = 'chart_grid', 'Chart Grid / Vector'
    PROOF_PDF = 'proof_pdf', 'Proof PDF'
    FINAL_EXPORT = 'final_export', 'Final Print / Digital Export'
    OTHER = 'other', 'Other Asset'


class ProjectAsset(models.Model):
    """Stores manuscripts, illustrations, and press-ready files linked to a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assets')
    title = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=50, choices=AssetType.choices, default=AssetType.MANUSCRIPT)
    file = CloudinaryField('file', blank=True, null=True, resource_type='auto')
    file_url = models.URLField(blank=True, help_text="Direct link or external document link (e.g. Google Docs/Drive)")
    version = models.CharField(max_length=20, default='v1.0')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.title} - {self.title} ({self.version})"