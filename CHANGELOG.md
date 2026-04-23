### [0.1.1] — 2026-04-21
**Type:** Infrastructure  
**Author:** Project lead  
**Summary:** Repository structure fully initialised. README.md replaced with full project documentation. CHANGELOG.md format established. All placeholder folders created.  
**Rationale:** Establishing a clean, agreed folder structure before any code or documents are added prevents reorganisation later and ensures every subsequent contribution lands in the right place. README captures project scope, disclaimers, regulatory context, and AI usage principles from the outset — consistent with the governance standards the project supports.  
**Dependencies or implications:** Folder structure reflects the five-stage POC build sequence. Any structural changes from this point should be recorded here with rationale.

### [0.1.2] — 2026-04-21
**Type:** Infrastructure  
**Author:** Project lead  
**Summary:** Full folder structure created and pushed to GitHub. `.env.example` created with all anticipated environment variables documented.  
**Rationale:** Single-script folder creation ensures consistency and is repeatable. `.env.example` establishes the pattern of never committing secrets whilst documenting exactly what credentials the project requires.  
**Dependencies or implications:** `.env` (with real values) must be added to `.gitignore` before any API keys are configured locally. Pinecone index name set as `charity-compliance` — change here and in code if renamed.

### [0.1.3] — 2026-04-21
**Type:** Schema  
**Author:** Project lead  
**Summary:** Metadata schema v0.2.0 added to `docs/metadata-schema/`. Repository gaps register `repository_gaps.json` created and committed.  
**Rationale:** Metadata schema is the foundational design decision for retrieval quality — all subsequent ingestion depends on it. Gap register ensures the system explicitly flags areas of weak or absent coverage rather than retrieving poor matches. Both documents reflect the project principle of transparency over false confidence.  
**Dependencies or implications:** Schema v0.2.0 introduces three-field workforce model and dedicated ICO section — both must be applied consistently at ingestion. Gap register must be kept current as repository is enhanced. System prompt (Stage 3) must reference gap register at runtime.

### [0.1.4] — 2026-04-21
**Type:** Decision  
**Author:** Project lead  
**Summary:** ADR-001 created — RAG adopted as primary AI architecture, fine-tuning explicitly deferred.  
**Rationale:** RAG makes knowledge gaps visible and outputs traceable to source documents. Both properties are essential for a compliance tool where silent errors are more dangerous than acknowledged limitations. Fine-tuning conceals gaps and removes traceability.  
**Dependencies or implications:** Pinecone confirmed as vector store. Chunking strategy and metadata schema quality are now critical success factors. Retrieval quality testing (Stage 2) is a hard gate before interface development.

### [0.1.5] — 2026-04-21
**Type:** Decision  
**Author:** Project lead  
**Summary:** ADR-002 and ADR-003 created. Streamlit adopted as POC frontend — explicitly time-bounded to POC stage. Microsoft Presidio adopted for anonymisation with mandatory human spot-check gate.  
**Rationale:** Streamlit keeps frontend effort proportionate to POC goals. Presidio runs locally ensuring no sensitive data transmitted externally, with retain list support for authoritative entity names. Neither decision is permanent — both will be revisited at web application stage.  
**Dependencies or implications:** Streamlit migration to production frontend requires its own ADR. Presidio retain list must be actively maintained. Curator spot-check is a hard gate enforced via metadata flag — not optional.

### [0.1.6] — 2026-04-21
**Type:** Decision  
**Author:** Project lead  
**Summary:** Document inventory created with 38 documents. doc_005 (Council Meeting Agenda and Minutes) and doc_006 (Council Office Bearers and Lead Roles) intentionally excluded.  
**Rationale:** Both excluded documents contain named individuals. Risk of incomplete anonymisation considered too high given sensitivity of meeting minutes and named role holders. Exclusion is the proportionate decision. Doc IDs 005 and 006 are retired and will not be reused.  
**Dependencies or implications:** Repository contains 38 documents across two source organisations — EPS (anonymised to Caledonian Arts Forum) and Lyle Gateway (anonymised to Strathaven Community Trust). XLSX and HTML formats flagged for special handling in ingestion pipeline. doc_032 and doc_039 require no anonymisation. Inventory to be reviewed and page counts added in next session.

