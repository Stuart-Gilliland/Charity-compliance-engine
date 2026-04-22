"""
Test script — runs anonymisation on a single document.
Run from project root with venv active:
    python -m ingestion.anonymise.test_single
"""

from pathlib import Path
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from ingestion.anonymise.anonymise import process_document

project_root = Path(__file__).resolve().parents[2]
test_file = project_root / "source-documents" / "EPS Appropriate Behaviour Policy v1.2 20250921.docx"
output_dir = project_root / "ingestion" / "anonymise" / "test_output"
output_dir.mkdir(exist_ok=True)

print(f"Testing anonymisation on: {test_file.name}")
print(f"Output directory: {output_dir}\n")

if not test_file.exists():
    print(f"ERROR: File not found at {test_file}")
else:
    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()
    result = process_document(test_file, output_dir, analyzer, anonymizer)
    print(f"Status:  {result['status']}")
    print(f"Output:  {result['output_file']}")
    if result['issues']:
        print(f"Issues:  {result['issues']}")
    else:
        print("\nNo issues — check output file for anonymisation quality")
