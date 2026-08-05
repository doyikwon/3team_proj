# 담당: 봄이 / TOP10 랭킹·데이터 분석 코드를 이 파일에 작성해주세요

import streamlit as st

st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
    
    html, body, .stApp, p, div, span, button, input, select, textarea, h1, h2, h3, h4, h5, h6 {
        font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    }

    [data-testid="stIcon"], 
    [class*="material-"], 
    .material-symbols-outlined,
    .material-icons,
    [data-testid="stSidebarCollapseButton"] *,
    [data-testid="stHeaderActionElements"] *,
    i[aria-hidden="true"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }

    .block-container { 
        padding: 1.5rem 2.5rem 2rem 2.5rem !important; 
        max-width: 100% !important; 
    }
    .stApp { background-color: #FAF9F6 !important; }
</style>
""", unsafe_allow_html=True)

st.title("📊 데이터 분석")
st.caption("식품의약품안전처 및 보건복지부 한국인 영양소 섭취기준(KDRI) 기반 분석")

st.markdown("---")

st.info("💡 **데이터 분석 페이지 준비 중입니다.** (팀원 봄이 작업 영역)")

st.markdown("""
### 📋 구현 예정 주요 기능
1. **TOP 10 랭킹 분석:** 대중적으로 많이 찾는 건강기능식품 영양 성분 순위
2. **영양소 섭취 기준 대조:** 한국인 성별·연령별 일일 권장 섭취량(RDA) 통계
3. **제품 성분 트렌드:** 카테고리별 성분 조합 및 함량 정보 visual chart
""")