import os
import json
import magic
import fitz
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import spacy
from docx import Document
from pdf2image import convert_from_path
from sentence_transformers import SentenceTransformer,util
import pdfplumber
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()




def take_inputs():
    resume_path = input("enter the file path")
    if resume_path.startswith('"'):
        resume_path = resume_path.removeprefix('"')
    if resume_path.endswith('"'):
        resume_path = resume_path.removesuffix('"')


    jd_path = input("Enter the JD path")
    if jd_path.startswith('"'):
        jd_path = jd_path.removeprefix('"')
    if jd_path.endswith('"'):
        jd_path = jd_path.removesuffix('"')

    return resume_path , jd_path





def is_scanned_pdf(path):
    doc = fitz.open(path)
    for page in doc:
        text = page.get_text()
        if text.strip():
            return False
    return True




def extract_text_from_resume(file_path):
    if os.path.exists(file_path):
        file_type = magic.from_file(file_path, mime=True)
        if file_type == 'application/pdf':
            if is_scanned_pdf(file_path):
                images = convert_from_path(file_path)
                return "\n".join(pytesseract.image_to_string(img) for img in images)

            with pdfplumber.open(file_path) as pdf:
                resume_text = ""
                for page in pdf.pages:
                    resume_text += page.extract_text() + "\n"
                return resume_text
            
        if file_type == 'image/png':
            resume_text =  pytesseract.image_to_string(Image.open(file_path))
            return resume_text
        
        if file_type =='application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])





def extract_text_from_jd(jd_path):
    if os.path.exists(jd_path):
        jd_text = ""
        with pdfplumber.open(jd_path) as pdf:
            for page in pdf.pages:
                jd_text += page.extract_text() +"\n"
            return jd_text



api_key = os.getenv("GOOGLE_API_KEY")
llm = ChatGoogleGenerativeAI(
    model= "models/gemini-2.0-flash",
    google_api_key=api_key
)




def parse_resume(resume_text):
    prompt = f"""
        You are an expert resume reviewer.

        Analyze the following resume text:

        {resume_text}

        Please provide your analysis in strict JSON format with these keys:

        {{
        "strengths": [list of strengths found in the resume],
        "weaknesses": [list of weaknesses or missing info],
        "missing_sections": [list of important resume sections missing],
        "wording_suggestions": [list of suggestions to improve wording or phrasing]
        }}

        Answer ONLY with valid JSON — no extra explanation or text.
        Each list should contain concise bullet points or phrases.

    """

    response = llm.invoke(prompt)
    section_content = response.content.strip()

    if section_content.startswith("```json"):
        section_content = section_content.removeprefix("```json").strip()
    if section_content.endswith("```"):
        section_content = section_content.removesuffix("```").strip()

    try:
        print(json.loads(section_content))
        return json.loads(section_content)

    except json.JSONDecodeError:
        print("Error: LLM returned invalid JSON.")
        return None






def ATS_Score(resume_content , jd_content):
    #model3 = SentenceTransformer('all-mpnet-base-v2')
    model1 = SentenceTransformer('sentence-transformers/msmarco-distilbert-base-tas-b')  # or 'cuda' if you're using GPU
    model2 = SentenceTransformer('all-MiniLM-L6-v2')  # or 'cuda' if you're using GPU


    #score3 = util.cos_sim(model1.encode(resume_content), model1.encode(jd_content))
    score1 = util.cos_sim(model1.encode(resume_content), model1.encode(jd_content))
    score2 = util.cos_sim(model2.encode(resume_content), model2.encode(jd_content))
    score1 , score2 = str(score1.item()) , str(score2.item())
    final_score = round(((float(score1)*0.35) + (float(score2)*0.65))*100, 2)
    return final_score


def create_resume(resume_text):
    prompt = f''' 
        You are a professional resume editor and web designer.

        I will provide raw extracted plain text from a resume.

        Your task is to:

        1. Identify and organize the content into clear, standard resume sections (Header, Summary, Education, Experience, Skills, Projects, etc.).
        2. Improve the wording throughout the resume — fix weaknesses, replace weak phrases with stronger, action-oriented language, and polish the text for maximum impact.
        3. Generate a visually attractive, modern, and clean HTML resume. Use appropriate semantic tags, and style it inline or with embedded CSS to look professional and elegant (clean fonts, spacing, headings, bullet points, and subtle colors).
        4. Ensure the resume is still ATS-friendly by keeping structure logical and simple.
        5. Output the complete HTML code only, ready to be displayed in a browser.
        6. Make it extremely attractive with beautiful formating and colours and beautifull backgrounds also background shapes.
        7. If applicable also build two way resume like with two coloumn on same page with different sections

        Here is the raw resume text:

        {resume_text}

        Create the improved, styled resume HTML now
        return only direct html do not start with``` html or ``` nothing direct HTML return
        '''
    
    response = llm.invoke(prompt)
    gen_resume = response.content.strip()
    if gen_resume.startswith("```html"):
        gen_resume = gen_resume.removeprefix("```html")
    if gen_resume.endswith("```"):
        gen_resume = gen_resume.removesuffix("```")
    print(gen_resume)
    return gen_resume
