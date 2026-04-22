# ADR-004: Document chunking strategy for Pinecone ingestion

**Date:** 2026-04-22  
**Status:** Accepted  
**Author:** Project lead  
**Recorded in CHANGELOG:** 0.1.8

---

## Context

Before documents can be embedded and stored in Pinecone, they must be split into chunks — discrete units of text that are individually embedded and retrieved. The chunking strategy directly determines retrieval quality. Poor chunking is the most common cause of RAG system failure and cannot be compensated for by prompt engineering alone.

The document inventory (37 documents) informs this decision. Key characteristics of the repository:

- Mostly single-topic policies and procedures (2-10 pages typically)
- A few longer documents — doc_004 (30 pages), doc_017 (27 pages), doc_020 (21 pages)
- Logically structured with headings, numbered sections, and clauses
- One XLSX (doc_010 — gift register template)
- One HTML (doc_040 — volunteer safeguarding guide)
- One PPTX (doc_001 excluded; no PPTX files remain for ingestion)
- Mix of DOCX and PDF formats

Compliance documents have specific characteristics that affect chunking:

- Section headings carry meaning — a chunk without its heading loses context
- Numbered clauses are often interdependent — splitting mid-clause loses coherence
- Policy documents have a standard structure (purpose, scope, definitions, procedure, review) — chunks should respect this structure
- Some documents reference other documents — cross-references should be preserved within chunks where possible

---

## Options considered

### Option 1 — Fixed-size chunking

Split every document into chunks of a fixed token count (e.g. 512 tokens) with a sliding overlap window (e.g. 50 tokens).

**Advantages**
- Simple to implement
- Consistent chunk sizes
- Well-supported by LangChain out of the box

**Disadvantages**
- Ignores document structure entirely — splits mid-sentence, mid-clause, mid-section
- Particularly damaging for compliance documents where clause boundaries matter
- Overlap helps but does not solve the structural problem
- Produces poor retrieval for policy documents with distinct named sections

### Option 2 — Semantic chunking

Use an embedding model to identify natural semantic boundaries in the text and split at points of maximum semantic shift.

**Advantages**
- Theoretically produces the most coherent chunks
- Respects meaning rather than token count

**Disadvantages**
- Computationally expensive
- Less predictable chunk sizes — harder to manage context window
- Overkill for documents that already have explicit structural signals (headings, numbered sections)
- Harder to debug when retrieval quality is poor

### Option 3 — Structure-aware chunking

Split documents at natural structural boundaries — section headings, numbered clauses, paragraph breaks — with a target chunk size and a maximum chunk size as guardrails.

**Advantages**
- Respects document structure — chunks align with how the document is actually organised
- Section headings are preserved at the start of each chunk providing context
- Predictable and debuggable
- Well-suited to policy and procedure documents with explicit headings and numbered sections
- LangChain's RecursiveCharacterTextSplitter supports this pattern

**Disadvantages**
- Requires more configuration than fixed-size chunking
- Very short sections may need to be merged with adjacent sections
- Very long sections may still need to be split — requiring a fallback strategy

### Option 4 — Document-level chunking (no splitting)

Store each document as a single chunk.

**Advantages**
- Maximum context preservation
- Simple to implement

**Disadvantages**
- Most documents exceed practical context window limits for retrieval
- Retrieval returns entire documents — too much noise for specific queries
- Defeats the purpose of vector retrieval for targeted compliance questions

---

## Decision

**Option 3 — Structure-aware chunking, with fixed-size fallback for oversized sections.**

The primary chunking strategy is structure-aware, splitting at section headings and numbered clause boundaries. The following parameters are adopted:

- **Target chunk size:** 400 tokens
- **Maximum chunk size:** 600 tokens
- **Minimum chunk size:** 100 tokens (sections smaller than this are merged with the next section)
- **Overlap:** 50 tokens between consecutive chunks from the same document
- **Heading preservation:** The nearest preceding heading is prepended to every chunk that does not begin with a heading
- **Fallback:** Sections exceeding 600 tokens are split using RecursiveCharacterTextSplitter at paragraph boundaries

### Special handling by format

**DOCX** — python-docx extracts text with paragraph and heading structure intact. Headings identified by style name (Heading 1, Heading 2 etc.). Split at heading boundaries first, then apply size guardrails.

**PDF** — pdfplumber extracts text page by page. Heading detection uses font size heuristics. Split at detected headings, with paragraph breaks as fallback. PDF extraction quality varies — curator spot-check recommended for PDFs post-chunking.

**XLSX (doc_010 — Gift Register template)** — tabular data. Not split. Converted to a structured text representation (column headers + row descriptions) and stored as a single chunk with a descriptive prefix. Metadata tagged separately to flag tabular format.

**HTML (doc_040 — Volunteer Safeguarding Guide)** — BeautifulSoup extracts text with heading tags (h1, h2, h3) preserved as structural signals. Split at heading boundaries following the same rules as DOCX.

---

## Rationale

Structure-aware chunking is the correct strategy for this repository because the documents are already well-structured. Headings and numbered sections are explicit signals that define where one topic ends and another begins — using them as chunk boundaries produces chunks that are coherent, retrievable, and usable as standalone reference material.

The 400-token target is chosen to balance two competing requirements. It is large enough to include sufficient context for a compliance clause or procedure step to be meaningful in isolation. It is small enough that multiple relevant chunks can be passed to Claude within the context window without crowding out the system prompt and charity profile.

Heading preservation is non-negotiable for this use case. A chunk beginning mid-section with no heading is ambiguous — it is not clear what policy area it relates to. Prepending the nearest heading restores that context at minimal token cost.

The fixed-size fallback for oversized sections is pragmatic. A small number of documents (doc_020 at 21 pages, doc_004 at 30 pages, doc_017 at 27 pages) may have sections that exceed 600 tokens. Paragraph-boundary splitting within those sections is preferable to arbitrary mid-sentence splitting.

---

## Consequences

- Chunking script lives in `ingestion/chunk/` — to be built in Stage 1
- LangChain RecursiveCharacterTextSplitter used as the core splitting mechanism
- python-docx, pdfplumber, and BeautifulSoup added as ingestion dependencies
- XLSX handling requires openpyxl — convert to structured text before chunking
- Chunk metadata must include `chunk_index` and `total_chunks` per document to support ordered retrieval where needed
- Post-chunking quality review required for all PDF documents — PDF text extraction is less reliable than DOCX
- doc_020 (21 pages), doc_004 (30 pages), and doc_017 (27 pages) flagged for careful chunking review — most likely to trigger fallback splitting
- Target chunk parameters (400/600/100 tokens) are initial values — to be tuned during Stage 2 retrieval quality testing
- A chunk preview script should be built alongside the chunking script to allow visual inspection of chunk boundaries before ingestion into Pinecone
