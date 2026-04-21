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
