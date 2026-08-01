"""
시작 전 동의 및 안내 화면 (01_Intro.py)
작성자: Antigravity
작성일: 2026-07-11
역할: 서비스 안내 및 면책 공지를 제공하며, 필수 항목 동의 후 문진 단계로 넘어갑니다.
"""

import streamlit as st

st.set_page_config(page_title="NutriFit | 시작하기", page_icon="🌱")

st.markdown("## 📋 서비스 이용 동의 (동의 게이트)")

st.warning("🚨 **안내 공지**: 본 서비스는 의학적 치료나 진단을 대체하는 의료 행위가 아니며, 라이프스타일을 바탕으로 영양 정보를 제공하는 '참고용 컨디션 체크' 서비스입니다. 기저질환자 및 임산부는 영양제 섭취 전 반드시 전문가와 상담하시기 바랍니다.")

st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
agree_1 = st.checkbox("[필수] 개인정보 수집·이용 동의")
st.caption("수집 항목: 성명, 나이, 성별, 건강 고민 | 목적: 1:1 맞춤 영양 정보 추천")

agree_2 = st.checkbox("[필수] 건강정보(민감정보) 활용 동의")
st.caption("수집 항목: 기저질환, 약물 복용 여부, 영양제 섭취 데이터 | 목적: 중복·초과 섭취 방지 및 안전 알레르기 필터링")

agree_3 = st.checkbox("[필수] 서비스 면책 사항 확인")
st.caption("본 서비스는 참고용 웰니스 가이드이며 의학적 진단·치료를 대신하지 않습니다.")

agree_4 = st.checkbox("[선택] 마케팅 정보 수신 동의")
st.caption("영양 정보 소식지 및 맞춤 혜택 알림 수신 동의")
st.markdown("</div>", unsafe_allow_html=True)

if agree_1 and agree_2 and agree_3:
    st.success("모든 필수 항목에 동의하셨습니다. 셀프 체크를 시작해 주세요!")
    if st.button("동의하고 시작하기", type="primary", use_container_width=True):
        st.session_state.agreed = True
        st.switch_page("pages/02_Dashboard.py")
else:
    st.button("동의하고 시작하기 🚀", disabled=True, use_container_width=True)

st.markdown("---")
st.caption("본 서비스는 의학적 진단·처방이 아니며, 건강기능식품 정보 제공을 목적으로 한 참고용입니다. 개인의 건강 상태에 따라 전문가와 상담하세요.")
st.caption("데이터 출처: 식약처 공공데이터 / 보건복지부 한국인 영양소 섭취기준(KDRI)")

