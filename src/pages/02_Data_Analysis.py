"""
NutriMatch 데이터 분석 및 랭킹 엔진 페이지 (src/pages/02_Data_Analysis.py)
작성자: 봄이 (별별)
역할: 종합 서브플롯 시각화 대시보드 + 검색 및 대화형 랭킹 분석
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

st.title("📊 NutriMatch 실시간 데이터 종합 분석실")
st.markdown("##### 크롤링 데이터 다차원 집계(Groupby) 및 서브플롯 종합 시각화 파트")

# ==========================================================
# [데이터 로드 및 전처리]
# ==========================================================
@st.cache_data
def load_crawled_analysis_data():
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "data", "crawled_products.csv"),
        os.path.join(os.path.dirname(__file__), "..", "data", "crawled_products.csv"),
        "data/crawled_products.csv",
        "crawled_products.csv"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return pd.read_csv(path)
            
    # 에러 방지용 가상 데모 데이터
    return pd.DataFrame({
        '브랜드': ['고려은단', '나우푸드', '락토핏', '솔가', '센트룸', '종근당', '뉴트리원', '네이처메이드', '대웅제약', '일양약품'],
        '제품명': ['비타민C 1000', '실리마린 밀크씨슬', '생유산균 골드', '비타민D3 5000', '멀티비타민 포뮬러', '프로메가 오메가3', '루테인 지아잔틴', '밀크씨슬 컴플렉스', '임팩타민 프리미엄', '비타민C 500'],
        '주요효능': ['피로회복', '피로회복', '장건강', '관절보호', '혈관케어', '혈관케어', '눈건강', '피로회복', '피로회복', '피로회복'],
        '연령대': ['2030대', '2030대', '2030대', '4050대', '4050대', '4050대', '60대이상', '4050대', '2030대', '60대이상'],
        '평점': [4.8, 4.5, 4.7, 4.2, 4.6, 4.4, 4.5, 4.3, 4.9, 4.1],
        '리뷰수': [15200, 8400, 23000, 1200, 9500, 11000, 4300, 3100, 18000, 900],
        '가격': [22000, 18900, 15400, 28000, 32000, 19900, 24500, 21000, 35000, 12000]
    })

df = load_crawled_analysis_data()

# 추천 지수(Score) 공통 연산
max_price = df['가격'].max() if df['가격'].max() > 0 else 1
df['가격점수'] = (1 - (df['가격'] / max_price)) * 10
df['log_review'] = np.log(df['리뷰수'].replace(0, 1))
max_log_review = df['log_review'].max() if df['log_review'].max() > 0 else 1

df['추천 지수 (Score)'] = (df['평점'] * 0.4) + ((df['log_review'] / max_log_review) * 10 * 0.3) + (df['가격점수'] * 0.3)
df['추천 지수 (Score)'] = df['추천 지수 (Score)'].round(2)

# ==========================================================
# 1. 🖼️ [강사님 피드백 핵심] 종합 서브플롯(Subplots) 시각화
# ==========================================================
st.markdown("### 📈 전체 데이터 카테고리 종합 분석 (Subplots)")
st.caption("선택하지 않아도 주요 효능군, 연령대별 통계 및 가격 vs 스코어 관계를 한눈에 한 화면에서 비교합니다.")

# 2x2 서브플롯 생성
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        "① 주요 효능별 평균 추천 스코어 (Groupby)",
        "② 연령대별 수집 제품 수 분포",
        "③ 주요 효능별 평균 가격대 비교 (원)",
        "④ 가격 vs 추천 지수 상관관계"
    ),
    vertical_spacing=0.15,
    horizontal_spacing=0.1
)

# ① 효능별 평균 점수 (Groupby)
eff_groupby = df.groupby('주요효능')['추천 지수 (Score)'].mean().reset_index()
fig.add_trace(
    go.Bar(x=eff_groupby['주요효능'], y=eff_groupby['추천 지수 (Score)'], marker_color='#4CAF50', name="평균 스코어"),
    row=1, col=1
)

# ② 연령대별 제품 분포
age_groupby = df['연령대'].value_counts().reset_index()
age_groupby.columns = ['연령대', 'count']
fig.add_trace(
    go.Bar(x=age_groupby['연령대'], y=age_groupby['count'], marker_color='#FF9800', name="제품 수"),
    row=1, col=2
)

# ③ 효능별 평균 가격
price_groupby = df.groupby('주요효능')['가격'].mean().reset_index()
fig.add_trace(
    go.Bar(x=price_groupby['주요효능'], y=price_groupby['가격'], marker_color='#2196F3', name="평균 가격"),
    row=2, col=1
)

# ④ 가격 vs 스코어 산점도 (Scatter)
fig.add_trace(
    go.Scatter(
        x=df['가격'], y=df['추천 지수 (Score)'], 
        mode='markers',
        text=df['제품명'],
        marker=dict(size=10, color=df['평점'], colorscale='Viridis', showscale=True),
        name="제품 분포"
    ),
    row=2, col=2
)

fig.update_layout(height=700, showlegend=False, title_text="<b>NutriMatch 데이터 종합 통합 매트릭스</b>")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================================
# 2. 🔍 [상세 탐색] 키워드 검색 & 세부 필터링 TOP 10
# ==========================================================
st.markdown("### 🔎 조건별 세부 제품 랭킹 & 키워드 검색")

# 검색 및 셀렉트 박스 필터 한 줄 배치
col_search, col_eff, col_age = st.columns([1.2, 1, 1])

with col_search:
    search_keyword = st.text_input("🔍 제품명 / 브랜드 / 성분 키워드 검색", placeholder="예: 비타민, 고려은단, 유산균")

with col_eff:
    eff_list = ["전체"] + sorted(list(df['주요효능'].dropna().astype(str).unique()))
    selected_eff = st.selectbox("🎯 주요 효능 선택", eff_list)

with col_age:
    age_list = ["전체"] + sorted(list(df['연령대'].dropna().astype(str).unique()))
    selected_age = st.selectbox("👥 연령대 선택", age_list)

# 데이터 필터 연산
filtered_df = df.copy()

if search_keyword:
    filtered_df = filtered_df[
        filtered_df['제품명'].str.contains(search_keyword, case=False, na=False) |
        filtered_df['브랜드'].str.contains(search_keyword, case=False, na=False)
    ]

if selected_eff != "전체":
    filtered_df = filtered_df[filtered_df['주요효능'] == selected_eff]

if selected_age != "전체":
    filtered_df = filtered_df[filtered_df['연령대'] == selected_age]

# 랭킹 정렬
filtered_rank = filtered_df.sort_values(by='추천 지수 (Score)', ascending=False).reset_index(drop=True).head(10)

# 결과 출력
if not filtered_rank.empty:
    chart_col, table_col = st.columns([1.1, 0.9])
    
    with chart_col:
        st.markdown(f"📊 **검색/필터 결과 TOP {len(filtered_rank)} 스코어 시각화**")
        fig_sub = px.bar(
            filtered_rank, 
            x='추천 지수 (Score)', 
            y='제품명', 
            orientation='h', 
            color='추천 지수 (Score)',
            color_continuous_scale='Blues',
            text='추천 지수 (Score)'
        )
        fig_sub.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
        st.plotly_chart(fig_sub, use_container_width=True)
        
    with table_col:
        st.markdown("📋 **상세 통계 매트릭스**")
        st.dataframe(
            filtered_rank[['브랜드', '제품명', '주요효능', '연령대', '평점', '가격', '추천 지수 (Score)']],
            use_container_width=True,
            hide_index=True
        )
else:
    st.warning("⚠️ 입력하신 검색어 또는 필터 조건에 일치하는 제품이 없습니다. 다른 키워드로 검색해 보세요.")