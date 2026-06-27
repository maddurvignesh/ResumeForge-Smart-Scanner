# ResumeForge - Smart Resume Screener & ATS Optimizer
View live demo at:https://resume-forge-smart-scanner-9dpb.vercel.app/

ResumeForge is an advanced, modern web application that screens resumes against specific job descriptions, parses details, calculates an ATS match score, audits skills, and offers upskilling recommendations.

It utilizes a dual-engine parser:
1. **AI Engine (Gemini 2.5 Flash)**: Connects to Google Gemini API using the new `google-genai` SDK (v2.10.0) to analyze resume context, layout, formatting, and suggest precise improvements.
2. **Local Engine**: A fully offline, regex-and-heuristic-based parser that identifies contact info, skills, education, and calculates keyword matching scores.

---

## Technical Stack

*   **Backend**: Flask 3.1.1 (Python 3.12+)
*   **Parsing**: `pypdf` 5.6.0, `docx2txt` 0.8
*   **AI Integration**: `google-genai` 2.10.0 SDK — `gemini-2.5-flash` model
*   **Frontend**: Vanilla HTML5, CSS3 (Custom Glassmorphic Theme), and ES6 Javascript

---

## Installation & Setup

1. **Clone or navigate to the directory**:
    ```bash
    d:\New
    ```

2. **Create and Activate Virtual Environment**:
    ```bash
    # Windows
    python -m venv .venv
    .venv\Scripts\activate
    ```

3. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **API Key Setup (Optional)**:
   Copy `.env.example` to `.env` and fill in your Gemini API Key, or configure it directly in the frontend UI.
    ```bash
    copy .env.example .env
    ```

---

## Running the Application

Start the Flask server:
```bash
python app.py
```

The application will be accessible at: **`http://127.0.0.1:5000`**

---

## Visual Aesthetics & Design

The frontend is styled using a premium, custom glassmorphism design:
*   **High-contrast Dark Palette**: Deep dark background (`#08090d`) with glowing indigo, purple, and blue background blobs.
*   **Glass Panels**: Backdrops are styled using blur effects (`backdrop-filter: blur(12px)`) and transparent borders.
*   **Interactive Gauges**: Real-time animated SVG stroke-dashoffset circle showing the ATS score match.
*   **File Dropzone**: Supports file drag-and-drop, showing instant file details, icon changes by file-type, and removal options.
*   **Dynamic Tabs**: Instantly switch between the main Dashboard, detailed Skill Analysis, ATS Action recommendations, extracted information profile, and course recommendations.

---

## About Me

I built ResumeForge to help job seekers turn resume data into actionable feedback with a polished, easy-to-use interface. My work focuses on combining practical recruiting workflows with AI-powered resume parsing and optimization.

As a developer, I enjoy:
*   Building Python and Flask applications that solve real user problems.
*   Designing clean frontend experiences with modern HTML, CSS, and JavaScript.
*   Integrating AI models and parser tooling to make resume review faster, more accurate, and more useful.

This project reflects my passion for improving hiring workflows and helping professionals present their experience clearly to both human readers and ATS systems.
