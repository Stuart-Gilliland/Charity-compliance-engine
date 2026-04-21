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
