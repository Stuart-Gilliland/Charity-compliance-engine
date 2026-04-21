# ADR-002: Streamlit as POC frontend framework

**Date:** 2026-04-21  
**Status:** Accepted  
**Author:** Project lead  
**Recorded in CHANGELOG:** 0.1.5

---

## Context

The POC requires a working browser-based interface that supports an intake form, a conversational refinement interface, and output display with download capability. The interface needs to be buildable without a dedicated frontend developer, using Claude-assisted development, and must be functional enough to test with real users at Stage 5.

---

## Options considered

### Option 1 — Streamlit

Streamlit is a Python-native framework that produces browser-based interfaces from pure Python code. No HTML, CSS, or JavaScript is required for standard components.

**Advantages**
- Python-native — consistent with the rest of the stack (FastAPI, LangChain, Presidio)
- No frontend development skills required
- Built-in support for forms, chat interfaces, file downloads, and session state
- Rapid iteration — changes are visible immediately on save
- Well-supported by Claude-assisted development
- Free and open source
- Adequate for internal POC use and trustee testing

**Disadvantages**
- Limited UI customisation compared to a full frontend framework
- Not suitable as a long-term production frontend at scale
- Concurrency limitations for high simultaneous user loads
- Less control over user experience detail

### Option 2 — React + FastAPI

A React frontend communicating with the FastAPI backend via REST API — the standard production web application architecture.

**Advantages**
- Full control over UI and user experience
- Scalable to production
- Standard architecture familiar to most developers

**Disadvantages**
- Requires frontend development skills
- Significantly more build time at POC stage
- Introduces JavaScript/TypeScript as a second language stack
- Premature optimisation for a POC whose core proposition is not yet proven

### Option 3 — Gradio

Gradio is similar to Streamlit — Python-native, browser-based, rapid to build.

**Advantages**
- Slightly simpler API than Streamlit for pure chat interfaces
- Good Hugging Face ecosystem integration

**Disadvantages**
- Less flexible for multi-step intake forms
- Smaller community and ecosystem than Streamlit
- Less suitable for the hybrid intake-plus-conversation interaction model

---

## Decision

**Option 1 — Streamlit for the POC.**

Streamlit is adopted for all POC interface development. A migration to React or an equivalent production frontend framework will be addressed in a separate ADR when the POC is proven and a web application is being planned.

---

## Rationale

The POC exists to prove one thing: that RAG over the curated repository produces useful, grounded, proportionate compliance outputs. The interface is a means to that end, not the end itself. Streamlit allows the interface to be built quickly and iterated on without frontend development expertise, keeping development effort focused on the pipeline and retrieval quality where it matters most at this stage.

The decision to use Streamlit is explicitly time-bounded to the POC. It is not a production architecture decision.

---

## Consequences

- All interface code lives in `app/` and is pure Python
- Session state for charity profiles managed via Streamlit session state
- File download handled via Streamlit's native download button
- When POC transitions to web application, a new ADR must be written covering frontend framework selection for production
- UI customisation is constrained — this is acceptable at POC stage and should not drive scope creep into frontend polish
