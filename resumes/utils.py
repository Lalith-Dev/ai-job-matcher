import json
import re
from datetime import datetime

import PyPDF2
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .skills import SKILLS

nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def extract_skills(text):
    text = text.lower()
    return list(set([skill for skill in SKILLS if skill in text]))


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
    docs = [resume_text, job_description]
    tfidf = TfidfVectorizer().fit_transform(docs)
    score = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return float(score[0][0]) * 100


def extract_entities(text):
    doc = nlp(text)
    orgs, locations = set(), set()

    for ent in doc.ents:
        if ent.label_ == "ORG":
            orgs.add(ent.text)
        elif ent.label_ == "GPE":
            locations.add(ent.text)

    return {
        "organizations": list(orgs),
        "locations": list(locations)
    }


def extract_experience(text):
    text_lower = text.lower()

    # Extract only experience section
    start = text_lower.find("experience")
    end = text_lower.find("education")

    if start != -1:
        text_lower = text_lower[start:end if end != -1 else None]

    text_lower = text_lower.replace("\n", " ")
    text_lower = re.sub(r"\s+", " ", text_lower)

    total_years = 0

    pattern = r'([a-zA-Z]+)\s*(\d{4})\s*[–—-]\s*([a-zA-Z]+)\s*(\d{4}|present)'
    matches = re.findall(pattern, text_lower)

    months_map = {
        "jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,
        "jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12
    }

    for sm, sy, em, ey in matches:
        try:
            sm = months_map[sm[:3]]
            sy = int(sy)

            if ey == "present":
                now = datetime.now()
                em, ey = now.month, now.year
            else:
                em = months_map[em[:3]]
                ey = int(ey)

            total_years += ((ey - sy) * 12 + (em - sm)) / 12
        except:
            continue

    return round(total_years, 2)


def extract_education(text):
    keywords = ["bachelor", "master", "msc", "bsc", "phd", "university"]
    lines = text.split("\n")

    result = []
    for line in lines:
        if any(k in line.lower() for k in keywords):
            result.append(line.strip())

    return list(set(result))


def generate_suggestions(missing_skills):
    return [f"Learn {skill} to improve match" for skill in missing_skills]