"""
초개인화 장바구니 큐레이션 (03_Curation.py)
작성자: Antigravity
작성일: 2026-07-11
역할: 추천 로직이 적용된 상품 리스트를 카드 뷰로 보여주고 병용 금기 등 상세 안내를 추가합니다.
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_supplement_data
from utils.recommender import get_recommendations

st.set_page_config(page_title="NutriFit | 큐레이션 상세", page_icon="🛒", layout="wide")

if 'answers' not in st.session_state or not st.session_state.answers.get('goals'):
    st.warning("문진을 먼저 완료해 주세요.")
    st.stop()

st.title("🛒 초개인화 맞춤 큐레이션")
st.write("유저님의 건강 목표, 라이프스타일, 그리고 안전성(Hard Filter)을 최우선으로 고려한 추천 상품입니다.")

df = load_supplement_data()
if df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

recommended_items = get_recommendations(df, st.session_state.answers)
st.markdown(f"**총 {len(recommended_items.head(6))}개의 큐레이션 상품이 준비되었습니다.**")

cols = st.columns(3)
for i, (_, row) in enumerate(recommended_items.head(6).iterrows()):
    with cols[i % 3]:
        with st.container(border=True):
            st.image(row['img_url'], use_container_width=True)
            st.caption(row['brand'])
            st.subheader(row['name'])
            st.markdown(f"<h4 style='color: #E91E63;'>{row['price_cur']:,}원</h4>", unsafe_allow_html=True)
            st.write(f"⭐ {row['score']} | 💬 리뷰 {row['review_count']:,}건")
            
            # 상세 정보 Expander
            with st.expander("자세히 보기 (효능 및 주의사항)"):
                st.markdown("#### 📖 성분 및 제품 설명")
                st.markdown(f"<div style='background-color:#f8f9fa; padding:10px; border-radius:5px;'>{row['tags_clean']}를 주요 특징으로 하는 제품입니다.</div>", unsafe_allow_html=True)
                
                st.markdown("#### ✨ 효능 및 타겟 포인트")
                st.markdown(f"<div style='background-color:#E8F5E9; padding:10px; border-radius:5px; color:#2E7D32;'><b>{row['benefits_tag']}</b><br>{row['reason']}</div>", unsafe_allow_html=True)
                
                st.markdown("#### ⚠️ 안전성 필터 및 병용 금기 안내")
                warning_text = row['safety_warning']
                if "금기" in warning_text or "주의" in warning_text or "피하" in warning_text:
                    bg_color = "#FFEBEE"
                    text_color = "#C62828"
                    icon = "🚨"
                else:
                    bg_color = "#E3F2FD"
                    text_color = "#1565C0"
                    icon = "✅"
                    
                st.markdown(f"<div style='background-color:{bg_color}; padding:10px; border-radius:5px; color:{text_color};'>{icon} {warning_text}</div>", unsafe_allow_html=True)
                
            st.button("장바구니 담기 🛒", key=f"add_{i}", use_container_width=True)

st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.button("✅ 선택 상품 모두 담기", use_container_width=True)
with col2:
    st.button("🔔 정기구독 신청", use_container_width=True, type="primary")

st.caption("면책 조항: 본 큐레이션은 참고용 알고리즘 결과이며 의학적 진단을 대체하지 않습니다. 반드시 섭취 전 전문의 또는 약사와 상담하십시오.")
