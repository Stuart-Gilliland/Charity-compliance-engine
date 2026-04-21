# ADR-003: Microsoft Presidio for document anonymisation

**Date:** 2026-04-21  
**Status:** Accepted  
**Author:** Project lead  
**Recorded in CHANGELOG:** 0.1.5

---

## Context

The document repository is seeded with real compliance documents from Scottish charities. These documents may contain names of individuals, names of organisations, addresses, and other identifying information. A core confidentiality requirement is that all such information is anonymised before any document is chunked, embedded, or stored in Pinecone.

Anonymisation must occur at ingestion — before any data touches the vector store. The original pre-anonymisation documents must be stored separately with access controls and must never enter the retrieval pipeline.

The anonymisation approach must also support a configurable retain list — a set of entity names that should never be redacted because they are authoritative references required for retrieval (OSCR, SCVO, ICO, specific legislation names, etc.).

---

## Options considered

### Option 1 — Microsoft Presidio

Presidio is an open source PII detection and anonymisation framework developed by Microsoft. It uses Named Entity Recognition (NER) to identify personal and organisational information and replaces it with configurable placeholders.

**Advantages**
- Built specifically for PII detection and anonymisation — not a general NLP tool repurposed
- Supports configurable allow-lists (retain list) natively
- Replacements are configurable — `[PERSON]`, `[CHARITY]`, `[ADDRESS]` etc.
- Runs entirely locally — no data sent to external APIs during anonymisation
- Open source and free
- Python-native — consistent with the rest of the stack
- Actively maintained with good documentation
- Supports custom recognisers for domain-specific entity types

**Disadvantages**
- NER accuracy is not perfect — edge cases require human spot-check
- Scottish charity-specific terminology may require custom recogniser configuration
- Does not guarantee 100% anonymisation — curator review gate is still required

### Option 2 — spaCy with custom NER pipeline

spaCy is a general-purpose NLP library with strong NER capabilities. A custom anonymisation pipeline could be built on top of it.

**Advantages**
- Highly flexible and customisable
- Excellent transformer-based models available
- Strong community and documentation

**Disadvantages**
- Anonymisation logic would need to be built from scratch — Presidio provides this out of the box
- More engineering effort for equivalent outcome
- No native allow-list or placeholder replacement mechanism

### Option 3 — Manual anonymisation by curator

All documents anonymised manually by the human curator before ingestion.

**Advantages**
- 100% accuracy if done carefully
- No tooling complexity

**Disadvantages**
- Not scalable as the repository grows
- Introduces human error and inconsistency
- Does not scale to the knowledge feedback loop where new documents enter from engagements

### Option 4 — Commercial PII redaction API

Third-party API services offering PII detection and redaction.

**Advantages**
- High accuracy with minimal configuration

**Disadvantages**
- Documents containing sensitive charity information sent to external services
- Cost at scale
- Data sovereignty concerns — particularly relevant given GDPR obligations
- Dependency on third-party service availability

---

## Decision

**Option 1 — Microsoft Presidio, with mandatory human spot-check as a second layer.**

Presidio is adopted as the automated anonymisation layer. It is not treated as a complete solution in isolation — all documents pass through a human curator spot-check before being admitted to the approved repository. The combination of automated NER and human review provides the appropriate balance of scalability and accuracy.

---

## Rationale

Presidio is the correct tool because it was built for exactly this use case. Running locally ensures no sensitive charity data is transmitted externally during processing, which is a firm requirement given the nature of the documents. The retain list mechanism directly addresses the need to preserve authoritative entity names.

The mandatory spot-check gate is non-negotiable. Presidio will miss edge cases — particularly role-based references, indirect identifiers, and Scottish-specific terminology. Human review catches what automated NER misses and provides an audit record that a document was reviewed before ingestion.

---

## Consequences

- Presidio configured in `ingestion/anonymise/` with retain list and custom placeholder definitions
- Retain list must be maintained as the repository grows — new authoritative sources added as encountered
- Original pre-anonymisation documents stored in access-controlled location, never in the retrieval pipeline
- Curator spot-check is a mandatory step — ingestion pipeline must enforce this via the `curator_approved` metadata flag
- Custom recognisers to be developed for Scottish charity-specific terminology as edge cases are identified during testing
- Re-anonymisation script must be maintained for cases where the retain list or recogniser configuration changes
- GDPR documentation should record Presidio as the anonymisation tool and describe the process — this supports accountability obligations under UK GDPR Article 5(2)
