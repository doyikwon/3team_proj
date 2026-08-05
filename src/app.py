"""
NutriMatch 통합 멀티페이지 대시보드 진입점 (app.py)
 - Pretendard 폰트 시스템 및 정돈된 베이지/포레스트그린 사이드바 톤앤매너 적용
 - 사이드바-콘텐츠 좌우 대칭 여백 균형 최적화
 - Streamlit Material Symbols 아이콘 폰트 보존 (keyboard_double_ 등 아이콘 깨짐 방지)
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
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
        
        /* 본문 요소 폰트 및 자간 적용 (Streamlit 내장 아이콘 폰트 제외) */
        html, body, .stApp, p, div, span, button, input, select, textarea {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
            letter-spacing: -0.02em;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
            letter-spacing: -0.03em !important;
        }

        /* Streamlit Material Symbols 및 Icon 폰트 강제 보존 */
        [data-testid="stIcon"], 
        [class*="material-"], 
        .material-symbols-outlined,
        .material-icons,
        [data-testid="stSidebarCollapseButton"] *,
        [data-testid="stHeaderActionElements"] *,
        i[aria-hidden="true"] {
            font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
        }

        /* 메인 컨테이너 여백 및 대칭 배치 (사이드바 간격 28px + 우측 대칭) */
        .block-container { 
            padding: 0.75rem 2rem 1.5rem 2rem !important; 
            max-width: 100% !important; 
            margin: 0 auto !important;
        }
        
        header { display: none !important; }
        footer { display: none !important; }
        
        .stApp { 
            background-color: #FAF9F6 !important; 
        }
        
        /* 사이드바 대시보드 베이지 & 포레스트 그린 톤앤매너 조화 */
        [data-testid="stSidebar"] {
            background-color: #F4F2EC !important;
            border-right: 1px solid #E5E2D8 !important;
            padding-top: 1rem !important;
        }
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stSidebar"] span {
            color: #1E3A2F !important;
            font-weight: 600 !important;
        }

        /* iframe full width & 스크롤 유연성 */
        iframe { 
            border: none !important; 
            width: 100% !important; 
        }
    </style>
    """, unsafe_allow_html=True)
    
    html_path = os.path.join(os.path.dirname(__file__), "..", "html_app", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
            html_data = f.read()
        components.html(html_data, height=1550, scrolling=False)
    else:
        st.error("HTML 대시보드 파일(html_app/index.html)을 찾을 수 없습니다.")

def render_data_analysis_page():
    data_analysis_path = os.path.join(os.path.dirname(__file__), "pages", "_02_Data_Analysis.py")
    if os.path.exists(data_analysis_path):
        with open(data_analysis_path, "r", encoding="utf-8") as f:
            code = f.read()
        exec(code, globals())
    else:
        st.error("데이터 분석 파일(src/pages/_02_Data_Analysis.py)을 찾을 수 없습니다.")

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

# Streamlit st.navigation API 구동 (pages/ 자동 스캔 차단 후 st.Page 컨트롤)
if hasattr(st, "navigation") and hasattr(st, "Page"):
    page_1 = st.Page(render_custom_care_page, title="맞춤 진단", icon="🌱", default=True)
    page_2 = st.Page(render_data_analysis_page, title="데이터 분석", icon="📊")
    
    # 약통 페이지 존재 시 추가
    html_pillbox_path = os.path.join(os.path.dirname(__file__), "..", "html_app", "virtual_pillbox.html")
    if os.path.exists(html_pillbox_path):
        page_3 = st.Page(render_virtual_pillbox_page, title="나의 약통", icon="💊")
        pg = st.navigation([page_1, page_3, page_2])
    else:
        pg = st.navigation([page_1, page_2])
        
    pg.run()
else:
    st.sidebar.title("🌱 NutriMatch")
    menu_options = ["맞춤 진단", "데이터 분석"]
    html_pillbox_path = os.path.join(os.path.dirname(__file__), "..", "html_app", "virtual_pillbox.html")
    if os.path.exists(html_pillbox_path):
        menu_options.insert(1, "나의 약통")
        
    menu = st.sidebar.radio("메뉴 선택", menu_options)
    
    if menu == "맞춤 진단":
        render_custom_care_page()
    elif menu == "나의 약통":
        render_virtual_pillbox_page()
    elif menu == "데이터 분석":
        render_data_analysis_page()