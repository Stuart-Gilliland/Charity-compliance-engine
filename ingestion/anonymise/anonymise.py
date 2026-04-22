"""
Anonymisation pipeline for the Charity Compliance Engine.
Processes documents using Microsoft Presidio to detect and replace
personally identifiable information and named organisations before
ingestion into the vector store.

Retain list: entities that must never be redacted.
Replacement map: real organisation names replaced with fictional equivalents.
"""

import os
import json
from pathlib import Path
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from docx import Document
import pdfplumber


# ── RETAIN LIST ──────────────────────────────────────────────────────────────
# Entities that must never be redacted — authoritative sources and legislation

RETAIN_LIST = [
    # Regulators and sector bodies
    "OSCR",
    "Office of the Scottish Charity Regulator",
    "SCVO",
    "Scottish Council for Voluntary Organisations",
    "ICO",
    "Information Commissioner's Office",
    "Disclosure Scotland",
    "Protection of Vulnerable Groups",
    "PVG",
    "Fundraising Regulator",
    "HMRC",
    "Companies House",
    "Office of the Public Guardian",
    "Care Inspectorate",
    "Scottish Government",
    "UK Government",
    "ACAS",
    "Health and Safety Executive",
    "HSE",
    "Volunteer Scotland",
    "Burness Paull",
    "Church of Scotland",
    # Legislation
    "Charities and Trustee Investment (Scotland) Act 2005",
    "Charities (Regulation and Administration) (Scotland) Act 2023",
    "UK GDPR",
    "GDPR",
    "Data Protection Act 2018",
    "Protection of Vulnerable Groups (Scotland) Act 2007",
    "Equality Act 2010",
    "Employment Rights Act 1996",
    "Health and Safety at Work etc. Act 1974",
    "Freedom of Information (Scotland) Act 2002",
    # Geographic references to preserve
    "Scotland",
    "Scottish",
    "United Kingdom",
    "UK",
]

# ── REPLACEMENT MAP ───────────────────────────────────────────────────────────
# Real organisation names replaced with fictional equivalents for readability

REPLACEMENT_MAP = {
    "EPS": "Caledonian Arts Forum",
    "Lyle Gateway": "Strathaven Community Trust",
    "Lyle_Gateway": "Strathaven Community Trust",
}

# ── ANONYMISATION OPERATORS ───────────────────────────────────────────────────

OPERATORS = {
    "PERSON": OperatorConfig("replace", {"new_value": "[PERSON]"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
    "URL": OperatorConfig("replace", {"new_value": "[URL]"}),
    "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
    "DATE_TIME": OperatorConfig("keep", {}),
    "DEFAULT": OperatorConfig("keep", {}),
}


# ── ENGINE SETUP ──────────────────────────────────────────────────────────────

def build_analyzer() -> AnalyzerEngine:
    """Build the Presidio analyzer with retain list applied."""
    analyzer = AnalyzerEngine()
    return analyzer


def apply_replacement_map(text: str) -> str:
    """Replace known organisation names with fictional equivalents."""
    for real, fictional in REPLACEMENT_MAP.items():
        text = text.replace(real, fictional)
    return text


def is_retained(text: str, start: int, end: int) -> bool:
    """Check whether a detected entity overlaps with the retain list."""
    entity_text = text[start:end]
    for retained in RETAIN_LIST:
        if retained.lower() in entity_text.lower():
            return True
    return False


def anonymise_text(text: str, analyzer: AnalyzerEngine, anonymizer: AnonymizerEngine) -> str:
    """Run full anonymisation pipeline on a text string."""
    # Step 1 — apply organisation replacement map
    text = apply_replacement_map(text)

    # Step 2 — detect entities with Presidio
    results = analyzer.analyze(text=text, language="en")

    # Step 3 — filter out retained entities
    filtered = [r for r in results if not is_retained(text, r.start, r.end)]

    # Step 4 — anonymise remaining entities
    if filtered:
        anonymised = anonymizer.anonymize(
            text=text,
            analyzer_results=filtered,
            operators=OPERATORS,
        )
        return anonymised.text

    return text


# ── FORMAT HANDLERS ───────────────────────────────────────────────────────────

def extract_text_docx(filepath: Path) -> str:
    """Extract text from a DOCX file preserving paragraph structure."""
    doc = Document(filepath)
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text.strip())
    return "\n\n".join(paragraphs)


def extract_text_pdf(filepath: Path) -> str:
    """Extract text from a PDF file page by page."""
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())
    return "\n\n".join(pages)


