import json
import re
import PyPDF2
from .skills import SKILLS
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
nlp = spacy.load("en_core_web_sm")


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

def extract_entities(text):
    doc = nlp(text)

    organizations = set()
    locations = set()

    for ent in doc.ents:
        if ent.label_ == "ORG":
            organizations.add(ent.text)

        elif ent.label_ == "GPE":
            locations.add(ent.text)

    return {
        "organizations": list(organizations),
        "locations": list(locations)
    }

def extract_experience(text):
    text_lower = text.lower()

    # -----------------------------------
    # Step 1: Identify experience section
    # -----------------------------------
    experience_headers = [
        "professional experience",
        "work experience",
        "experience",
        "employment history"
    ]

    education_headers = [
        "education",
        "academic background"
    ]

    experience_text = ""

    start_index = -1
    end_index = len(text_lower)

    # Find start of experience section
    for header in experience_headers:
        idx = text_lower.find(header)
        if idx != -1:
            start_index = idx
            break

    if start_index == -1:
        return 0

    # Find next education section after experience
    for header in education_headers:
        idx = text_lower.find(header, start_index)
        if idx != -1:
            end_index = idx
            break

    experience_text = text[start_index:end_index]

    total_years = 0

    # -----------------------------------
    # Step 2: Detect explicit years
    # -----------------------------------
    explicit_pattern = r'(\d+(?:\.\d+)?)\s*\+?\s*(years|year|yrs|yr)'
    explicit_matches = re.findall(explicit_pattern, experience_text.lower())

    if explicit_matches:
        for match in explicit_matches:
            total_years += float(match[0])

        return round(total_years, 1)

    # -----------------------------------
    # Step 3: Detect date ranges only inside experience block
    # -----------------------------------
    months = {
        "jan": 1, "january": 1,
        "feb": 2, "february": 2,
        "mar": 3, "march": 3,
        "apr": 4, "april": 4,
        "may": 5,
        "jun": 6, "june": 6,
        "jul": 7, "july": 7,
        "aug": 8, "august": 8,
        "sep": 9, "september": 9,
        "oct": 10, "october": 10,
        "nov": 11, "november": 11,
        "dec": 12, "december": 12,
    }

    date_pattern = r'([A-Za-z]+)\s+(\d{4})\s*[–—-]\s*([A-Za-z]+)\s+(\d{4}|present)'
    matches = re.findall(date_pattern, experience_text.lower())
    print("Matched date ranges:", matches)

    for start_month, start_year, end_month, end_year in matches:
        try:
            start_m = months[start_month[:3]]
            start_y = int(start_year)

            if end_year == "present":
                now = datetime.now()
                end_m = now.month
                end_y = now.year
            else:
                end_m = months[end_month[:3]]
                end_y = int(end_year)

            months_diff = (end_y - start_y) * 12 + (end_m - start_m)
            total_years += months_diff / 12

        except:
            continue

    return round(total_years, 1)


def extract_education(text):
    education_keywords = [
        "bachelor",
        "master",
        "msc",
        "bsc",
        "phd",
        "university"
    ]

    lines = text.split("\n")
    education_found = []

    for line in lines:
        for keyword in education_keywords:
            if keyword in line.lower():
                education_found.append(line.strip())
                break

    return list(set(education_found))

def calculate_candidate_ranking(resume, job):
    import json

    resume_skills = json.loads(resume.skills) if resume.skills else []
    job_skills = json.loads(job.required_skills) if job.required_skills else []

    skill_match = match_skills(resume_skills, job_skills)
    skills_score = skill_match["match_score"]

    # Experience score
    if job.min_experience == 0:
        experience_score = 100
    else:
        experience_score = min(
            (resume.experience_years / job.min_experience) * 100,
            100
        )

    # Education score
    education_list = json.loads(resume.education) if resume.education else []

    education_score = 0
    for edu in education_list:
        if job.required_education.lower() in edu.lower():
            education_score = 100
            break

    # Weighted final score
    final_rank_score = (
        skills_score * 0.5 +
        experience_score * 0.3 +
        education_score * 0.2
    )

    return {
        "final_rank_score": round(final_rank_score, 2),
        "skills_score": round(skills_score, 2),
        "experience_score": round(experience_score, 2),
        "education_score": round(education_score, 2)
    }