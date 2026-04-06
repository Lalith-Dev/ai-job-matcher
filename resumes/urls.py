from django.urls import path
from .views import ResumeUploadView, MatchJobView

urlpatterns = [
    path('upload/', ResumeUploadView.as_view()),
    path('match/<int:resume_id>/<int:job_id>/', MatchJobView.as_view()),
]