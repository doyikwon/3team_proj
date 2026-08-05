"""
초개인화 장바구니 큐레이션 (03_Curation.py)
작성자: Antigravity
작성일: 2026-07-11
역할: 추천 로직이 적용된 상품 리스트를 카드 뷰로 보여주고 병용 금기 등 상세 안내를 추가합니다.
"""

import streamlit as st
import sys
import os
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.data_loader import load_supplement_data
from utils.recommender import get_recommendations
from utils.clustering import get_current_user_cluster

st.set_page_config(page_title="NutriFit | 큐레이션 상세", page_icon="🛒", layout="wide")

# --- session_state 안전 폴백 및 쿼리 파라미터 연동 설정 ---
import urllib.parse
import json

if "answers" in st.query_params:
    try:
        answers_str = st.query_params["answers"]
        answers_data = json.loads(urllib.parse.unquote(answers_str))
        
        # HTML 앱의 key 값들과 Streamlit의 key 값들 매칭 보정
        goals_map = {
            'fatigue': '만성피로',
            'eyes': '눈 건조',
            'gut': '장 건강',
            'diet': '다이어트',
            'immunity': '면역력',
            'joints': '뼈/관절 건강',
            'skin': '피부 보습',
            'blood': '혈행 개선'
        }
        
        python_goals = []
        html_goals = answers_data.get('goals', [])
        for g in html_goals:
            if g in goals_map:
                python_goals.append(goals_map[g])
            elif g in goals_map.values():
                python_goals.append(g)
                
        # 질병/복용약물 매칭 보정
        diseases = []
        html_conds = answers_data.get('conditions', [])
        cond_map = {
            'bloodclot': '혈전 관련질환-항응고제',
            'diabetes': '당뇨',
            'bloodpressure': '고혈압'
        }
        for c in html_conds:
            if c in cond_map:
                diseases.append(cond_map[c])
            else:
                diseases.append(c)
                
        if answers_data.get('femaleStage') == 'pregnant':
            diseases.append('임산부')
            
        # 알레르기 매칭 보정
        allergies = []
        html_allergies = answers_data.get('allergies', [])
        allergy_map = {
            'shrimp': '갑각류',
            'soy': '대두',
            'gluten': '글루텐',
            'dairy': '유제품',
            'nuts': '견과류',
            'fish': '어류'
        }
        for a in html_allergies:
            if a in allergy_map:
                allergies.append(allergy_map[a])
            else:
                allergies.append(a)
                
        st.session_state.answers = {
            'goals': python_goals if python_goals else ['만성피로'],
            'gender': '여성' if answers_data.get('gender') == 'female' else '남성',
            'age': '30대',
            'diseases': diseases,
            'allergies': allergies,
            'current_supplements': answers_data.get('current_supplements', []),
            'pill_discomfort': '매우 불편함' if answers_data.get('pillDiscomfort') in ['extreme', 'uncomfortable'] else '상관없음',
            'budget': '3~5만원'
        }
    except Exception as e:
        st.error(f"설문 결과를 불러오는 중 오류가 발생했습니다: {e}")

if 'answers' not in st.session_state:
    st.session_state.answers = {
        'goals': ['만성피로', '눈 건조'],
        'gender': '남성',
        'age': '30대',
        'diseases': [],
        'allergies': [],
        'current_supplements': [],
        'pill_discomfort': '상관없음',
        'budget': '3~5만원'
    }

if 'compare_items' not in st.session_state:
    st.session_state.compare_items = []

# --- 보조 파싱 함수 정의 ---
def parse_capacity(name):
    # 100정, 60캡슐, 20포, 500ml, 120g 등 패턴 매칭
    match = re.search(r'(\d+)\s*(정|캡슐|포|ml|g|알|병|개월분)', name)
    if match:
        return match.group(0)
    return "정보 없음"

def parse_serving_days(name):
    # 20일분, 30일분, 1개월분(30), 2개월분(60) 등 매칭
    match_day = re.search(r'(\d+)\s*(일분|일)', name)
    if match_day:
        return int(match_day.group(1))
    match_month = re.search(r'(\d+)\s*(개월분|개월)', name)
    if match_month:
        return int(match_month.group(1)) * 30
    # 만약 정/캡슐 수가 나오면 1일 1회 복용으로 가정하고 일수 계산
    match_cnt = re.search(r'(\d+)\s*(정|캡슐|포|알)', name)
    if match_cnt:
        return int(match_cnt.group(1))
    return 30 # 기본값 30일

def get_formulation(name, tags):
    text = (name + " " + tags).lower()
    if "캡슐" in text:
        return "캡슐 (Capsule)"
    elif "정" in text or "타블렛" in text or "tablet" in text:
        return "정제 (Tablet)"
    elif "포" in text or "가루" in text or "분말" in text:
        return "분말 (Powder)"
    elif "액상" in text or "앰플" in text or "드링크" in text or "골드" in text:
        return "액상 (Liquid)"
    elif "젤리" in text or "구미" in text:
        return "젤리/구미 (Jelly)"
    return "기타 제형"

st.title("🛒 초개인화 맞춤 큐레이션")

# --- 고객 군집화 기반 사용자 분석 표시 ---
user_cluster, cluster_msg = get_current_user_cluster(st.session_state.answers)

colors = {
    '👑 VIP 고객': '#FCE4EC',     # 연한 핑크
    '🚀 잠재 충성 고객': '#FFF3E0', # 연한 오렌지
    '🌱 신규 고객': '#E8F5E9',     # 연한 그린
    '⚠️ 이탈 위험 고객': '#F5F5F5'  # 연한 그레이
}
bg_color = colors.get(user_cluster, '#FFFFFF')

