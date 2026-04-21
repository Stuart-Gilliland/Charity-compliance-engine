# Pinecone Metadata Schema
## Charity Compliance Engine

**Version:** 0.2.0  
**Date:** 2026-04-21  
**Status:** Draft — awaiting review  
**Author:** Project lead  
**Changes from v0.1.0:** Headcount bands restructured to reflect paid/volunteer mix. ICO and data protection compliance areas expanded with dedicated subarea taxonomy. `communications` added as a recognised gap area.

---

## Purpose

This document defines the metadata schema applied to every document chunk stored in Pinecone. The schema enables filtered, accurate retrieval based on a charity's profile — ensuring that outputs are proportionate, relevant, and grounded in appropriate source material.

Metadata is applied at ingestion. Every chunk must carry a complete set of metadata fields before it is admitted to the index. Chunks with incomplete metadata are rejected to the staging area for curator review.

---

## Design Principles

- **Retrieval accuracy over richness** — every field must earn its place by improving retrieval relevance. Fields that do not filter or rank results are not included.
- **Explicit gaps** — where the repository does not yet cover a compliance area, this is recorded in the schema and surfaced to the system prompt so the AI flags the gap rather than retrieving poor matches.
- **Proportionality** — size band and complexity fields allow the system to match documents to charities of comparable scale, avoiding over-engineering for small organisations or under-serving larger ones.
- **Auditability** — source and authority fields ensure every retrieved chunk can be traced to its origin.

---

## Schema Fields

### 1. Document identity

| Field | Type | Description | Example |
|---|---|---|---|
| `doc_id` | string | Unique identifier for the source document | `doc_001` |
| `chunk_id` | string | Unique identifier for this specific chunk | `doc_001_chunk_003` |
| `doc_title` | string | Descriptive title of the source document | `Safeguarding Policy — Small Charity Template` |
| `doc_type` | string | Type of document (see controlled list below) | `policy` |
| `source_authority` | string | Origin of the document (see controlled list below) | `repository` |
| `date_ingested` | string | ISO date of ingestion | `2026-04-21` |
| `version` | string | Version of the document if known | `1.2` |
| `anonymised` | boolean | Confirms anonymisation was applied at ingestion | `true` |
| `curator_approved` | boolean | Confirms human spot-check was completed | `true` |

**Controlled list — `doc_type`**