def extract_text_html(filepath: Path) -> str:
    """Extract text from an HTML file."""
    from bs4 import BeautifulSoup
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(separator="\n").strip()


def extract_text(filepath: Path) -> str:
    """Route to the correct extractor based on file extension."""
    ext = filepath.suffix.lower()
    if ext == ".docx":
        return extract_text_docx(filepath)
    elif ext == ".pdf":
        return extract_text_pdf(filepath)
    elif ext in (".html", ".htm"):
        return extract_text_html(filepath)
    else:
        raise ValueError(f"Unsupported format: {ext} — {filepath.name}")


# ── MAIN PIPELINE ─────────────────────────────────────────────────────────────

def process_document(
    filepath: Path,
    output_dir: Path,
    analyzer: AnalyzerEngine,
    anonymizer: AnonymizerEngine,
) -> dict:
    """
    Process a single document through the anonymisation pipeline.
    Returns a result dictionary with status and any issues noted.
    """
    result = {
        "filename": filepath.name,
        "status": None,
        "output_file": None,
        "issues": [],
    }

    try:
        # Extract text
        raw_text = extract_text(filepath)

        # Anonymise
        clean_text = anonymise_text(raw_text, analyzer, anonymizer)

        # Write anonymised output as plain text
        output_path = output_dir / (filepath.stem + "_anonymised.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        result["status"] = "success"
        result["output_file"] = str(output_path)

    except Exception as e:
        result["status"] = "error"
        result["issues"].append(str(e))

    return result


def run_pipeline(source_dir: Path, output_dir: Path) -> None:
    """
    Run the anonymisation pipeline over all supported documents
    in the source directory.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    analyzer = build_analyzer()
    anonymizer = AnonymizerEngine()

    supported = {".docx", ".pdf", ".html", ".htm"}
    files = [f for f in source_dir.iterdir() if f.suffix.lower() in supported]

    if not files:
        print(f"No supported documents found in {source_dir}")
        return

    print(f"Processing {len(files)} documents...\n")
    results = []

    for filepath in sorted(files):
        print(f"  Processing: {filepath.name}")
        result = process_document(filepath, output_dir, analyzer, anonymizer)
        results.append(result)
        status = "✓" if result["status"] == "success" else "✗"
        print(f"  {status} {result['status'].upper()}")
        if result["issues"]:
            for issue in result["issues"]:
                print(f"    Issue: {issue}")

    # Write summary report
    summary_path = output_dir / "anonymisation_report.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    success = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")

    print(f"\nComplete — {success} succeeded, {errors} errors")
    print(f"Report saved to: {summary_path}")
    print(f"\nIMPORTANT: All outputs require human curator review")
    print(f"before being moved to repository/approved/")


# ── ENTRY POINT ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Paths relative to project root
    project_root = Path(__file__).resolve().parents[2]
    source_dir = project_root / "source-documents"
    output_dir = project_root / "repository" / "staging"

    print("Charity Compliance Engine — Anonymisation Pipeline")
    print("=" * 50)
    print(f"Source:  {source_dir}")
    print(f"Output:  {output_dir}")
    print(f"Note:    XLSX files require separate handling")
    print("=" * 50 + "\n")

    run_pipeline(source_dir, output_dir)
