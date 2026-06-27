import os
import re
import json
import urllib.parse
from google import genai
from google.genai import types

# List of common skills for rule-based parsing
COMMON_SKILLS = [
    # Programming Languages
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "sql", "html", "css", "r", "scala", "shell", "bash",
    # Frameworks & Libraries
    "react", "react native", "next.js", "nextjs", "vue", "angular", "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring boot", "laravel", "rails", "jquery", "bootstrap", "tailwind", "pytorch", "tensorflow", "keras", "scikit-learn", "pandas", "numpy", "redux", "graphql",
    # Tools & Technologies
    "git", "github", "docker", "kubernetes", "aws", "azure", "gcp", "google cloud", "firebase", "mongodb", "postgresql", "mysql", "sqlite", "redis", "elasticsearch", "jenkins", "terraform", "ansible", "ci/cd", "linux", "unix", "nginx", "apache", "graphql", "rest api", "apis", "webhooks",
    # Methodologies & Concepts
    "agile", "scrum", "devops", "system design", "microservices", "oop", "functional programming", "data structures", "algorithms", "machine learning", "deep learning", "artificial intelligence", "nlp", "computer vision", "data analysis", "testing", "jest", "cypress", "unittest", "pytest",
    # Soft & Professional Skills
    "project management", "product management", "leadership", "communication", "teamwork", "problem solving", "critical thinking", "ui/ux", "figma", "sketch", "adobe xd"
]

