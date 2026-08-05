"""
NutriMatch 맞춤 진단 페이지 (01_Custom_Care.py)
"""

import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="NutriMatch | 개인 맞춤형 영양 체크",
    page_icon="🌱",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    * {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif !important;
    }

    .block-container { 
        padding: 0.75rem 2rem 1.5rem 2rem !important; 
        max-width: 100% !important; 
        margin: 0 auto !important;
    }
    header { display: none !important; }
    footer { display: none !important; }
    .stApp { background-color: #FAF9F6 !important; }
    iframe { border: none !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)

html_path = os.path.join(os.path.dirname(__file__), "..", "..", "html_app", "index.html")
if not os.path.exists(html_path):
    html_path = os.path.join(os.path.dirname(__file__), "..", "html_app", "index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        html_data = f.read()
    components.html(html_data, height=1550, scrolling=False)
else:
    st.error("HTML 대시보드 파일(html_app/index.html)을 찾을 수 없습니다.")