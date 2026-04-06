from django.db import models
from django.contrib.auth.models import User
import json

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True)
    skills = models.TextField(blank=True)  # store as JSON string
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.TextField()  # JSON list

    def __str__(self):
        return self.title