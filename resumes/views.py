import json

from rest_framework import generics, permissions
from .models import Resume, Job
from .serializers import ResumeSerializer
from .utils import extract_text_from_pdf, extract_skills, match_skills, compute_similarity
from rest_framework.views import APIView
from rest_framework.response import Response

class ResumeUploadView(generics.CreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        file = self.request.FILES['file']
        text = extract_text_from_pdf(file)
        skills = extract_skills(text)

        serializer.save(
            user=self.request.user,
            extracted_text=text,
            skills=json.dumps(skills)
        )
        
class MatchJobView(APIView):
    def get(self, request, resume_id, job_id):
        resume = Resume.objects.get(id=resume_id)
        job = Job.objects.get(id=job_id)

        resume_skills = json.loads(resume.skills)
        job_skills = json.loads(job.required_skills)

        skill_match = match_skills(resume_skills, job_skills)

        similarity_score = compute_similarity(
            resume.extracted_text,
            job.description
        )

        return Response({
            "skill_match": skill_match,
            "similarity_score": similarity_score
        })