# HireWise — AI-Powered Recruitment System

HireWise is a two-sided AI recruitment platform built as a BS CS term project. Companies post job roles with custom evaluation criteria, candidates upload their CVs, and an AI pipeline evaluates them using an expert system, fuzzy logic, and RAG-based improvement tips. Results are delivered instantly via email with a detailed PDF report.

---

## What It Does

**For Companies**
- Post job roles with a custom pass threshold (50%–95%)
- Toggle individual skill requirements on or off before posting
- Receive an email notification every time a candidate passes your threshold
- Manage and remove active job listings from a dashboard

**For Candidates**
- Select a role and browse companies currently hiring for it
- Upload a CV in PDF format
- Receive an instant AI evaluation with an explainable score
- Get a detailed PDF report with a rule-by-rule breakdown and personalised improvement tips
- Receive the result via email — interview invitation if passed, improvement report if not

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python 3.13) |
| CV Parsing | Google Gemini 2.5 Flash API |
| Expert System | experta (PyKnow) — 60 rules across 5 roles |
| Fuzzy Scoring | scikit-fuzzy — trapezoidal membership functions |
| RAG Tips | Keyword-based retrieval from a curated tip database |
| PDF Reports | ReportLab + Plotly |
| Email | Gmail SMTP with App Password |
| Company Storage | JSON file (companies.json) |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |

---

## Project Structure

```
HireWise/
├── backend/
│   ├── main.py          # FastAPI app, all API routes
│   ├── cv_parser.py     # Gemini-powered CV extraction with rule-based fallback
│   ├── engine.py        # PyKnow expert system engine
│   ├── rules.py         # 60 weighted rules across 5 roles
│   ├── fuzzy.py         # scikit-fuzzy scoring (blended 60/40 with hard score)
│   ├── rag.py           # Keyword-matched improvement tips
│   ├── report.py        # ReportLab PDF generation with Plotly charts
│   ├── mailer.py        # Gmail SMTP email sender
│   ├── companies.json   # Persistent company storage
│   └── reports/         # Generated PDF reports (auto-created)
├── frontend/
│   └── src/app/
│       ├── page.tsx          # Landing page
│       ├── apply/page.tsx    # Candidate application flow
│       ├── company/page.tsx  # Company dashboard
│       └── results/page.tsx  # Evaluation results
├── data/
│   └── occupation.json  # Role definitions reference
└── .env                 # API keys and configuration (not committed)
```

---

## Supported Roles

Each role has 12 weighted evaluation rules.

| Role | Key Requirements |
|---|---|
| Software Engineer | Python, Java, SQL, Git, Docker, REST API, Linux, Cloud |
| Data Analyst | SQL, Python, Pandas, Statistics, Excel, Visualization |
| Web Developer | HTML, CSS, JavaScript, React, Node.js, TypeScript |
| Cybersecurity Analyst | Network Security, Linux, Pen Testing, OWASP, SIEM |
| Machine Learning Engineer | Python, scikit-learn, PyTorch/TF, NumPy, NLP, MLOps |

---

## How the Scoring Works

1. **CV Parsing** — Gemini 2.5 Flash extracts skills, education, experience, projects, and certifications from the PDF. A rule-based system acts as fallback if Gemini is unavailable.

2. **Expert System** — PyKnow evaluates 12 weighted rules for the selected role. Companies can disable specific rules before posting. The engine computes a raw weighted score.

3. **Fuzzy Scoring** — scikit-fuzzy applies trapezoidal membership functions to experience, skill count, project count, and education level, producing a partial score for near-misses. The final score is a 60/40 blend of the hard rule score and the fuzzy partial score.

4. **Pass Decision** — The final score is compared against the company's custom threshold (default 75%). Pass → interview invitation. Fail → rejection with improvement tips.

5. **RAG Tips** — Failed rules are mapped to keywords. Tips from a role-specific and global database are ranked by keyword match and the top 5 are returned.

6. **PDF Report** — ReportLab generates a report with a Plotly score gauge, horizontal bar chart of all rules, passed/failed rule tables, improvement tips, and a CV summary.

7. **Email** — Candidate receives a styled HTML email. If they passed, the company also receives a notification with the candidate's details.

---

## Prerequisites

- Python 3.13
- Node.js 18+
- A Google Gemini API key (free tier works)
- A Gmail account with an App Password

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/hirewise.git
cd hirewise
```

### 2. Backend setup

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

pip install fastapi uvicorn python-dotenv pdfplumber httpx
pip install experta scikit-fuzzy numpy pandas
pip install reportlab plotly kaleido
pip install python-multipart
```

### 3. Create the `.env` file

Create `backend/.env` with the following:

```
GEMINI_API_KEY=your_gemini_api_key_here
GMAIL_USER=youremail@gmail.com
GMAIL_APP_PASSWORD=your16charapppassword
```

**Getting a Gemini API key:** Go to [aistudio.google.com](https://aistudio.google.com) → Get API Key → Free tier is sufficient.

**Getting a Gmail App Password:**
1. Enable 2-Step Verification on your Google account
2. Go to `myaccount.google.com` → Security → App Passwords
3. Type any name (e.g. HireWise) → Click Create
4. Copy the 16-character password — paste it without spaces

### 4. Run the backend

```powershell
cd backend
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`. API docs available at `http://localhost:8000/docs`.

### 5. Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:3000`. 

---

## Usage

### As a Company

1. Go to `http://localhost:3000/company`
2. Fill in company name, contact email, select a role
3. Set your pass threshold using the slider
4. Toggle off any skill requirements your role does not need
5. Click **Post Role**
6. Switch to the **Manage** tab to view or remove your listings

### As a Candidate

1. Go to `http://localhost:3000/apply`
2. Select your target role
3. Browse companies currently hiring, or evaluate independently
4. Upload your CV (PDF only)
5. Enter your email address and click **Run Evaluation**
6. View your results instantly on screen, and check your email for the full report

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/companies/create` | Register a company and post a role |
| GET | `/companies` | List all active companies |
| GET | `/companies/role/{role}` | Companies hiring for a specific role |
| GET | `/companies/rules/{role}` | Available rule keys for a role |
| DELETE | `/companies/{id}` | Remove a job posting |
| POST | `/apply` | Submit CV for evaluation |
| POST | `/parse-cv` | Debug endpoint — returns raw CV extraction |

---

## Note on Running

This project requires a valid Gemini API key and Gmail App Password to function fully. Without the Gemini key, CV parsing falls back to a rule-based system which may be less accurate for complex CVs. Without Gmail credentials, emails are skipped but all other functionality (scoring, PDF, results page) continues to work.

---

## Author

Muhammad Saad
