from django.db import models
from django.contrib.auth.models import User
import json

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    organizations = models.TextField(blank=True)
    locations = models.TextField(blank=True)
    experience_years = models.FloatField(default=0)
    education = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField()
    min_experience = models.IntegerField(default=0)
    required_education = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.title