"""
NutriMatch (NutriFit) 대시보드 메인 앱 (app.py)
작성자: Antigravity
작성일: 2026-07-18
역할: 기존 순수 HTML/JS로 작성된 완벽한 웹 대시보드를 Streamlit 화면 전체에 렌더링합니다.
"""

import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="NutriMatch | 개인 맞춤형 영양 진단",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Streamlit 기본 UI 숨기기 및 여백 제거
st.markdown("""
<style>
    /* 전체 화면 꽉 채우기 */
    .block-container { 
        padding: 0 !important; 
        max-width: 100% !important; 
        margin: 0 !important;
    }
    /* 헤더, 사이드바, 푸터 숨기기 */
    header { display: none !important; }
    #MainMenu { display: none !important; }
    footer { display: none !important; }
    [data-testid="stSidebarNav"] { display: none !important; }
    
    /* 기본 배경색 일치 및 스크롤바 최적화 */
    .stApp { background-color: #FAF9F6; }
    iframe { border: none !important; }
</style>
""", unsafe_allow_html=True)

# index.html 파일 읽어서 렌더링
html_path = os.path.join(os.path.dirname(__file__), "..", "html_app", "index.html")
if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        html_data = f.read()
    
    # iframe 형태로 전체 화면 렌더링
    # height를 넉넉하게 줘서 내부 스크롤을 유도합니다
    components.html(html_data, height=1200, scrolling=True)
else:
    st.error("HTML 대시보드 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
