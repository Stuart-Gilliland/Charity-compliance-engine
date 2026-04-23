"""
Anonymisation pipeline for the Charity Compliance Engine.
Reads source and output paths from .env file.
"""

import re
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from docx import Document
import pdfplumber

load_dotenv()

RETAIN_LIST = [
    "OSCR", "Office of the Scottish Charity Regulator",
    "SCVO", "Scottish Council for Voluntary Organisations",
    "ICO", "Information Commissioner's Office",
    "Disclosure Scotland", "Protection of Vulnerable Groups", "PVG",
    "Fundraising Regulator", "HMRC", "Companies House",
    "Office of the Public Guardian", "Care Inspectorate",
    "Scottish Government", "UK Government", "ACAS",
    "Health and Safety Executive", "HSE", "Volunteer Scotland",
    "Burness Paull", "Church of Scotland",
    "Charities and Trustee Investment (Scotland) Act 2005",
    "Charities (Regulation and Administration) (Scotland) Act 2023",
    "UK GDPR", "GDPR", "Data Protection Act 2018",
    "Protection of Vulnerable Groups (Scotland) Act 2007",
    "Equality Act 2010", "Employment Rights Act 1996",
    "Health and Safety at Work etc. Act 1974",
    "Freedom of Information (Scotland) Act 2002",
    "Scotland", "Scottish", "United Kingdom", "UK",
]

REPLACEMENT_MAP = {
    "Edinburgh Photographic Society (EPS)": "Caledonian Arts Forum",
    "Edinburgh Photographic Society": "Caledonian Arts Forum",
    "EPS": "Caledonian Arts Forum",
    "Lyle Gateway": "Strathaven Community Trust",
    "Lyle_Gateway": "Strathaven Community Trust",
}

UNDERSCORE_NAME_PATTERN = re.compile(r'\b[A-Z][a-z]+_[A-Z][a-z]+\b')
FULL_EMAIL_PATTERN = re.compile(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
TRAILING_AT_PATTERN = re.compile(r'\b[a-zA-Z0-9._%+-]+@(?=[\s,]|$)')
LEADING_AT_PATTERN = re.compile(r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')

OPERATORS = {
    "PERSON": OperatorConfig("replace", {"new_value": "[PERSON]"}),
    "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
    "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
    "URL": OperatorConfig("replace", {"new_value": "[URL]"}),
    "LOCATION": OperatorConfig("keep", {}),
    "DATE_TIME": OperatorConfig("keep", {}),
    "DEFAULT": OperatorConfig("keep", {}),
}


def build_analyzer():
    return AnalyzerEngine()


def apply_replacement_map(text):
    for real, fictional in REPLACEMENT_MAP.items():
        text = text.replace(real, fictional)
    return text


def apply_pattern_redaction(text):
    text = UNDERSCORE_NAME_PATTERN.sub("[PERSON]", text)
    text = FULL_EMAIL_PATTERN.sub("[EMAIL]", text)
    text = TRAILING_AT_PATTERN.sub("[EMAIL]", text)
    text = LEADING_AT_PATTERN.sub("[EMAIL]", text)
    return text


def is_retained(text, start, end):
    entity_text = text[start:end]
    for retained in RETAIN_LIST:
        if retained.lower() in entity_text.lower():
            return True
    return False


def anonymise_text(text, analyzer, anonymizer):
    text = apply_replacement_map(text)
    text = apply_pattern_redaction(text)
    results = analyzer.analyze(text=text, language="en")
    filtered = [r for r in results if not is_retained(text, r.start, r.end)]
    if filtered:
        anonymised = anonymizer.anonymize(
            text=text,
            analyzer_results=filtered,
            operators=OPERATORS,
        )
        return anonymised.text
    return text


def extract_text_docx(filepath):
    doc = Document(filepath)
    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text.strip())
    return "\n\n".join(paragraphs)


def extract_text_pdf(filepath):
    pages = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text and text.strip():
                pages.append(text.strip())
    return "\n\n".join(pages)


def extract_text_html(filepath):
    from bs4 import BeautifulSoup
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text(separator="\n").strip()


def extract_text(filepath):
    ext = filepath.suffix.lower()
    if ext == ".docx":
        return extract_text_docx(filepath)
    elif ext == ".pdf":
        return extract_text_pdf(filepath)
    elif ext in (".html", ".htm"):
        return extract_text_html(filepath)
    else:
        raise ValueError(f"Unsupported format: {ext} — {filepath.name}")


def process_document(filepath, output_dir, analyzer, anonymizer):
    result = {
        "filename": filepath.name,
        "status": None,
        "output_file": None,
        "issues": [],
    }
    try:
        raw_text = extract_text(filepath)
        clean_text = anonymise_text(raw_text, analyzer, anonymizer)
        output_path = output_dir / (filepath.stem + "_anonymised.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(clean_text)
        result["status"] = "success"
        result["output_file"] = str(output_path)
    except Exception as e:
        result["status"] = "error"
        result["issues"].append(str(e))
    return result


def run_pipeline(source_dir, output_dir):
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
    summary_path = output_dir / "anonymisation_report.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    success = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")
    print(f"\nComplete — {success} succeeded, {errors} errors")
    print(f"Report saved to: {summary_path}")
    print(f"\nIMPORTANT: All outputs require human curator review")
    print(f"before being moved to repository/approved/")


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[2]

    source_docs = os.getenv("SOURCE_DOCS_PATH")
    if not source_docs:
        print("ERROR: SOURCE_DOCS_PATH not set in .env file")
        print("Copy .env.example to .env and configure paths for this machine")
        exit(1)

    source_dir = Path(source_docs)
    output_dir = project_root / "repository" / "staging"

    if not source_dir.exists():
        print(f"ERROR: Source directory not found: {source_dir}")
        print("Check SOURCE_DOCS_PATH in .env is correct for this machine")
        exit(1)

    print("Charity Compliance Engine — Anonymisation Pipeline")
    print("=" * 50)
    print(f"Source:  {source_dir}")
    print(f"Output:  {output_dir}")
    print(f"Note:    XLSX files require separate handling")
    print("=" * 50 + "\n")

    run_pipeline(source_dir, output_dir)
