from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def rank_sections(persona_job_str, docs_sections, top_k=20):
    # Flatten sections
    corpus = []
    meta = []
    for d in docs_sections:
        for s in d["sections"]:
            text = (s["title"] + " " + s["text"]).strip()
            corpus.append(text)
            meta.append((d["document"], s))

    if not corpus:
        return []

    vectorizer = TfidfVectorizer(stop_words="english", max_features=50000)
    X = vectorizer.fit_transform(corpus)
    q = vectorizer.transform([persona_job_str])
    sims = cosine_similarity(q, X).flatten()

    ranked = []
    for score, (doc_name, sec) in sorted(zip(sims, meta), key=lambda x: x[0], reverse=True):
        ranked.append({
            "document": doc_name,
            "page_number": sec["page_number"],
            "section_title": sec["title"],
            "importance_rank": None,  # fill later
            "score": float(score),
            "text": sec["text"]
        })
    # Assign importance_rank
    for i, r in enumerate(ranked, start=1):
        r["importance_rank"] = i

    return ranked

def rank_subsections(persona_job_str, section_text, top_k=5):
    # Split by paragraphs
    paras = [p.strip() for p in section_text.split("\n") if p.strip()]
    if not paras:
        return []
    vectorizer = TfidfVectorizer(stop_words="english", max_features=20000)
    X = vectorizer.fit_transform(paras)
    q = vectorizer.transform([persona_job_str])
    sims = cosine_similarity(q, X).flatten()
    ranked = []
    for i, score in sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:top_k]:
        ranked.append({
            "paragraph_index": i,
            "refined_text": paras[i],
            "score": float(score)
        })
    return ranked