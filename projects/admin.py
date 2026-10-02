from django.contrib import admin
from .models import Project, ProjectAssignment, Milestone, ProjectAsset


class ProjectAssignmentInline(admin.TabularInline):
    model = ProjectAssignment
    extra = 1


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1


class ProjectAssetInline(admin.TabularInline):
    model = ProjectAsset
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'project_type', 'status', 'primary_language', 'is_published')
    list_filter = ('category', 'project_type', 'status', 'primary_language', 'is_published')
    search_fields = ('title', 'description', 'isbn_or_sku')
    inlines = [ProjectAssignmentInline, MilestoneInline, ProjectAssetInline]


@admin.register(ProjectAssignment)
class ProjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role', 'assigned_date')
    list_filter = ('role', 'assigned_date')
    search_fields = ('project__title', 'user__username', 'user__pen_name')


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'due_date', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'due_date')


@admin.register(ProjectAsset)
class ProjectAssetAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'asset_type', 'version', 'created_at')
    list_filter = ('asset_type', 'created_at')