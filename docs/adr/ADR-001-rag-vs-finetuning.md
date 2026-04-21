# ADR-001: RAG as primary AI architecture over fine-tuning

**Date:** 2026-04-21  
**Status:** Accepted  
**Author:** Project lead  
**Recorded in CHANGELOG:** 0.1.4

---

## Context

The compliance engine requires Claude to generate outputs that are grounded in a specific, curated repository of Scottish charity compliance documents and authoritative regulatory guidance. A core project principle is that the AI must not fabricate compliance requirements or reference legislation that does not exist.

Two primary approaches were considered for achieving this grounding: Retrieval-Augmented Generation (RAG) and fine-tuning of the underlying model.

---

## Options considered

### Option 1 — Retrieval-Augmented Generation (RAG)

RAG keeps the base model unchanged. At query time, relevant document chunks are retrieved from a vector database (Pinecone) based on the charity's profile and the query context, and passed to Claude as part of the prompt. Claude generates outputs using those retrieved chunks as its grounding source.

**Advantages**
- Repository can be updated, corrected, and extended without retraining
- Transparency — retrieved source chunks can be cited in outputs
- Gaps are detectable and surfaceable — if retrieval returns nothing relevant, the system knows and can flag it
- No risk of the model hallucinating content from training data, as retrieved chunks anchor the response
- Cost-effective — no training runs required
- Aligns with the project principle of drawing only on the curated repository

**Disadvantages**
- Retrieval quality is dependent on chunking strategy and metadata schema design
- Complex queries may require multiple retrieval passes
- Context window limits constrain how many chunks can be passed per query

### Option 2 — Fine-tuning

Fine-tuning involves training the model on the curated repository documents so that compliance knowledge is embedded in the model weights rather than retrieved at runtime.

**Advantages**
- No retrieval step required at inference time
- Can produce more fluent, integrated outputs for well-represented topics

**Disadvantages**
- Repository updates require retraining — expensive and slow
- Gaps are invisible — the model may generate plausible-sounding but incorrect content in areas of weak training data
- No citation mechanism — outputs cannot be traced to source documents
- Fine-tuning does not eliminate hallucination; it may embed incorrect patterns from training data
- Requires significant volume of high-quality training data — the repository is not yet at that scale
- Conflicts with the project principle of not inferring beyond available information

### Option 3 — Hybrid (RAG now, fine-tuning later)

Use RAG for the POC and initial production phases. Revisit fine-tuning once the repository reaches sufficient scale and RAG is proven.

---

## Decision

**Option 3 — RAG now, fine-tuning deferred.**

RAG is adopted as the primary architecture for the POC and all foreseeable production phases. Fine-tuning is explicitly deferred and will only be reconsidered when:

1. The repository contains sufficient volume and quality of documents to support meaningful fine-tuning
2. RAG has been proven to work well and its limitations are clearly understood
3. A specific capability gap exists that RAG cannot address and fine-tuning demonstrably can

---

## Rationale

RAG is the correct architecture for this project at this stage for three specific reasons.

First, the gap visibility argument is decisive for a compliance tool. A system that silently generates plausible but incorrect compliance guidance is more dangerous than one that acknowledges it does not have sufficient grounding. RAG makes gaps detectable; fine-tuning conceals them.

Second, the repository is actively growing. Fine-tuning a static snapshot of an evolving repository would require repeated retraining. RAG allows the repository to be updated and the system to immediately benefit from those updates.

Third, the project's regulatory and ethical obligations require traceability. Outputs that cannot be traced to source documents are harder to defend to trustees, regulators, or beneficiaries. RAG enables citation; fine-tuning does not.

---

## Consequences

- Pinecone is confirmed as the vector store (see metadata schema v0.2.0)
- Chunking strategy and metadata schema quality are critical success factors — poor retrieval directly degrades output quality
- The system prompt must instruct Claude to work from retrieved chunks and flag when retrieval is insufficient
- Context window management becomes an engineering concern — large queries may require prioritisation of retrieved chunks
- Fine-tuning remains on the roadmap but requires a formal ADR before adoption
- Retrieval quality testing (Stage 2) is a genuine gate before interface development begins
