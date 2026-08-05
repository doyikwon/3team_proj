"""
NutriMatch (NutriFit) 통합 멀티페이지 대시보드 진입점 (app.py)
작성자: Antigravity & 별별
역할: Streamlit 통합 실행 진입점
 - 페이지 1: "맞춤 진단" (html_app/index.html 전체 렌더링)
 - 페이지 2: "데이터 분석" (팀원 봄이 담당 파이썬 분석 및 랭킹 엔진)
"""

import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="NutriMatch | 개인 맞춤형 영양 케어 & 데이터 분석",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

def render_custom_care_page():
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
    
    html_path = os.path.join(os.path.dirname(__file__), "..", "html_app", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            html_data = f.read()
        components.html(html_data, height=1400, scrolling=True)
    else:
        st.error("HTML 대시보드 파일(html_app/index.html)을 찾을 수 없습니다.")

def render_virtual_pillbox_page():
    st.markdown("""
    <style>
        .block-container { 
            padding: 0 !important; 
            max-width: 100% !important; 
            margin: 0 !important;
        }
        header { display: none !important; }
        footer { display: none !important; }
        .stApp { background-color: #f8fafc; }
        iframe { border: none !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)
    
    html_path = os.path.join(os.path.dirname(__file__), "..", "html_app", "virtual_pillbox.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            html_data = f.read()
        components.html(html_data, height=1200, scrolling=True)
    else:
        st.error("나의 약통 HTML 파일(html_app/virtual_pillbox.html)을 찾을 수 없습니다.")

# Streamlit 최신 st.navigation API 사용 시도
if hasattr(st, "navigation") and hasattr(st, "Page"):
    page_1 = st.Page(render_custom_care_page, title="맞춤 진단", icon="🌱", default=True)
    page_2 = st.Page("pages/02_Data_Analysis.py", title="데이터 분석", icon="📊")
    page_3 = st.Page(render_virtual_pillbox_page, title="나의 약통", icon="💊")
    
    pg = st.navigation([page_1, page_3, page_2])
    pg.run()
else:
    # Streamlit pages/ 디렉토리 표준 및 사이드바 탭 폴백
    st.sidebar.title("🌱 NutriMatch Navigation")
    menu = st.sidebar.radio("메뉴 이동", ["맞춤 진단", "나의 약통", "데이터 분석"])
    
    if menu == "맞춤 진단":
        render_custom_care_page()
    elif menu == "나의 약통":
        render_virtual_pillbox_page()
    elif menu == "데이터 분석":
        data_analysis_path = os.path.join(os.path.dirname(__file__), "pages", "02_Data_Analysis.py")
        if os.path.exists(data_analysis_path):
            with open(data_analysis_path, "r", encoding="utf-8") as f:
                code = f.read()
            exec(code)
        else:
            st.title("📊 데이터 분석")
            st.info("💡 데이터 분석 페이지 준비 중입니다. (팀원 봄이 작업 영역)")