- `policy` — a formal organisational policy
- `procedure` — an operational procedure or process document
- `template` — a reusable document template
- `guidance` — regulatory or sector guidance (not a charity's own document)
- `framework` — a governance or compliance framework document
- `checklist` — a compliance or governance checklist
- `example` — an anonymised real-world example document

**Controlled list — `source_authority`**

- `repository` — anonymised real-world charity document from the curated repository
- `oscr` — Office of the Scottish Charity Regulator
- `scvo` — Scottish Council for Voluntary Organisations
- `ico` — Information Commissioner's Office
- `legislation` — primary or secondary legislation
- `other_regulator` — another recognised regulatory or sector body

---

### 2. Compliance area

| Field | Type | Description | Example |
|---|---|---|---|
| `compliance_area` | string | Primary compliance domain (see controlled list) | `safeguarding` |
| `compliance_subarea` | string | More specific topic within the domain | `safer_recruitment` |
| `repository_coverage` | string | Indicates depth of repository coverage for this area | `good` |

**Controlled list — `compliance_area` and `compliance_subarea`**

| `compliance_area` | `compliance_subarea` options | Current coverage |
|---|---|---|
| `governance` | `trustee_duties`, `conflicts_of_interest`, `board_meetings`, `delegated_authority`, `reserves_policy`, `risk_management`, `charity_constitution` | Good |
| `safeguarding` | `child_protection`, `adult_protection`, `safer_recruitment`, `pvg_scheme`, `reporting_obligations`, `lone_working`, `safeguarding_training` | Good |
| `data_protection` | `gdpr_policy`, `privacy_notices`, `consent_management`, `legitimate_interest`, `data_sharing_agreements`, `subject_access_requests`, `retention_schedules`, `data_breach_response`, `ico_registration`, `dpia` | Good — see ICO note below |
| `financial_controls` | `financial_procedures`, `fraud_prevention`, `signing_authorities`, `expenses_policy`, `reserves_policy`, `annual_accounts`, `independent_examination` | Good |
| `fundraising` | `fundraising_policy`, `donor_management`, `gift_aid`, `online_fundraising`, `fundraising_complaints` | Partial |
| `volunteering` | `volunteer_policy`, `volunteer_agreements`, `volunteer_induction`, `volunteer_expenses`, `volunteer_supervision` | Partial |
| `grant_management` | `grant_reporting`, `funder_compliance`, `conditions_management`, `project_monitoring` | Partial |
| `employment` | `employment_contracts`, `disciplinary_procedure`, `grievance_procedure`, `absence_management`, `equality_diversity`, `whistleblowing` | Gap |
| `premises_health_safety` | `health_safety_policy`, `risk_assessment`, `fire_safety`, `lone_working`, `accident_reporting` | Gap |
| `communications` | `social_media_policy`, `media_handling`, `public_communications`, `brand_guidelines` | Gap |

**Controlled list — `repository_coverage`**

- `good` — multiple real-world examples and guidance documents available
- `partial` — some documents available but limited in depth or range
- `gap` — area identified but not yet represented in the repository

---

#### ICO and data protection — expanded note

Data protection is treated as `good` coverage but the subarea taxonomy above reflects the full range of ICO requirements relevant to charities. The following subareas are particularly critical and should be prioritised in repository development:

| Subarea | Why critical for charities |
|---|---|
| `consent_management` | Charities frequently rely on consent as their lawful basis — often incorrectly. ICO guidance is specific and frequently misapplied. |
| `legitimate_interest` | Many charities process data under legitimate interest without conducting or documenting a legitimate interest assessment. |
| `data_sharing_agreements` | Charities sharing data with statutory partners, funders, or referral agencies require formal agreements. Frequently absent in practice. |
| `retention_schedules` | Retention of safeguarding records, financial records, and beneficiary data each carry different requirements. Often conflated or ignored. |
| `dpia` | Data Protection Impact Assessments required for high-risk processing — relevant to any charity holding sensitive personal data about vulnerable beneficiaries. |
| `ico_registration` | Most charities processing personal data must register with ICO. Many small charities are unaware of this obligation or believe they are exempt. |
| `data_breach_response` | 72-hour reporting obligation to ICO. Charities frequently lack a documented response procedure. |

---

### 3. Charity size and workforce model

Paid staff headcount and volunteer numbers are treated as separate dimensions. Most Scottish charities operate a mixed model and compliance obligations differ meaningfully depending on that mix.

| Field | Type | Description | Example |
|---|---|---|---|
| `income_band_min` | string | Minimum income band this document is relevant to | `under_25k` |
| `income_band_max` | string | Maximum income band this document is relevant to | `100k_500k` |
| `workforce_model` | string | Predominant workforce model (see controlled list) | `mixed` |
| `paid_staff_band` | string | Paid staff headcount band (see controlled list) | `1_5` |
| `volunteer_band` | string | Volunteer headcount band (see controlled list) | `11_50` |
| `complexity` | string | Organisational complexity level | `low` |

**Controlled list — income bands**

- `under_25k`
- `25k_100k`
- `100k_500k`
- `500k_1m`
- `over_1m`

**Controlled list — `workforce_model`**

- `volunteer_led` — entirely or almost entirely volunteer-run, no or negligible paid staff
- `mixed` — meaningful combination of paid staff and volunteers
- `staff_led` — primarily paid staff, volunteers play a minor or no role

This field drives top-level document matching. A safeguarding policy written for a volunteer-led organisation is structurally different from one written for a staff-led service delivery team and should not be retrieved interchangeably.

**Controlled list — `paid_staff_band`**

- `none` — no paid staff
- `1_5`
- `6_20`
- `21_50`
- `over_50`

**Controlled list — `volunteer_band`**

- `none` — no volunteers
- `1_10`
- `11_50`
- `51_200`
- `over_200`

**Controlled list — `complexity`**

- `low` — simple structure, single activity, limited public interaction
- `medium` — multiple activities or income streams, some public interaction
- `high` — complex structure, regulated activities, significant public interaction or vulnerable beneficiaries

---

### 4. Regulatory and legislative references

| Field | Type | Description | Example |
|---|---|---|---|
| `legislation_refs` | list[string] | Specific legislation this document references | `["Charities and Trustee Investment (Scotland) Act 2005", "UK GDPR"]` |
| `oscr_principle` | list[string] | OSCR good governance principles this document relates to | `["Principle 1", "Principle 4"]` |
| `jurisdiction` | string | Jurisdiction this document applies to | `scotland` |

**Legislation reference standard**

Always use the full formal name of the Act or Regulation. Abbreviations are not used in this field to ensure consistent matching. Examples:

- `Charities and Trustee Investment (Scotland) Act 2005`
- `Charities (Regulation and Administration) (Scotland) Act 2023`
- `Protection of Vulnerable Groups (Scotland) Act 2007`
- `UK General Data Protection Regulation`
- `Data Protection Act 2018`
- `Equality Act 2010`
- `Health and Safety at Work etc. Act 1974`

**Controlled list — `jurisdiction`**

- `scotland` — Scotland-specific
- `uk_wide` — applies across UK
- `scotland_and_england` — dual jurisdiction (note carefully)

---

### 5. Activity and beneficiary context

| Field | Type | Description | Example |
|---|---|---|---|
| `activity_type` | list[string] | Type of charitable activity this document is relevant to | `["direct_service_delivery", "grant_giving"]` |
| `beneficiary_group` | list[string] | Beneficiary groups that make this document particularly relevant | `["children", "vulnerable_adults"]` |
| `regulated_activity` | boolean | Whether this document relates to a regulated activity under safeguarding legislation | `true` |

**Controlled list — `activity_type`**

- `direct_service_delivery`
- `grant_giving`
- `campaigning_advocacy`
- `community_development`
- `arts_culture`
- `sport_recreation`
- `education_training`
- `housing_support`
- `health_social_care`
- `environmental`
- `international`
- `religious`

**Controlled list — `beneficiary_group`**

- `children`
- `vulnerable_adults`
- `older_people`
- `people_with_disabilities`
- `general_public`
- `specific_community`
- `animals`
- `environment`

---

## Example — Fully Tagged Chunk

```json
{
  "doc_id": "doc_042",
  "chunk_id": "doc_042_chunk_002",
  "doc_title": "Safeguarding Policy — Mixed Workforce Charity Example",
  "doc_type": "policy",
  "source_authority": "repository",
  "date_ingested": "2026-04-21",
  "version": "2.0",
  "anonymised": true,
  "curator_approved": true,
  "compliance_area": "safeguarding",
  "compliance_subarea": "safer_recruitment",
  "repository_coverage": "good",
  "income_band_min": "25k_100k",
  "income_band_max": "500k_1m",
  "workforce_model": "mixed",
  "paid_staff_band": "6_20",
  "volunteer_band": "11_50",
  "complexity": "medium",
  "legislation_refs": [
    "Protection of Vulnerable Groups (Scotland) Act 2007",
    "Charities and Trustee Investment (Scotland) Act 2005"
  ],
  "oscr_principle": ["Principle 1", "Principle 3"],
  "jurisdiction": "scotland",
  "activity_type": ["direct_service_delivery", "health_social_care"],
  "beneficiary_group": ["children", "vulnerable_adults"],
  "regulated_activity": true
}
```

---

## Gap Handling

Where `repository_coverage` is `gap`, the ingestion pipeline will:

1. Still create the metadata entry to register the gap explicitly
2. Flag the area in a `repository_gaps.json` file maintained in `docs/metadata-schema/`
3. The system prompt will check this gaps file and explicitly instruct Claude to acknowledge the limitation and direct the user to seek appropriate external guidance rather than retrieving weak matches

**Current registered gaps**

| Area | Gap reason | Recommended interim action |
|---|---|---|
| `employment` | Not yet in repository | Direct users to ACAS, SCVO HR guidance, and specialist employment advice |
| `premises_health_safety` | Not yet in repository | Direct users to HSE guidance and local authority environmental health |
| `communications` | Not yet in repository | Direct users to SCVO communications resources |

---

## Schema Versioning

This schema will evolve as the repository grows. All changes must be:

1. Recorded in `CHANGELOG.md` with rationale
2. Reflected in a new version number on this document
3. Applied to existing chunks on next re-ingestion (a re-ingestion script will be maintained in `ingestion/embed/`)

---

## Next Steps

- [ ] Create `repository_gaps.json` to formally register current gap areas
- [ ] Build ingestion validation script that rejects chunks with incomplete metadata
- [ ] Define chunking strategy (see `ingestion/chunk/`) that preserves metadata context
- [ ] Test schema against first batch of real documents
- [ ] Review ICO subarea coverage against actual documents in repository
- [ ] Assess whether `workforce_model` field alone is sufficient for top-level filtering or whether `paid_staff_band` + `volunteer_band` combination queries are needed
