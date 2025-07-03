import streamlit as st
import PyPDF2
import io
import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit page setup
st.set_page_config(page_title="AI Resume Critiquer", page_icon="📃", layout="centered")

# Title & Subtitle
st.title("📃 AI Resume Critiquer")
st.markdown(
    "<h5 style='color: gray;'>Upload your resume and get AI-powered feedback tailored to your job goals!</h5>",
    unsafe_allow_html=True
)

# Get API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# File uploader and role input
with st.container():
    st.subheader(" Upload Your Resume")
    uploaded_file = st.file_uploader("Accepted formats: PDF or TXT", type=["pdf", "txt"])

    st.subheader("Target Role (optional)")
    job_role = st.text_input("Enter the job role you're targeting")

analyze = st.button("Analyze Resume")

# PDF Text Extractor
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text

# General Text Extractor
def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

# Resume Analysis
if analyze and uploaded_file:
    try:
        with st.spinner("Analyzing your resume... please wait..."):
            file_content = extract_text_from_file(uploaded_file)

            if not file_content.strip():
                st.error(" The uploaded file appears to be empty.")
                st.stop()

            prompt = f"""Please analyze this resume and provide constructive feedback. 
Focus on the following aspects:
1. Content clarity and impact
2. Skills presentation
3. Experience descriptions
4. Specific improvements for {job_role if job_role else 'general job applications'}

resume_content:
{file_content}

Please provide your analysis in a clear, structured format with specific recommendations."""

            # Call Groq
            client = Groq(api_key=GROQ_API_KEY)
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume reviewer with years of experience in HR and recruitment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
            )

        # Display Result
        st.success(" Resume analysis complete!")
        st.markdown("###  AI Feedback")
        st.markdown(response.choices[0].message.content)

    except Exception as e:
        st.error(f" An error occurred: {str(e)}")