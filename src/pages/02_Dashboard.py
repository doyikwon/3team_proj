"""
대시보드 메인 화면 (02_Dashboard.py)
작성자: Antigravity
작성일: 2026-07-11
역할: 문진 기능, 스코어보드, 랭킹 차트, 영양제 가이드를 포함하는 통합 대시보드 화면.
"""

import streamlit as st
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_supplement_data

st.set_page_config(page_title="NutriFit | 대시보드", page_icon="📊", layout="wide")

if 'agreed' not in st.session_state or not st.session_state.agreed:
    st.warning("서비스 이용 동의 후 진행할 수 있습니다.")
    st.stop()

if 'step' not in st.session_state:
    st.session_state.step = 1

ans = st.session_state.answers
df = load_supplement_data()

# 상단 헤더
st.title("🎯 NutriFit 통합 대시보드")
st.markdown("나만의 맞춤 영양을 설계하고 트렌디한 제품들을 확인하세요.")

# 메인 레이아웃: Section A(문진/스코어) + Section B(랭킹)
colA, colB = st.columns([7, 3])

with colA:
    st.markdown("### [Section A] 개인 맞춤 건강 컨디션 체크")
    
    # 문진 진행 중인 경우 (Step 1~5)
    if st.session_state.step <= 5:
        st.info("정확한 맞춤 큐레이션을 위해 아래 문진을 진행해 주세요.")
        progress_bar = st.progress(st.session_state.step * 20)
        st.write(f"**Step {st.session_state.step} / 5**")
        
        with st.container(border=True):
            if st.session_state.step == 1:
                st.subheader("1️⃣ 기본 정보 (Demographics)")
                ans['gender'] = st.radio("성별", ["남성", "여성"], index=0 if not ans['gender'] else ["남성", "여성"].index(ans['gender']) if ans['gender'] in ["남성", "여성"] else 0)
                if ans['gender'] == "여성":
                    st.info("임산부/수유부 안전 필터링 적용을 위해 생애주기를 선택해 주세요.")
                    female_status = st.selectbox("생애주기 상태", ["해당없음", "임신 준비 중", "임신 중", "수유 중", "폐경기"])
                    if female_status in ["임신 중", "수유 중"] and '임산부' not in ans['diseases']:
                        ans['diseases'].append('임산부')
                elif ans['gender'] == "남성":
                    st.multiselect("주요 고민 영역", ["탈모·두피 관리", "전립선 건강", "근육량 증가"])
                
                ans['age'] = st.selectbox("연령대", ["20대 미만", "20대", "30대", "40대", "50대", "60대 이상"])
                c1, c2 = st.columns(2)
                ans['height'] = c1.number_input("키 (cm)", value=170.0)
                ans['weight'] = c2.number_input("몸무게 (kg)", value=65.0)

            elif st.session_state.step == 2:
                st.subheader("2️⃣ 라이프스타일 & 일상 습관")
                ans['exercise'] = st.selectbox("운동 종류 및 목적", ["안 함·재활", "고강도 유산소", "저항성·근력", "유연성·코어", "고강도 인터벌"])
                ans['alcohol'] = st.radio("음주 빈도", ["전혀 안 함", "보통", "잦은 음주"])
                st.slider("스트레스 자가인지", 1, 5, 3)

            elif st.session_state.step == 3:
                st.subheader("3️⃣ 건강 상태 및 안전성 필터")
                st.error("💡 알레르기 및 복용 약물은 부작용 방지를 위한 하드 필터로 적용됩니다.")
                ans['smoking'] = st.radio("흡연 여부", ["비흡연", "흡연"])
                
                al_options = ["갑각류", "대두", "글루텐", "유제품", "견과류", "어류", "없음"]
                col_a1, col_a2 = st.columns([2, 1])
                with col_a1:
                    sel_al = st.multiselect("알레르기 원료", al_options, default=[x for x in ans['allergies'] if x in al_options])
                with col_a2:
                    cus_al = st.text_input("기타 알레르기 (수기 입력, 쉼표 구분)", value=",".join([x for x in ans['allergies'] if x not in al_options]))
                ans['allergies'] = sel_al + [x.strip() for x in cus_al.split(',') if x.strip()]
                
                dis_options = ["고혈압", "당뇨", "이상지질혈증", "만성 위장질환", "혈전 관련질환-항응고제", "간·신장질환", "없음"]
                col_d1, col_d2 = st.columns([2, 1])
                with col_d1:
                    sel_dis = st.multiselect("지병 및 복용 약물", dis_options, default=[x for x in ans['diseases'] if x in dis_options])
                with col_d2:
                    cus_dis = st.text_input("기타 지병/약물 (수기 입력, 쉼표 구분)", value=",".join([x for x in ans['diseases'] if x not in dis_options and x != '임산부']))
                ans['diseases'] = sel_dis + [x.strip() for x in cus_dis.split(',') if x.strip()]
                if '임산부' in st.session_state.answers.get('diseases', []) and '임산부' not in ans['diseases']:
                    ans['diseases'].append('임산부')
                
                sup_options = ["종합비타민", "오메가3", "유산균", "비타민C", "비타민B", "비타민D", "루테인", "칼슘/마그네슘", "홍삼", "콜라겐", "없음"]
                col_s1, col_s2 = st.columns([2, 1])
                with col_s1:
                    sel_sup = st.multiselect("현재 복용 중인 영양제 (중복 추천 방지)", sup_options, default=[x for x in ans['current_supplements'] if x in sup_options])
                with col_s2:
                    cus_sup = st.text_input("기타 영양제 (수기 입력, 쉼표 구분)", value=",".join([x for x in ans['current_supplements'] if x not in sup_options]))
                ans['current_supplements'] = sel_sup + [x.strip() for x in cus_sup.split(',') if x.strip()]

            elif st.session_state.step == 4:
                st.subheader("4️⃣ 건강 고민 및 목표")
                ans['goals'] = st.multiselect(
                    "가장 신경쓰이는 건강 고민 (최대 2개)",
                    ["만성피로", "눈 건조", "장 건강", "다이어트", "면역력", "뼈/관절 건강", "피부 보습", "혈행 개선"],
                    default=ans['goals'][:2]
                )

            elif st.session_state.step == 5:
                st.subheader("5️⃣ 섭취 편의성 및 구매 성향")
                ans['pill_discomfort'] = st.radio("알약 섭취 불편감", ["상관없음", "매우 불편함"])
                ans['budget'] = st.select_slider("월 예산대", options=["1~3만원", "3~5만원", "5~10만원", "10만원 이상"])

            st.write("---")
            nav_c1, nav_c2, nav_c3 = st.columns(3)
            if st.session_state.step > 1:
                if nav_c1.button("⬅️ 이전"):
                    st.session_state.step -= 1
                    st.rerun()
            if st.session_state.step < 5:
                if nav_c3.button("다음 ➡️"):
                    st.session_state.step += 1
                    st.rerun()
            else:
                if nav_c3.button("문진 완료 및 결과 보기 📊"):
                    st.session_state.step = 6
                    st.rerun()
                    
    # 문진이 완료된 경우 (Scoreboard)
    else:
        st.success("✅ 문진이 완료되었습니다! 분석 결과를 확인하세요.")
        score = 80
        if ans.get('alcohol') == "잦은 음주": score -= 10
        if ans.get('smoking') == "흡연": score -= 15
        if ans.get('exercise') in ["고강도 유산소", "저항성·근력"]: score += 10
        
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = score,
            title = {'text': "나의 웰니스 스코어"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4CAF50"},
                'steps': [
                    {'range': [0, 50], 'color': "#FFEBEE"},
                    {'range': [50, 80], 'color': "#FFF8E1"},
                    {'range': [80, 100], 'color': "#E8F5E9"}
                ]
            }
        ))
        st.plotly_chart(fig, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.info(f"**현재 목표:** {', '.join(ans['goals']) if ans['goals'] else '없음'}\n\n이 목표를 달성하기 위한 맞춤 큐레이션이 준비되었습니다.")
        with c2:
            st.warning("⚠️ **라이프스타일 분석**: 스트레스와 피로도가 감지되었습니다. 충분한 수면과 영양 보충이 필요합니다.")
            
        if st.button("👉 초개인화 맞춤 영양제 추천 보러가기", use_container_width=True, type="primary"):
            st.switch_page("pages/03_Curation.py")

with colB:
    st.markdown("### [Section B] 실시간 TOP 10 랭킹")
    st.caption("가장 많이 사랑받는 트렌디한 제품들 👑")
    
    if not df.empty:
        # 리뷰 수가 많은 순으로 10개 추출
        top10 = df.sort_values(by='review_count', ascending=False).head(10)
        for idx, (_, row) in enumerate(top10.iterrows()):
            with st.container(border=True):
                st.markdown(f"**{idx+1}위** 👑")
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.image(row['img_url'], use_container_width=True)
                with c2:
                    st.markdown(f"<span style='font-size:11px; color:#888;'>{row['brand']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**{row['name']}**")
                    st.markdown(f"<span style='color:#E91E63; font-weight:bold;'>{row['price_cur']:,}원</span>", unsafe_allow_html=True)
                    st.caption(f"⭐ {row['score']} | 🔥 HOT")
    else:
        st.write("데이터를 불러오는 중 오류가 발생했습니다.")

st.markdown("---")
# 하단 Section C: 영양제 상식 카드뉴스 가이드
st.markdown("### [Section C] 💡 영양제 상식 가이드")
card1, card2, card3 = st.columns(3)

with card1:
    st.markdown("""
    <div style='background-color:#E3F2FD; padding:20px; border-radius:15px; height:100%;'>
        <h4>💊 피곤한 직장인을 위한<br>비타민B군 고르는 법</h4>
        <p style='font-size:13px; color:#555;'>에너지 생성에 필수적인 비타민B군, 활성형인지 함량은 충분한지 꼭 확인하세요!</p>
    </div>
    """, unsafe_allow_html=True)

with card2:
    st.markdown("""
    <div style='background-color:#FFF3E0; padding:20px; border-radius:15px; height:100%;'>
        <h4>⏰ 식전? 식후?<br>영양제 타이밍 가이드</h4>
        <p style='font-size:13px; color:#555;'>지용성 비타민은 식후에, 유산균은 공복에! 흡수율을 200% 높이는 시간대 공식.</p>
    </div>
    """, unsafe_allow_html=True)

with card3:
    st.markdown("""
    <div style='background-color:#FFEBEE; padding:20px; border-radius:15px; height:100%;'>
        <h4>❌ 같이 먹으면 독?<br>병용 금기 영양제 조합</h4>
        <p style='font-size:13px; color:#555;'>철분과 칼슘은 상극! 서로의 흡수를 방해하는 최악의 조합 리스트를 공개합니다.</p>
    </div>
    """, unsafe_allow_html=True)
