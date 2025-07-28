import sys
from pathlib import Path
from datetime import datetime
from io_utils import INPUT_DIR, OUTPUT_DIR, ensure_dirs, write_json, read_persona_job
from heading_detection import extract_sections
from ranker import rank_sections, rank_subsections

def load_docs_sections():
    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    docs_sections = []
    for pdf in pdfs:
        docs_sections.append(extract_sections(pdf))
    return docs_sections

def main():
    ensure_dirs()

    persona_job_file = INPUT_DIR / "persona_job.json"
    if not persona_job_file.exists():
        print("ERROR: Please place persona_job.json in /app/input")
        return 1

    persona_job = read_persona_job(persona_job_file)
    persona = persona_job.get("persona", "")
    job = persona_job.get("job_to_be_done", "")
    prompt = f"Persona: {persona}\nJob: {job}"

    docs_sections = load_docs_sections()
    ranked_sections = rank_sections(prompt, docs_sections, top_k=5)

    output = {
        "metadata": {
            "input_documents": [d["document"] for d in docs_sections],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.utcnow().isoformat()
        },
        "extracted_sections": [],
        "subsection_analysis": []
    }

    for section in ranked_sections:
        output["extracted_sections"].append({
            "document": section["document"],
            "section_title": section["section_title"],
            "importance_rank": section["importance_rank"],
            "page_number": section["page_number"]
        })

        refined_subs = rank_subsections(prompt, section["text"], top_k=5)
        for sub in refined_subs:
            output["subsection_analysis"].append({
                "document": section["document"],
                "refined_text": sub["refined_text"],
                "page_number": section["page_number"]
            })

    write_json(output, OUTPUT_DIR / "output.json")
    print("Wrote /app/output/output.json")
    return 0
if __name__ == "__main__":
    sys.exit(main())
