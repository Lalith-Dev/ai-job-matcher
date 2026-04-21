import json

from rest_framework import generics, permissions
from .models import Resume, Job
from .serializers import ResumeSerializer
from .utils import extract_text_from_pdf, extract_skills, match_skills, compute_similarity, rank_jobs, generate_suggestions, extract_entities, calculate_candidate_ranking, extract_experience, extract_education
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

class ResumeUploadView(generics.CreateAPIView):
    serializer_class = ResumeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        file = self.request.FILES["file"]

        # Extract full text from PDF
        text = extract_text_from_pdf(file)

        # Extract skills
        skills = extract_skills(text)

        # Extract organizations and locations
        entities = extract_entities(text)

        # Extract years of experience
        experience_years = extract_experience(text)

        # Extract education
        education = extract_education(text)

        # Save everything
        serializer.save(
            user=self.request.user,
            extracted_text=text,
            skills=json.dumps(skills),
            organizations=json.dumps(entities["organizations"]),
            locations=json.dumps(entities["locations"]),
            experience_years=experience_years,
            education=json.dumps(education)
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

        suggestions = generate_suggestions(
            skill_match["missing_skills"]
        )

        return Response({
            "skill_match": skill_match,
            "similarity_score": similarity_score,
            "suggestions": suggestions
        })
    
class RecommendJobsView(APIView):
    def get(self, request, resume_id):
        resume = Resume.objects.get(id=resume_id)
        jobs = Job.objects.all()

        ranked_jobs = rank_jobs(resume, jobs)

        return Response(ranked_jobs)
    
class CandidateRankingView(APIView):
    def get(self, request, resume_id, job_id):
        resume = Resume.objects.get(id=resume_id)
        job = Job.objects.get(id=job_id)

        ranking = calculate_candidate_ranking(resume, job)

        return Response(ranking)
    
    
class ATSAnalyzerView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get("file")
        job_description = request.data.get("job_description")

        if not file or not job_description:
            return Response({"error": "file and job_description required"}, status=400)

        resume_text = extract_text_from_pdf(file)

        resume_skills = extract_skills(resume_text)
        job_skills = extract_skills(job_description)

        skill_match = match_skills(resume_skills, job_skills)
        similarity = compute_similarity(resume_text, job_description)

        experience = extract_experience(resume_text)
        education = extract_education(resume_text)

        suggestions = generate_suggestions(skill_match["missing_skills"])

        return Response({
            "match_score": round(similarity, 2),
            "skills_match": skill_match,
            "experience_years": experience,
            "education": education,
            "suggestions": suggestions
        })