### [0.1.7] — 2026-04-22
**Type:** Schema + Decision  
**Author:** Project lead  
**Summary:** Document inventory updated. doc_001 excluded (91 pages, not critical). doc_032 corrected — Church of Scotland Safeguarding Handbook not Scottish Government. Two attribution columns added: attribution_required and attribution_text. Source authority controlled list extended with faith_organisation and legal_publisher.  
**Rationale:** doc_001 would chunk poorly and add noise at 91 pages. Church of Scotland correction materially changes tagging and retrieval context. Attribution fields address the overnight concern about third-party content — Burness Paull templates and Church of Scotland materials require attribution wherever referenced. This is a non-negotiable requirement regardless of how content is used.  
**Dependencies or implications:** Metadata schema v0.2.0 needs a minor update to reflect new source_authority values and attribution fields — will be addressed in v0.3.0 alongside chunking strategy decisions. System prompt must reference attribution_required flag and include attribution_text in any output that draws on attributed documents. Repository now contains 37 documents for ingestion.

### [0.1.8] — 2026-04-22
**Type:** Decision  
**Author:** Project lead  
**Summary:** ADR-004 created — structure-aware chunking adopted as primary strategy. Target chunk size 400 tokens, maximum 600, minimum 100, overlap 50. Special handling defined for XLSX and HTML formats. Fixed-size fallback for oversized sections.  
**Rationale:** Repository documents are well-structured with explicit headings and numbered sections. Structure-aware chunking respects that organisation, producing coherent retrievable chunks. Fixed-size chunking would split across clause boundaries, damaging retrieval quality for compliance queries.  
**Dependencies or implications:** python-docx, pdfplumber, BeautifulSoup, openpyxl added as ingestion dependencies. Chunk parameters are initial values subject to tuning in Stage 2. doc_020, doc_004, and doc_017 flagged as highest risk for chunking quality — priority review items. Chunk preview script required alongside chunking script before any Pinecone ingestion.

### [0.1.9] — 2026-04-22
**Type:** Build  
**Author:** Project lead  
**Summary:** Anonymisation script v0.1.0 added to `ingestion/anonymise/`. Presidio pipeline with retain list, replacement map, and format handlers for DOCX, PDF, and HTML. Outputs written to `repository/staging/` as plain text files with anonymisation report.  
**Rationale:** First working code in the project. Anonymisation is the mandatory first step before any document enters the repository. Script includes retain list covering all authoritative sources and legislation, and replacement map converting real organisation names to fictional equivalents for readability.  
**Dependencies or implications:** XLSX files (doc_010) not handled by this script — require separate processing. All outputs require human curator review before promotion to repository/approved/. Script must be run from project root with venv active.

### [0.2.0] — 2026-04-22
**Type:** Build  
**Author:** Project lead  
**Summary:** Anonymisation pipeline tested and validated on two documents. Three issues identified and resolved — combined organisation name replacement, underscore-format name redaction, and partial email pattern redaction. Pipeline confirmed clean on both a simple policy and a document containing named individuals and email fragments.  
**Rationale:** Testing against a document with real edge cases (named individual in non-standard format, partial email addresses) validated that the pipeline handles real-world content correctly. All identified issues resolved before running full pipeline across all 37 documents.  
**Dependencies or implications:** Pipeline ready for full run across source-documents/. XLSX (doc_010) still requires separate handling. Human curator review of all outputs remains mandatory before promotion to repository/approved/.

### [0.2.1] — 2026-04-22
**Type:** Build  
**Author:** Project lead  
**Summary:** Full anonymisation pipeline run completed — 36 of 37 documents processed successfully, 0 errors. Anonymised outputs written to repository/staging/. XLSX gift register (doc_010) not processed — requires separate handling as confirmed in ADR-004.  
**Rationale:** First full pipeline run validates that the anonymisation approach works across all supported formats (DOCX, PDF, HTML) and document types in the repository.  
**Dependencies or implications:** All 36 outputs require human curator review before promotion to repository/approved/. Curator review is the next step before chunking and embedding can begin. XLSX handling to be addressed separately.

### [0.2.2] — 2026-04-23
**Type:** Schema + Decision  
**Author:** Project lead  
**Summary:** KB register created at docs/kb-register/kb-register.json. Three knowledge types formalised — Type 1 charity documents, Type 2 external reference summaries, Type 3 structured KB additions. 37 Type 1 entries, 15 Type 3 SCVO governance template entries, 2 Type 2 placeholder entries for OSCR and ICO summaries. Three Pinecone namespaces defined — charity-docs, external-refs, kb-additions. Quarterly review cycle established with next review due 2026-07-01.  
**Rationale:** KB register provides single source of truth for all repository content. Essential for managing attribution obligations, tracking ingestion status, and supporting the quarterly review cycle. SCVO governance templates added as first Type 3 content — covers all five Scottish charity governance structures with guidance, template and additional clauses per structure.  
**Dependencies or implications:** Pinecone index configuration must be updated to support three namespaces. SCVO templates require separate ingestion pipeline run — no anonymisation needed but attribution metadata must be applied. Two Type 2 summaries flagged as not_yet_written — priority task before Stage 2 retrieval testing. source-documents-kb/ added to gitignore.
