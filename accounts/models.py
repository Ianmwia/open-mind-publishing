from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField


class RoleName(models.TextChoices):
    AUTHOR = 'author', 'Author'
    FREELANCER = 'freelancer', 'Freelancer'
    ILLUSTRATOR = 'illustrator', 'Illustrator'
    TRANSLATOR = 'translator', 'Translator'
    EDITOR = 'editor', 'Editor'
    REVIEWER = 'reviewer', 'Reviewer'
    PROJECT_MANAGER = 'project_manager', 'Project Manager'


class Role(models.Model):
    name = models.CharField(max_length=50, choices=RoleName.choices, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.get_name_display()


class CustomUser(AbstractUser):
    # Multiple roles can be selected by/assigned to a user
    roles = models.ManyToManyField(Role, related_name='users', blank=True)

    # General profile fields
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    address = models.TextField(blank=True)

    # Contributor & Author/Freelancer specifics
    pen_name = models.CharField(max_length=255, blank=True, help_text="Public pen name or publishing alias")
    specialties_or_languages = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="e.g. 'English to French Translation', 'Watercolor Storybook Art', 'Phonetics'"
    )
    portfolio_url = models.URLField(blank=True)
    emergency_or_agent_contact = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Agent, manager, or emergency contact info"
    )

    timezone = models.CharField(max_length=30, default='UTC')
    is_custom = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_utc(self):
        return self.timezone == 'UTC'

    def __str__(self):
        display = self.pen_name if self.pen_name else self.username
        return f"{display} ({self.email})" if self.email else display
