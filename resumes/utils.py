import PyPDF2
from .skills import SKILLS


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