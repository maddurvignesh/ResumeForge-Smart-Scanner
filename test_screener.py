import sys
from utils.screener import screen_resume

def main():
    print("--- Running Local Screener Validation Test ---")
    
    # Mock Resume
    resume_text = """
    Jane Doe
    jane.doe@example.com | (123) 456-7890 | github.com/janedoe | linkedin.com/in/janedoe
    
    Professional Experience:
    Software Engineer - ACME Corp (2022 - Present)
    - Built responsive web pages using React and Tailwind CSS.
    - Designed and implemented microservices using Python and Flask.
    - Automated tests using pytest.
    
    Education:
    Bachelor of Science in Computer Science - Tech University (2018-2022)
    
    Skills:
    Python, JavaScript, React, Flask, Git, Docker, HTML, CSS
    """
    
    # Mock Job Description
    jd_text = """
    We are looking for a Software Engineer to join our team. 
    Requirements:
    - 2+ years of experience with Python, Django, or Flask.
    - Strong skills in JavaScript and React.
    - Experience with Docker, Kubernetes, and AWS is a plus.
    - Good communication and teamwork skills.
    """
    
    # Run screening in local fallback mode (no API key)
    results = screen_resume(resume_text, jd_text)
    
    print("\n--- RESULTS ---")
    print(f"Candidate Name: {results.get('candidate_name')}")
    print(f"Email: {results.get('email')}")
    print(f"Phone: {results.get('phone')}")
    print(f"Social Links: {results.get('links')}")
    print(f"ATS Match Score: {results.get('ats_score')}%")
    print(f"Matched Skills: {results.get('skills_matched')}")
    print(f"Missing Skills: {results.get('skills_missing')}")
    
    print("\n--- RECOMMENDATIONS ---")
    for rec in results.get('ats_recommendations', []):
        print(f"[{rec['category']} - {rec['priority']} Priority] {rec['finding']}")
        print(f"  Rec: {rec['recommendation']}")
        print(f"  Ex: {rec['example']}")
        print()
        
    print("--- COURSE SUGGESTIONS ---")
    for course in results.get('course_recommendations', []):
        print(f"  - [{course['platform']}] {course['course_name']} (Skill: {course['skill']})")
        
    # Check assertions
    assert results.get("candidate_name") == "Jane Doe", "Name extraction failed"
    assert results.get("email") == "jane.doe@example.com", "Email extraction failed"
    assert results.get("phone") == "(123) 456-7890", "Phone extraction failed"
    assert "https://github.com/janedoe" in results.get("links"), "GitHub link extraction failed"
    assert "python" in results.get("skills_matched"), "Python matching failed"
    assert "react" in results.get("skills_matched"), "React matching failed"
    assert "kubernetes" in results.get("skills_missing"), "Kubernetes missing check failed"
    assert "aws" in results.get("skills_missing"), "AWS missing check failed"
    
    print("\nALL LOCAL PARSER TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    main()
