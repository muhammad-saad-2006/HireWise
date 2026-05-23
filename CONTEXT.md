# HireWise — Project Context

> Paste this entire file at the start of every new Claude chat for this project.
> Say: "Read this context before we start coding." That's it.

---

## What is HireWise?

HireWise is a two-sided AI recruitment platform that acts as an intelligent HR system.
Companies post job roles with custom rules. Candidates upload their CV. An expert system
evaluates the match with explainable reasoning. An automated email is sent based on the result.

This is the term project for BS CS — AI course. Deadline: 31 May 2026.
Assignment category: HR & Recruitment #1 — Employee Recruitment Advisor.

---

## The Problem It Solves

Every CS student in Pakistan sends 50 job applications and hears nothing back.
They don't know why. Their resume went into a black box.
HireWise opens that black box — it tells candidates exactly why they were rejected
and exactly what to fix, with evidence, reasoning, and a score.

---

## Core Pipeline

```
Company sets rules for a role
        ↓
Candidate browses companies → selects role → uploads CV (PDF)
        ↓
PyMuPDF extracts raw text from PDF
        ↓
spaCy + HuggingFace NER extracts structured facts
(skills, years of experience, education level, projects)
        ↓
PyKnow expert system fires 60+ rules using forward chaining
        ↓
scikit-fuzzy handles partial matches (fuzzy logic)
Certainty factors weight each rule's contribution
        ↓
Score calculated → threshold check (≥90% = pass, <90% = fail)
        ↓
RAG (FAISS + LangChain) retrieves improvement suggestions
Plotly + Matplotlib generate visualizations
ReportLab generates PDF report
        ↓
Gmail API sends automated email:
  - ≥90% → Interview invite email
  - <90% → Rejection email + improvement report PDF attached
```

---

## Features

### Required by teacher (core expert system):
- 60+ meaningful rules derived from O*NET occupational data
- Forward chaining inference via PyKnow
- Explainable reasoning — every conclusion traces to which rule fired and why
- Conflict resolution strategy
- Knowledge acquisition documentation

### Bonus features (all included):
- **Fuzzy logic** — partial skill matching via scikit-fuzzy membership functions
- **Certainty factors** — weighted scoring per rule, aggregate confidence score
- **Hybrid AI** — HuggingFace NER model extracts skills → feeds facts into rule engine
- **NLP input** — spaCy processes raw PDF text into structured facts
- **Ontology integration** — O*NET occupational ontology maps roles → skills → experience levels
- **Explainable visualization** — radar chart, skill gap bar chart, rule firing tree (Plotly)
- **RAG** — FAISS vector store of real job postings, LangChain retrieval for improvement tips
- **Web deployment** — live URL on Render (backend) + Vercel (frontend)
- **Mobile** — Next.js frontend is mobile responsive, PWA installable

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | FastAPI (Python) | Async REST API |
| Frontend | Next.js 14 + Tailwind CSS | Web + mobile UI |
| CV Parsing | PyMuPDF | Extract text from PDF resumes |
| NLP | spaCy | Skill, experience, education extraction |
| NLP Model | HuggingFace `dslim/bert-base-NER` | Named entity recognition for skills |
| Rule Engine | PyKnow | Expert system, forward chaining |
| Fuzzy Logic | scikit-fuzzy | Partial skill and experience matching |
| RAG | FAISS + LangChain | Local vector store, job posting retrieval |
| Ontology | O*NET database | Job roles → required skills mapping |
| Charts | Plotly + Matplotlib | Interactive web charts + PDF charts |
| PDF Report | ReportLab | Generate candidate improvement report |
| Email | Gmail API / SMTP | Automated invite or rejection emails |
| Deployment | Render + Vercel | Free live hosting |

---

## Job Roles Covered (5 roles, ~12 rules each = 60+ total)

1. Software Engineer
2. Data Analyst
3. Web Developer
4. Cybersecurity Analyst
5. Machine Learning Engineer

Rules derived from O*NET data — fully justifiable, not made up.

---

## How the Scoring Works

- Each rule has a certainty factor (weight between 0 and 1)
- Fuzzy logic handles partial matches (e.g. 1yr React when 3yr required = 0.4 match)
- Final score = weighted sum of passed rules / total possible weight
- Threshold: ≥90% → interview invite, <90% → rejection + report
- Every score is traceable — user can see exactly which rules passed, failed, and their weights

---

## Project Folder Structure

```
hirewise/
│
├── CONTEXT.md
├── requirements.txt
├── .env
│
├── backend/
│   ├── main.py           ← FastAPI, all routes
│   ├── cv_parser.py      ← PyMuPDF + spaCy + HuggingFace NER
│   ├── engine.py         ← PyKnow forward chaining
│   ├── rules.py          ← all 60+ rules
│   ├── fuzzy.py          ← scikit-fuzzy partial matching
│   ├── rag.py            ← FAISS + LangChain combined
│   ├── report.py         ← charts + PDF report combined
│   └── mailer.py         ← Gmail API email sender
│
├── frontend/             ← Next.js, AI generated
│
└── data/
    ├── occupations.json  ← O*NET roles → skills
    └── job_postings/     ← 50 .txt files for RAG
└── README.md
```

---

## 7-Day Build Plan

| Day | Date | Focus |
|---|---|---|
| 1 | May 23 | Project setup, FastAPI skeleton, CV parser working |
| 2 | May 24 | PyKnow rule engine, 60 rules, certainty factors |
| 3 | May 25 | Fuzzy logic layer, HuggingFace NER hybrid AI |
| 4 | May 26 | RAG setup, Plotly charts, PDF report generation |
| 5 | May 27 | Next.js frontend, company + candidate portals, email |
| 6 | May 28 | Deploy Render + Vercel, end-to-end testing with real CVs |
| 7 | May 29 | Polish, demo video, documentation. Buffer: May 30-31 |

---

## How to Use This File in a New Chat

Paste the entire contents of this file and say:
**"This is my project context. Read it and then help me with [what you need]."**

Examples:
- "Read this context. Now help me write the PyKnow rules for a Software Engineer role."
- "Read this context. Write the spaCy extraction pipeline for cv_parser.py."
- "Read this context. Build the FAISS indexer for the RAG system."

---

*Project: HireWise | Course: AI | Deadline: 31 May 2026 | Student: BS CS*