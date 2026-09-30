from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField

# Create your models here.
class CustomUser(AbstractUser):
    '''
    AbstractUser = add to django's existing tour own fields, only 1 class needed, can use the default user manager
    AbstractBaseUser = create your own user model from scratch , no hand holding, must add a helper class to manage the user model, and add a custom user manager to handle the creation of users and superusers
    '''
    # custom table columns
    bio = models.TextField(blank=True)
    image = CloudinaryField('image', blank=True, null=True)
    timezone = models.CharField(max_length=30, default='UTC')
    is_custom = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_utc(self):
        return self.timezone == 'UTC'

    def __str__(self):
        return self.username

