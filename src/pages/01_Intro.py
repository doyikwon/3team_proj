"""
시작 전 동의 및 안내 화면 (01_Intro.py)
작성자: Antigravity
작성일: 2026-07-11
역할: 서비스 안내 및 면책 공지를 제공하며, 필수 항목 동의 후 문진 단계로 넘어갑니다.
"""

import streamlit as st

st.set_page_config(page_title="NutriFit | 시작하기", page_icon="💊")

st.markdown("## 📋 서비스 이용 동의")

st.warning("🚨 **면책 공지**: 본 서비스는 의학적 치료나 진단을 대체하는 의료 행위가 아니며, 유저의 라이프스타일을 바탕으로 영양제 큐레이션을 제공하는 '건강 컨디션 체크' 서비스입니다. 기저질환자 및 임산부는 영양제 섭취 전 반드시 전문가와 상담하시기 바랍니다.")

st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
agree_1 = st.checkbox("[필수] 서비스 이용약관 및 일반 개인정보 수집·이용 동의")

agree_2 = st.checkbox("[필수] 만 14세 이상 이용 확인")
if agree_2 is False:
    st.info("만 14세 미만은 법정대리인의 동의가 필요합니다. (데모 버전에서는 14세 이상만 진행 가능합니다.)")

agree_3 = st.checkbox("[필수] 건강 상태 및 라이프스타일(민감정보) 수집·이용 동의")
st.caption("질환 정보 및 복용 약물 수집에 대한 별도 동의가 포함됩니다.")
st.markdown("</div>", unsafe_allow_html=True)

if agree_1 and agree_2 and agree_3:
    st.success("모든 필수 항목에 동의하셨습니다. 컨디션 체크를 시작해 주세요!")
    if st.button("동의하고 시작하기", type="primary", use_container_width=True):
        st.session_state.agreed = True
        st.switch_page("pages/02_Dashboard.py")
else:
    st.button("컨디션 체크 시작하기 🚀", disabled=True)
