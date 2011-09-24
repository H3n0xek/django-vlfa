from django.db import models
from django.contrib.auth.models import User
from vlfa_base.models import Category, Thread, Post


class ModeratorProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    category = models.ManyToManyField(Category)
    
      
