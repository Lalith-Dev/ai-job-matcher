from django.urls import path
from .views import ResumeUploadView, MatchJobView, RecommendJobsView, CandidateRankingView, ATSAnalyzerView

urlpatterns = [
    path('upload/', ResumeUploadView.as_view()),
    path('match/<int:resume_id>/<int:job_id>/', MatchJobView.as_view()),
    path('recommend/<int:resume_id>/', RecommendJobsView.as_view()),
    path('ranking/<int:resume_id>/<int:job_id>/', CandidateRankingView.as_view()),
    path('ats-analyze/', ATSAnalyzerView.as_view())
]