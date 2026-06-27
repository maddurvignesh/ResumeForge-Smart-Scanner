import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import utilities
from utils.parser import parse_file
from utils.screener import screen_resume

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt', 'md'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB limit

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serves the static index.html from the static directory."""
    return app.send_static_file('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """
    Endpoint to receive a resume file and target job description,
    parse the text, analyze it, and return JSON results.
    """
    # 1. Check if job description is present
    jd_text = request.form.get('job_description', '').strip()
    if not jd_text:
        return jsonify({"error": "Job description is required."}), 400
        
    # 2. Check if resume file is present
    if 'resume' not in request.files:
        return jsonify({"error": "Resume file is required."}), 400
        
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected."}), 400
        
    # 3. Check client-supplied Gemini API key
    client_api_key = request.form.get('api_key', '').strip()
    
    if file and allowed_file(file.filename):
        # Create a unique filename to avoid collision
        original_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{original_ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        try:
            # Save file temporarily
            file.save(filepath)
            
            # Extract text
            resume_text = parse_file(filepath)
            if not resume_text.strip():
                return jsonify({"error": "Uploaded resume could not be parsed or contains no text."}), 400
                
            # Perform screening
            analysis_results = screen_resume(resume_text, jd_text, client_api_key)
            
            # Add metadata details
            analysis_results["filename"] = file.filename
            analysis_results["word_count"] = len(resume_text.split())
            analysis_results["char_count"] = len(resume_text)
            
            return jsonify(analysis_results), 200
            
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 400
        except Exception as e:
            print(f"Error during analysis: {e}")
            return jsonify({"error": f"An unexpected error occurred during analysis: {str(e)}"}), 500
        finally:
            # Clean up the file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception as cleanup_err:
                    print(f"Failed to delete temporary file {filepath}: {cleanup_err}")
    else:
        return jsonify({"error": "Invalid file format. Allowed formats: PDF, DOCX, DOC, TXT, MD"}), 400

@app.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({"error": "File size exceeds the 16MB limit."}), 413

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.getenv("PORT", 5000))
    # Run server
    print(f"Starting Resume Screener server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
