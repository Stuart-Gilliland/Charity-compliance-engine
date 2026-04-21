# Charity Compliance Engine

An AI-supported compliance framework generator for Scottish charities, built on a curated repository of real-world governance documents and authoritative regulatory guidance.

---

## Purpose

This project supports the design and tailoring of compliance frameworks for individual Scottish charities. It is not a generic template generator — outputs are proportionate to each charity's size, risk profile, activities, and existing governance arrangements.

The system draws on a curated repository of compliance documents implemented in practice across Scottish charities, supplemented by guidance from OSCR, SCVO, ICO, and other relevant authorities.

---

## Important Disclaimers

- Outputs are guidance materials and draft frameworks only
- They do not constitute legal, regulatory, or financial advice
- No assurance is given that generated materials fully meet the requirements of OSCR or any other regulator
- Final responsibility for reviewing, approving, and implementing any compliance framework rests with the charity's trustees
- Independent legal or professional advice should be sought where appropriate

---

## Scope

**In scope**
- Scottish charities registered with OSCR
- Proportionate, risk-based compliance frameworks
- Governance documents, policies, and procedures
- Tailored outputs based on structured charity profiles

**Out of scope**
- Legal advice
- Financial or investment advice
- Charities outside Scottish jurisdiction (without explicit adaptation)
- Automated compliance assurance or audit sign-off

---

## AI Usage Principles

- The AI draws only on the curated repository and explicitly defined regulatory context
- It does not infer beyond available information or fabricate compliance requirements
- Uncertainty, gaps, and areas requiring professional judgement are explicitly flagged
- Only real legislation is referenced — no generic generation of perceived laws
- Clarity and usability are prioritised over exhaustive completeness

---

## Project Status

**Current stage:** POC — internal use only  
**Visibility:** Private  
**Not yet:** Suitable for use with live charities without human review of all outputs

---

## Repository Structure

```
charity-compliance-engine/
│
├── README.md                  # This file
├── CHANGELOG.md               # Decision and change log
│
├── docs/                      # Design documents and architecture
│   ├── architecture/          # System architecture diagrams and notes
│   ├── metadata-schema/       # Pinecone metadata schema design
│   └── adr/                   # Architecture Decision Records
│
├── ingestion/                 # Document processing pipeline
│   ├── anonymise/             # Presidio configuration and redaction scripts
│   ├── chunk/                 # Document chunking strategy and scripts
│   └── embed/                 # Pinecone embedding and upload scripts
│
├── pipeline/                  # FastAPI + LangChain orchestration layer
│
├── app/                       # Streamlit user interface
│
├── prompts/                   # Versioned system prompts and templates
│
├── tests/                     # Test queries and retrieval evaluation
│   └── retrieval/             # Stage 2 query sets and results
│
├── repository/                # Anonymised source documents
│   ├── staging/               # Candidate documents awaiting curator review
│   └── approved/              # Cleared for ingestion into Pinecone
│
└── .env.example               # Environment variable template (no secrets)
```

---

## Setup

_To be completed as each stage is built. See CHANGELOG.md for current status._

---

## Regulatory Context

This project is designed with reference to:

- **Charities and Trustee Investment (Scotland) Act 2005**
- **Charities (Regulation and Administration) (Scotland) Act 2023**
- **UK GDPR and Data Protection Act 2018**
- **OSCR guidance and good governance publications**
- **SCVO resources for Scottish voluntary organisations**
- **ICO guidance relevant to charity data processing**

---

## Contributing

This is a private project. All contributions should be discussed with the project lead before implementation. All significant decisions must be recorded in CHANGELOG.md.
