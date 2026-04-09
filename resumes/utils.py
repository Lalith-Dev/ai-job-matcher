import PyPDF2
from .skills import SKILLS
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def extract_skills(text):
    text = text.lower()
    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    return list(set(found_skills))

def match_skills(resume_skills, job_skills):
    resume_set = set(resume_skills)
    job_set = set(job_skills)

    matched = resume_set.intersection(job_set)
    missing = job_set - resume_set

    score = int((len(matched) / len(job_set)) * 100) if job_set else 0

    return {
        "match_score": score,
        "matched_skills": list(matched),
        "missing_skills": list(missing)
    }
    
def compute_similarity(resume_text, job_description):
    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    return float(similarity[0][0]) * 100

def rank_jobs(resume, jobs):
    results = []

    for job in jobs:
        score = compute_similarity(resume.extracted_text, job.description)

        results.append({
            "job_title": job.title,
            "similarity_score": score
        })

    # sort highest first
    results.sort(key=lambda x: x["similarity_score"], reverse=True)

    return results

def generate_suggestions(missing_skills):
    suggestions = []

    for skill in missing_skills:
        suggestions.append(f"Consider learning {skill} to improve your match")

    return suggestions