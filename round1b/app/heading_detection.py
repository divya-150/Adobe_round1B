import fitz
from collections import defaultdict
import re

HEADING_MAX_LEN = 120

def is_heading_candidate(text):
    text = text.strip()
    if not text:
        return False
    if len(text) > HEADING_MAX_LEN:
        return False
    if re.search(r"[.:;]$", text):
        return False
    if len(re.sub(r"\d+[\.\)]*", "", text).strip()) == 0:
        return False
    return True

def extract_sections(pdf_path):
    """
    Returns:
      {
        "document": <name>,
        "sections": [
           {
             "title": "Intro",
             "level": "H1",
             "page_start": 2,
             "text": "...."
           },
           ...
        ]
      }
    """
    doc = fitz.open(pdf_path)
    spans = []
    for page_idx, page in enumerate(doc, start=1):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            for l in b.get("lines", []):
                for s in l.get("spans", []):
                    text = s.get("text", "").strip()
                    if not text:
                        continue
                    size = s.get("size", 0)
                    font = s.get("font", "")
                    bold = "Bold" in font or font.endswith("-B") or font.endswith("Bold")
                    spans.append((page_idx, text, size, bold))

    # Merge contiguous spans by size/bold → candidate lines
    lines_by_page = defaultdict(list)
    for page_idx, text, size, bold in spans:
        lines_by_page[page_idx].append((text, size, bold))

    candidates = []
    page_texts = defaultdict(list)
    for page_idx, lines in lines_by_page.items():
        buffer = []
        prev_size = None
        prev_bold = None
        for text, size, bold in lines:
            page_texts[page_idx].append(text)
            if buffer and (abs(size - prev_size) > 0.1 or bold != prev_bold):
                merged = " ".join([x[0] for x in buffer]).strip()
                if is_heading_candidate(merged):
                    candidates.append((page_idx, merged, buffer[0][1], any(x[2] for x in buffer)))
                buffer = []
            buffer.append((text, size, bold))
            prev_size, prev_bold = size, bold
        if buffer:
            merged = " ".join([x[0] for x in buffer]).strip()
            if is_heading_candidate(merged):
                candidates.append((page_idx, merged, buffer[0][1], any(x[2] for x in buffer)))

    if not candidates:
        return {"document": pdf_path.name, "sections": []}

    # Map sizes to hierarchy
    sizes = sorted({c[2] for c in candidates}, reverse=True)
    level_map = {}
    for idx, s in enumerate(sizes):
        if idx == 0:
            level_map[s] = "TITLE"
        elif idx == 1:
            level_map[s] = "H1"
        elif idx == 2:
            level_map[s] = "H2"
        else:
            level_map[s] = "H3"

    sections = []
    used_title = False
    for i, (page, text, size, bold) in enumerate(candidates):
        level = level_map.get(size, "H3")
        if level == "TITLE" and not used_title:
            used_title = True
            continue  # skip storing doc title as a section
        if level == "TITLE":  # demote to H1 if multiple
            level = "H1"
        if bold and level == "H3":
            level = "H2"
        sections.append({"title": text, "level": level, "page_start": page, "idx": i})

    # Add text content between this heading and the next heading
    full_text_by_page = {p: " ".join(t) for p, t in page_texts.items()}
    # Build rough page ranges for each section
    for idx, sec in enumerate(sections):
        start_page = sec["page_start"]
        end_page = (sections[idx + 1]["page_start"] - 1) if idx + 1 < len(sections) else len(doc)
        pages_text = []
        for p in range(start_page, end_page + 1):
            pages_text.append(full_text_by_page.get(p, ""))
        sec["page_end"] = end_page
        sec["text"] = "\n".join(pages_text)

    for sec in sections:
        # we'll set page_number = page_start for ranking metadata
        sec["page_number"] = sec["page_start"]

    return {"document": pdf_path.name, "sections": sections}