def extract_contact_info(text):
    """
    Extracts email, phone number, and social links using regex.
    """
    contacts = {
        "email": "",
        "phone": "",
        "links": []
    }
    
    # Email regex
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        contacts["email"] = email_match.group(0)
        
    # Phone regex (matches various formats like +1 234 567 8900, 123-456-7890, etc.)
    phone_match = re.search(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    if phone_match:
        contacts["phone"] = phone_match.group(0)
        
    # Links (GitHub, LinkedIn, Portfolio, etc.)
    # 1. Matches with protocols: http:// or https://
    urls_with_protocol = re.findall(r'https?://[^\s()<>|\x00-\x1F]+', text)
    for url in urls_with_protocol:
        cleaned = re.sub(r'[.,;:|]$', '', url).strip()
        if any(domain in cleaned.lower() for domain in ['github.com', 'linkedin.com', 'portfolio', 'behance', 'dribbble', 'medium.com']):
            contacts["links"].append(cleaned)
            
    # 2. Matches common profile domains without protocol: e.g. github.com/username
    no_protocol_pattern = r'(?:\s|^)(?:www\.)?(github\.com|linkedin\.com|behance\.(?:net|com)|dribbble\.com|medium\.com)/[a-zA-Z0-9_\-\.\/]+'
    urls_no_protocol = re.findall(no_protocol_pattern, text, re.IGNORECASE)
    
    # We need to re-find the full matched string because re.findall with a group only returns the group.
    # Let's search with an iterator instead:
    for m in re.finditer(r'(?:^|[\s|])(?:www\.)?((?:github\.com|linkedin\.com|behance\.(?:net|com)|dribbble\.com|medium\.com)/[a-zA-Z0-9_\-\.\/]+)', text, re.IGNORECASE):
        url = m.group(1)
        cleaned = re.sub(r'[.,;:|]$', '', url).strip()
        full_url = "https://" + cleaned
        contacts["links"].append(full_url)
            
    # Remove duplicates from links
    contacts["links"] = list(set(contacts["links"]))
    return contacts

def extract_name(text):
    """
    Attempt to extract candidate name from the top of the resume.
    Often the first few lines of text contain the name.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if not lines:
        return "Unknown Candidate"
    
    # Filter out potential email, phone, web address from the first few lines
    for line in lines[:5]:
        if '@' in line or any(p in line for p in ['+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']) or 'http' in line:
            continue
        # Names are usually 2-3 words
        words = line.split()
        if 1 < len(words) <= 4 and all(w[0].isupper() for w in words if w.isalpha()):
            return line
            
    return lines[0] if lines else "Candidate"

def find_skills(text):
    """
    Find matching skills from the COMMON_SKILLS dictionary.
    """
    found_skills = []
    text_lower = text.lower()
    
    # Word boundary checks to avoid partial matches (e.g. "go" in "good")
    for skill in COMMON_SKILLS:
        if len(skill) <= 3:
            # Short skills (go, git, r, sql) need strict boundaries
            pattern = r'\b' + re.escape(skill) + r'\b'
        else:
            pattern = re.escape(skill)
            
        if re.search(pattern, text_lower):
            found_skills.append(skill)
            
    return sorted(list(set(found_skills)))

def parse_structure(text):
    """
    Looks for standard section headings to verify resume structure.
    """
    headings = {
        "education": ["education", "academic", "university", "college", "degree", "qualification"],
        "experience": ["experience", "employment", "work history", "professional history", "work", "history"],
        "projects": ["projects", "personal projects", "academic projects", "open source"],
        "skills": ["skills", "technical skills", "technologies", "expertise", "core competencies"]
    }
    
    sections_found = {}
    text_lower = text.lower()
    
    for section, keywords in headings.items():
        found = False
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                found = True
                break
        sections_found[section] = found
        
    return sections_found

def run_local_screening(resume_text, jd_text):
    """
    Performs standard rule-based parsing and similarity checks.
    """
    contacts = extract_contact_info(resume_text)
    name = extract_name(resume_text)
    
    resume_skills = find_skills(resume_text)
    jd_skills = find_skills(jd_text)
    
    # If no skills identified in JD, parse all unique words/phrases as potential comparison
    if not jd_skills:
        # Fallback to Jaccard check on filtered words if no common skills found
        jd_skills = [w for w in re.findall(r'\b\w{4,}\b', jd_text.lower()) if w in COMMON_SKILLS]
        
    # Match skills
    matched_skills = [s for s in jd_skills if s in resume_skills]
    missing_skills = [s for s in jd_skills if s not in resume_skills]
    
    # Check structure
    sections = parse_structure(resume_text)
    
    # ATS Scoring Logic
    # 50% skill match (ratio of matched skills to target JD skills)
    # 30% completeness (contact details, sections present)
    # 20% structure (formatting, experience/education details)
    
    skill_score = 0
    if jd_skills:
        skill_score = (len(matched_skills) / len(jd_skills)) * 50
    else:
        # If JD has no identifiable skills, give default base score for skills
        skill_score = 40
        
    completeness_score = 0
    if contacts["email"]: completeness_score += 10
    if contacts["phone"]: completeness_score += 10
    if contacts["links"]: completeness_score += 10
    
    structure_score = 0
    for sec, found in sections.items():
        if found:
            structure_score += 5 # Max 20 for 4 sections
            
    # Add bonus for links presence
    total_score = round(skill_score + completeness_score + structure_score)
    total_score = min(max(total_score, 10), 99) # Cap between 10% and 99%
    
    # Generate structured recommendations
    recommendations = []
    
    # 1. Structural Checks
    if not contacts["email"] or not contacts["phone"]:
        recommendations.append({
            "category": "Contact Information",
            "priority": "High",
            "finding": "Missing contact details.",
            "recommendation": "Ensure your professional email and phone number are clearly visible at the top of your resume.",
            "example": "Email: jane.doe@example.com | Phone: +1-555-0199"
        })
        
    if not sections["experience"]:
        recommendations.append({
            "category": "Structure",
            "priority": "High",
            "finding": "No clear 'Experience' section found.",
            "recommendation": "Add a dedicated 'Experience' or 'Employment History' section detailing your professional work. Use reverse chronological order.",
            "example": "WORK EXPERIENCE\nSoftware Engineer | ACME Corp (2022 - Present)\n- Developed microservices..."
        })
        
    if not sections["education"]:
        recommendations.append({
            "category": "Structure",
            "priority": "Medium",
            "finding": "No clear 'Education' section found.",
            "recommendation": "Include a section for your academic degrees, certifications, or self-taught courses.",
            "example": "EDUCATION\nB.S. in Computer Science | University of Technology (Graduated 2021)"
        })
        
    # 2. Skill Match Checks
    if missing_skills:
        top_missing = missing_skills[:5]
        recommendations.append({
            "category": "Keywords & Skills",
            "priority": "High",
            "finding": f"Missing critical job requirements: {', '.join(top_missing)}",
            "recommendation": f"Add the following skills to your Skills section if you have experience with them: {', '.join(top_missing)}.",
            "example": f"SKILLS: {', '.join(top_missing)}, ..."
        })
        
    # 3. Formatting & Bullet Checks (Heuristics)
    bullet_count = resume_text.count('•') + resume_text.count('- ') + resume_text.count('* ')
    if bullet_count < 5:
        recommendations.append({
            "category": "Formatting",
            "priority": "Medium",
            "finding": "Low number of bullet points detected.",
            "recommendation": "Use bullet points rather than dense paragraphs to describe your achievements. This helps ATS parsers and human recruiters scan your resume.",
            "example": "- Optimized database queries, reducing API latency by 35%."
        })
        
    # 4. Quantitative Metrics Checks
    metrics_matches = len(re.findall(r'\b(?:\d+%\b|\$\d+|\d+\+)', resume_text))
    if metrics_matches < 3:
        recommendations.append({
            "category": "Quantitative Metrics",
            "priority": "Medium",
            "finding": "Few quantitative achievements detected.",
            "recommendation": "Quantify your impact using metrics (percentages, dollar amounts, hours saved) to prove your accomplishments.",
            "example": "Before: 'Improved app performance.'\nAfter: 'Improved application load times by 40% using Redis caching.'"
        })
        
    # 5. Course Recommendations
    courses = []
    for skill in missing_skills[:4]:
        skill_encoded = urllib.parse.quote_plus(skill)
        courses.append({
            "skill": skill.capitalize(),
            "course_name": f"Mastering {skill.capitalize()} & Advanced Concepts",
            "platform": "Udemy / Coursera",
            "url": f"https://www.coursera.org/courses?query={skill_encoded}"
        })
        
    # If no missing skills, add some default courses
    if not courses:
        courses = [
            {"skill": "System Design", "course_name": "Software Engineering System Design", "platform": "Educative", "url": "https://www.educative.io"},
            {"skill": "Cloud Basics", "course_name": "AWS Certified Cloud Practitioner", "platform": "Coursera", "url": "https://www.coursera.org"}
        ]
        
    # Structural details for dashboard
    education_extracted = []
    experience_extracted = []
    
    # Mock some structures based on regex splits for displaying in UI
    edu_matches = re.findall(r'(?:B\.?S\.?|M\.?S\.?|B\.?E\.?|B\.?Tech|Bachelor|Master|University|College)[^\n]+', resume_text, re.IGNORECASE)
    for match in edu_matches[:3]:
        education_extracted.append({
            "institution": "University/Institution",
            "degree": match.strip()[:60],
            "duration": "Duration (Detected)"
        })
        
    if not education_extracted:
        education_extracted = [{"institution": "Not clearly parsed locally", "degree": "Please check your resume layout", "duration": "N/A"}]
        
    exp_matches = re.findall(r'(?:Software Engineer|Developer|Analyst|Manager|Intern|Architect)[^\n]+', resume_text, re.IGNORECASE)
    for match in exp_matches[:3]:
        experience_extracted.append({
            "company": "Company Name",
            "role": match.strip()[:60],
            "duration": "Duration (Detected)",
            "description": "Details parsed from text."
        })
        
    if not experience_extracted:
        experience_extracted = [{"company": "Not clearly parsed locally", "role": "Please check your resume layout", "duration": "N/A", "description": ""}]
        
    return {
        "engine": "local_fallback",
        "candidate_name": name,
        "email": contacts["email"] or "Not found",
        "phone": contacts["phone"] or "Not found",
        "links": contacts["links"],
        "education": education_extracted,
        "experience": experience_extracted,
        "skills_matched": matched_skills,
        "skills_missing": missing_skills,
        "ats_score": total_score,
        "ats_recommendations": recommendations,
        "course_recommendations": courses
    }

def run_gemini_screening(resume_text, jd_text, api_key):
    """
    Runs high-fidelity screening using Gemini AI (gemini-2.5-flash) with structured JSON schema.
    Uses the new google-genai SDK (v2+).
    """
    try:
        # Initialize new-style client
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are an expert ATS (Applicant Tracking System) parser and professional recruiter.
Analyze the following Resume against the target Job Description (JD).

Return a strictly valid JSON object matching the following schema. Do not output markdown, preambles, backticks, or any trailing text. Output ONLY the JSON block.

JSON Schema:
{{
  "candidate_name": "Full name of the candidate, if found, else 'Unknown'",
  "email": "Email address, if found, else 'Not found'",
  "phone": "Phone number, if found, else 'Not found'",
  "links": ["List of links like GitHub, LinkedIn, portfolios found in the resume"],
  "education": [
    {{
      "institution": "University/Institution name",
      "degree": "Degree name & major",
      "duration": "Graduation year or date range"
    }}
  ],
  "experience": [
    {{
      "company": "Company name",
      "role": "Job title/role",
      "duration": "Employment duration/dates",
      "description": "Short summary of responsibilities"
    }}
  ],
  "skills_matched": ["List of skills found in BOTH the resume and the job description. Extract actual skills and tools, keep them short."],
  "skills_missing": ["List of critical skills/requirements listed in the Job Description but NOT found in the resume. Extract actual skills, tools, methodologies."],
  "ats_score": <An integer score between 0 and 100 representing the match quality based on skills overlap (50%), formatting (20%), quantitative metrics (20%), and contact info (10%)>,
  "ats_recommendations": [
    {{
      "category": "Category name (e.g. Keywords, Formatting, Quantitative Impact, Structure)",
      "priority": "High or Medium or Low",
      "finding": "Short statement of the issue or gap identified",
      "recommendation": "Actionable, specific guidance on how to fix this inside the resume text",
      "example": "Before/After code block or rewrite recommendation"
    }}
  ],
  "course_recommendations": [
    {{
      "skill": "Name of the missing skill",
      "course_name": "Suggested online course title",
      "platform": "Suggest Coursera or Udemy or edX",
      "url": "Search URL on Coursera or edX for that skill"
    }}
  ]
}}

---
JOB DESCRIPTION:
{jd_text}

---
RESUME TEXT:
{resume_text}
"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # Parse the JSON response
        result_text = response.text.strip()
        data = json.loads(result_text)
        data["engine"] = "gemini_2.5_flash"
        
        return data
        
    except Exception as e:
        print(f"Gemini API execution error: {e}. Falling back to local screening.")
        # Fall back to local screening if the API fails
        fallback_data = run_local_screening(resume_text, jd_text)
        fallback_data["api_error"] = str(e)
        return fallback_data

def screen_resume(resume_text, jd_text, client_api_key=None):
    """
    Main entry point for screening resumes. Checks environment or client keys.
    """
    api_key = client_api_key or os.getenv("GEMINI_API_KEY")
    if api_key and api_key.strip() and not api_key.startswith("your_gemini_api_key"):
        return run_gemini_screening(resume_text, jd_text, api_key)
    else:
        return run_local_screening(resume_text, jd_text)
