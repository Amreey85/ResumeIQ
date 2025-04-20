# main.py
import streamlit as st
import PyPDF2
import docx
import re
import pandas as pd
from google.generativeai import GenerativeModel, configure
from io import BytesIO
import base64

# ======================================
# UI Configuration & Custom CSS
# ======================================
def set_custom_theme():
    st.set_page_config(
        page_title="ResumeIQ Pro",
        page_icon="📋",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown(f"""
    <style>
    /* Main container */
    .stApp {{
        background-color: #1a1a1a;
        color: #ffffff;
    }}
    
    /* Sidebar */
    .css-1d391kg {{
        background-color: #262626 !important;
        border-right: 1px solid #404040;
    }}
    
    /* Input fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #4d4d4d;
        border-radius: 8px;
    }}
    
    /* File uploader */
    .st-emotion-cache-13ln4jf {{
        background-color: #333333;
        border: 2px dashed #4d4d4d;
        border-radius: 12px;
        padding: 2rem;
    }}
    
    /* Dataframe styling */
    .dataframe {{
        background-color: #262626 !important;
        color: #ffffff !important;
    }}
    
    /* Buttons */
    .stButton>button {{
        background-color: #4CAF50 !important;
        color: white !important;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
    }}
    
    .stButton>button:hover {{
        background-color: #45a049 !important;
        transform: scale(1.05);
    }}
    
    /* Progress bars */
    .st-emotion-cache-1m7p7ct {{
        background-color: #404040 !important;
    }}
    
    .st-emotion-cache-ztfqz8 {{
        background-color: #4CAF50 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

set_custom_theme()

# ======================================
# Core Functions
# ======================================
def parse_resume(file):
    """Extract text from PDF/DOCX files with error handling"""
    try:
        if file.type == "application/pdf":
            pdf_reader = PyPDF2.PdfReader(BytesIO(file.getvalue()))
            return "\n".join([page.extract_text() for page in pdf_reader.pages])
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(BytesIO(file.getvalue()))
            return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        st.error(f"Error parsing {file.name}: {str(e)}")
        return ""

def calculate_match_score(text, keywords):
    """Calculate keyword match percentage with normalization"""
    text = re.sub(r'\s+', ' ', text).lower()
    keywords = [k.strip().lower() for k in keywords.split(",") if k.strip()]
    
    if not keywords:
        return 0
    
    matches = sum(1 for keyword in keywords if re.search(rf'\b{re.escape(keyword)}\b', text))
    return min(round((matches / len(keywords)) * 100, 1), 100)

# ======================================
# AI Integration
# ======================================
def generate_ai_analysis(text, api_key, provider="Gemini"):
    """Generate professional summary with error handling"""
    try:
        if not api_key:
            return "⚠️ Please enter a valid API key"
            
        if provider == "Gemini":
            # Existing Gemini code
            configure(api_key=api_key)
            model = GenerativeModel('gemini-pro')
            response = model.generate_content(f"Analyze resume: {text[:3000]}")
            return response.text
            
        elif provider == "DeepSeek-R1":
            openai.api_base = "https://openrouter.ai/api/v1"
            openai.api_key = api_key
            
            response = openai.ChatCompletion.create(
                model="deepseek/deepseek-r1",
                messages=[{
                    "role": "user",
                    "content": f"""Analyze this resume and provide a structured summary:
                    1. Key technical skills
                    2. Work experience highlights
                    3. Education background
                    4. Notable achievements
                    Resume Content: {text[:3000]}"""
                }],
                headers={
                    "HTTP-Referer": "http://localhost:8501",  # For local testing
                    "X-Title": "ResumeIQ Pro"
                }
            )
            return response.choices[0].message.content
            
    except Exception as e:
        return f"❌ AI Error: {str(e)}"

# Update the sidebar provider selection
with st.sidebar:
    st.header("⚙️ Configuration")
    api_provider = st.selectbox("AI Provider", ["Gemini", "DeepSeek-R1"])  # Updated
    api_key = st.text_input("🔑 OpenRouter API Key", type="password")
    # Rest of your existing sidebar code...

import time
time.sleep(6)  # Add 6-second delay between requests

# ======================================
# Main Application
# ======================================
def main():
    st.title("📋 ResumeIQ Pro")
    st.caption("Professional Resume Analysis Platform")
    
    # ========= Sidebar Controls =========
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_provider = st.selectbox("AI Provider", ["Gemini", "Deepseek"])
        api_key = st.text_input("🔑 API Key", type="password")
        keywords = st.text_input("🔍 Keywords (comma-separated)", placeholder="python, machine learning, project management")
        max_files = st.slider("📁 Max Resumes", 1, 20, 10)
    
    # ========= File Upload Section =========
    with st.container():
        st.header("📤 Upload Resumes")
        uploaded_files = st.file_uploader(
            "Drag & drop resumes (PDF/DOCX)",
            type=["pdf", "docx"],
            accept_multiple_files=True,
            help="Max 20 files | Supported formats: PDF, DOCX"
        )
    
    if uploaded_files:
        # ========= Processing Section =========
        if len(uploaded_files) > max_files:
            st.warning(f"⚠️ Maximum {max_files} files allowed")
            st.stop()
            
        with st.status("📊 Analyzing resumes...", expanded=True) as status:
            resumes = []
            progress_bar = st.progress(0)
            
            for i, file in enumerate(uploaded_files):
                text = parse_resume(file)
                score = calculate_match_score(text, keywords)
                resumes.append({
                    "File": file.name,
                    "Content": text,
                    "Score": score
                })
                progress_bar.progress((i+1)/len(uploaded_files))
                
            df = pd.DataFrame(resumes).sort_values("Score", ascending=False)
            status.update(label="✅ Analysis Complete", state="complete")
        
        # ========= Results Display =========
        st.header("📈 Results Overview")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.dataframe(
                df[["File", "Score"]],
                use_container_width=True,
                column_config={
                    "Score": st.column_config.ProgressColumn(
                        "Match Score",
                        help="Keyword match percentage",
                        format="%d%%",
                        min_value=0,
                        max_value=100
                    )
                }
            )
        
        with col2:
            st.metric("Total Resumes", len(df))
            st.metric("Average Score", f"{df['Score'].mean():.1f}%")
            st.download_button(
                "💾 Export Results",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="resume_analysis.csv",
                mime="text/csv"
            )
        
        # ========= AI Analysis Section =========
        st.divider()
        st.header("🤖 AI-Powered Analysis")
        
        selected_file = st.selectbox("Select a resume for detailed analysis", df["File"])
        
        if st.button("🔍 Generate Full Analysis"):
            if not api_key:
                st.error("Please enter an API key in the sidebar")
                return
                
            selected = next(r for r in resumes if r["File"] == selected_file)
            
            with st.spinner("🧠 Analyzing with AI..."):
                analysis = generate_ai_analysis(selected["Content"], api_key, api_provider)
                
                st.subheader("Professional Summary")
                st.success(analysis)
                
                # Additional analysis sections can be added here

if __name__ == "__main__":
    main()