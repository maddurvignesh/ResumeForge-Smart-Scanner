import os
from pypdf import PdfReader
import docx2txt

def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file using pypdf.
    """
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error parsing PDF file {file_path}: {e}")
        raise ValueError(f"Could not parse PDF: {str(e)}")
    return text

def extract_text_from_docx(file_path):
    """
    Extracts text from a DOCX file using docx2txt.
    """
    try:
        text = docx2txt.process(file_path)
        return text
    except Exception as e:
        print(f"Error parsing DOCX file {file_path}: {e}")
        # Secondary fallback using basic zip/xml if docx2txt fails
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            with zipfile.ZipFile(file_path) as docx:
                xml_content = docx.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                text_parts = []
                for node in tree.iter():
                    if node.tag.endswith('t'):
                        text_parts.append(node.text or '')
                return ' '.join(text_parts)
        except Exception as e_inner:
            raise ValueError(f"Could not parse DOCX: {str(e_inner)}")

def extract_text_from_txt(file_path):
    """
    Extracts text from a plain text file. Try multiple encodings.
    """
    encodings = ['utf-8', 'latin-1', 'utf-16']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not parse TXT file: Unsupported encoding.")

def parse_file(file_path):
    """
    Main entry point to parse various document types.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file_path)
    elif ext in ['.txt', '.md']:
        return extract_text_from_txt(file_path)
    else:
        # Try reading it as text as a last resort
        try:
            return extract_text_from_txt(file_path)
        except Exception:
            raise ValueError(f"Unsupported file format: {ext}")
