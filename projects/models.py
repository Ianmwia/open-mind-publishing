from django.db import models

# Create your models here.
class Project(models.Model):
    #many to many relationship with the user model, a project can have multiple users and a user can have multiple projects
    user = models.ManyToManyField('accounts.CustomUser', related_name='projects')

    title = models.CharField(max_length=255)
    description = models.TextField()

    project_type = models.CharField(max_length=100)
    category = models.CharField(max_length=100)

    language = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title