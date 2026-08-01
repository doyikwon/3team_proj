"""
NutriMatch 맞춤 진단 페이지 (01_Custom_Care.py)
역할: html_app/index.html의 모든 기능(동의 게이트, 설문, 계단식 적합도 %)을 전체 화면으로 렌더링
"""

import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="NutriMatch | 개인 맞춤형 영양 체크",
    page_icon="🌱",
    layout="wide"
)

# Streamlit 기본 패딩 제거 및 스타일 적용
st.markdown("""
<style>
    .block-container { 
        padding: 0 !important; 
        max-width: 100% !important; 
        margin: 0 !important;
    }
    header { display: none !important; }
    footer { display: none !important; }
    .stApp { background-color: #FAF9F6; }
    iframe { border: none !important; width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# html_app/index.html 읽기
html_path = os.path.join(os.path.dirname(__file__), "..", "..", "html_app", "index.html")
if not os.path.exists(html_path):
    # 경로 보정
    html_path = os.path.join(os.path.dirname(__file__), "..", "html_app", "index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        html_data = f.read()
    components.html(html_data, height=1400, scrolling=True)
else:
    st.error("HTML 대시보드 파일(html_app/index.html)을 찾을 수 없습니다.")