st.markdown(f"""
<div style='background-color: {bg_color}; padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #E0E0E0;'>
    <h4 style='margin-top:0px; color:#333;'>고객 분석 결과: {user_cluster}</h4>
    <p style='margin-bottom:0px; color:#555;'>{cluster_msg}</p>
</div>
""", unsafe_allow_html=True)

st.write("유저님의 건강 목표, 라이프스타일, 그리고 안전성(Hard Filter)을 최우선으로 고려한 추천 상품입니다.")

df = load_supplement_data()
if df.empty:
    st.error("데이터를 불러오지 못했습니다.")
    st.stop()

recommended_items = get_recommendations(df, st.session_state.answers)

# --- 탭 구성 신설 ---
tab1, tab2 = st.tabs(["맞춤형 영양제 추천", "⚖️ 1:1 영양제 비교 분석"])

with tab1:
    st.markdown(f"**총 {len(recommended_items.head(6))}개의 큐레이션 상품이 준비되었습니다.**")
    
    cols = st.columns(3)
    for i, (_, row) in enumerate(recommended_items.head(6).iterrows()):
        with cols[i % 3]:
            with st.container(border=True):
                # 이미지 크기 70%로 조정 및 중앙 정렬
                st.markdown(f'<div style="text-align: center; margin-bottom: 10px;"><img src="{row["img_url"]}" style="width: 70%; max-height: 180px; object-fit: contain;"></div>', unsafe_allow_html=True)
                st.caption(row['brand'])
                st.subheader(row['name'])
                st.markdown(f"<h4 style='color: #E91E63;'>{row['price_cur']:,}원</h4>", unsafe_allow_html=True)
                st.write(f"⭐ {row['score']} | 💬 리뷰 {row['review_count']:,}건")
                
                # 비교함 담기 체크박스 추가
                is_selected = st.checkbox("비교함 담기 ⚖️", key=f"compare_{row['goods_no']}", value=(row['goods_no'] in st.session_state.compare_items))
                if is_selected:
                    if row['goods_no'] not in st.session_state.compare_items:
                        st.session_state.compare_items.append(row['goods_no'])
                else:
                    if row['goods_no'] in st.session_state.compare_items:
                        st.session_state.compare_items.remove(row['goods_no'])
                
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

with tab2:
    st.subheader("⚖️ 선택한 영양제 1:1 비교 분석")
    st.write("비교함에 담은 영양제들을 한눈에 나란히 비교합니다. (최대 3개 제품까지 지원)")
    
    selected_items = recommended_items[recommended_items['goods_no'].isin(st.session_state.compare_items)]
    
    if len(selected_items) == 0:
        st.info("💡 **'맞춤형 영양제 추천'** 탭에서 비교하고 싶은 상품 아래의 **[비교함 담기 ⚖️]** 체크박스를 체크해 주세요!")
    else:
        # 최대 3개까지만 비교
        compare_df = selected_items.head(3)
        
        # st.columns를 사용해 나란히 배치
        compare_cols = st.columns(len(compare_df))
        for idx, (_, row) in enumerate(compare_df.iterrows()):
            with compare_cols[idx]:
                with st.container(border=True):
                    # 상단 이미지 및 제목 (70% 크기 조정 및 중앙 정렬)
                    st.markdown(f'<div style="text-align: center; margin-bottom: 10px;"><img src="{row["img_url"]}" style="width: 70%; max-height: 180px; object-fit: contain;"></div>', unsafe_allow_html=True)
                    st.caption(row['brand'])
                    st.markdown(f"**{row['name']}**")
                    
                    st.markdown("---")
                    
                    # 1. 가격 및 용량
                    price = row['price_cur']
                    capacity = parse_capacity(row['name'])
                    st.markdown(f"**💰 가격 및 용량**")
                    st.markdown(f"- 가격: <h5 style='color: #E91E63; display:inline;'>{price:,}원</h5>", unsafe_allow_html=True)
                    st.markdown(f"- 용량: **{capacity}**")
                    
                    # 2. 1일 섭취 비용
                    days = parse_serving_days(row['name'])
                    daily_cost = int(price / days) if days > 0 else 0
                    st.markdown(f"**⏱️ 1일 섭취 비용**")
                    st.markdown(f"- 약 **{daily_cost:,}원** / 일 ({days}일분 기준)")
                    
                    # 3. 사용자 평점 및 리뷰 요약
                    st.markdown(f"**⭐ 평점 및 리뷰**")
                    st.markdown(f"- 평점: **{row['score']} / 5.0**")
                    st.markdown(f"- 리뷰 수: **{row['review_count']:,}건**")
                    st.markdown(f"- 요약: *{row['tags_clean']}* 중심의 긍정 평가 다수")
                    
                    # 4. 제형
                    formulation = get_formulation(row['name'], row['tags_clean'])
                    st.markdown(f"**💊 제형**")
                    st.markdown(f"- {formulation}")
                    
                    # 5. 주요 효능 및 핵심 성분
                    st.markdown(f"**✨ 주요 효능 및 성분**")
                    st.markdown(f"- {row['benefits_tag']}")
                    st.caption(f"근거: {row['reason']}")
                    
                    # 6. 안전성 경고
                    st.markdown(f"**⚠️ 주의 사항**")
                    st.caption(row['safety_warning'])
                    
                    st.markdown("---")
                    
                    # 구매 링크 다이렉트 연동 CTA 버튼
                    st.link_button("구매하러 가기 🔗", row['link'], use_container_width=True, type="primary")

st.caption("본 서비스는 의학적 진단·처방이 아니며, 건강기능식품 정보 제공을 목적으로 한 참고용입니다. 개인의 건강 상태에 따라 전문가와 상담하세요.")
st.caption("데이터 출처: 식약처 공공데이터 / 보건복지부 한국인 영양소 섭취기준(KDRI)")
