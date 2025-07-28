---

### 📁 **Round 1B – README.md**

markdown
# 🤖 Adobe India Hackathon – Round 1B: Persona-Driven Document Intelligence

## 🧠 Challenge Overview
Build a smart system to extract and rank the most **relevant document sections** based on:
- A persona (user role)
- A job-to-be-done (specific goal)

---

## 📥 Input
- Folder: `/app/input/`
- PDFs: 3 to 10 related documents
- Metadata JSON: contains persona + job-to-be-done

---

## 📤 Output Format
JSON with:
1. **Metadata**
   - Input docs
   - Persona
   - Job
   - Timestamp
2. **Extracted Sections**
   - Document name
   - Page number
   - Section title
   - Relevance rank
3. **Sub-section Analysis**
   - Extracted relevant text chunks
   - Page numbers

Refer to the `challenge1b_output.json` for the format.

---

## ⚙ Tech Stack & Tools
- Python 3.x
- `PyMuPDF`, `transformers`, `sentence-transformers`, `scikit-learn`
- Model: `MiniLM` (< 400MB)

---

## 🛠 Our Approach

1. **Preprocessing**: Extract raw text and segment using layout cues
2. **Embedding**: Convert persona, job, and sections into dense vectors
3. **Ranking**: Compute semantic similarity for relevance scores
4. **Sub-section Analysis**: Windowed chunking + ranking

---

## 🐳 Docker Instructions

### 🔨 Build Image
bash
docker build --platform linux/amd64 -t personaextractor:round1b .
