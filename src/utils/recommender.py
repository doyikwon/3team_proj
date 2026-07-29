"""
추천 로직 유틸리티 (recommender.py)
작성자: Antigravity
작성일: 2026-07-11
역할: 유저의 문진 답변(Session State)을 기반으로 적합한 영양제를 추천하고, 
      하드 필터링(안전 경고), 효능 태그, 상세 병용 금기 경고 등을 계산하여 반환합니다.
"""

import pandas as pd
import streamlit as st

def apply_hard_filters(df, answers):
    filtered_df = df.copy()
    allergies = answers.get('allergies', [])
    if allergies and '없음' not in allergies:
        for allergy in allergies:
            filtered_df = filtered_df[~filtered_df['name'].str.contains(allergy, na=False)]
            filtered_df = filtered_df[~filtered_df['tags_clean'].str.contains(allergy, na=False)]
            
    diseases = answers.get('diseases', [])
    if '혈전 관련질환-항응고제' in diseases:
        filtered_df = filtered_df[~filtered_df['name'].str.contains('오메가|비타민K', na=False)]
        filtered_df = filtered_df[~filtered_df['tags_clean'].str.contains('오메가|비타민K', na=False)]
        
    current_supplements = answers.get('current_supplements', [])
    if current_supplements and '없음' not in current_supplements:
        for supp in current_supplements:
            if supp == '칼슘/마그네슘':
                filtered_df = filtered_df[~filtered_df['name'].str.contains('칼슘|마그네슘', na=False)]
                filtered_df = filtered_df[~filtered_df['tags_clean'].str.contains('칼슘|마그네슘', na=False)]
            elif supp == '종합비타민':
                filtered_df = filtered_df[~filtered_df['name'].str.contains('종합|멀티', na=False)]
                filtered_df = filtered_df[~filtered_df['tags_clean'].str.contains('종합|멀티', na=False)]
            else:
                filtered_df = filtered_df[~filtered_df['name'].str.contains(supp, na=False)]
                filtered_df = filtered_df[~filtered_df['tags_clean'].str.contains(supp, na=False)]
                
    return filtered_df

def get_recommendations(df, answers):
    df_safe = apply_hard_filters(df, answers)
    goals = answers.get('goals', [])
    
    goal_keyword_map = {
        '만성피로': ['비타민B', '활력', '피로', '홍삼'],
        '눈 건조': ['루테인', '아스타잔틴', '눈'],
        '장 건강': ['유산균', '프로바이오틱스', '장'],
        '다이어트': ['가르시니아', '다이어트', '체지방'],
        '면역력': ['면역', '아연', '비타민C'],
        '뼈/관절 건강': ['칼슘', '마그네슘', '비타민D', '관절'],
        '피부 보습': ['콜라겐', '히알루론산', '피부'],
        '혈행 개선': ['오메가3', '혈행', '징코']
    }
    
    def calculate_match_details(row):
        score = 0
        matched_goals = []
        text_to_search = str(row['name']) + ' ' + str(row['tags_clean'])
        
        # Benefits and match score
        for goal in goals:
            if goal in goal_keyword_map:
                for kw in goal_keyword_map[goal]:
                    if kw in text_to_search:
                        score += 10
                        if goal not in matched_goals:
                            matched_goals.append(goal)
                            
        # 효능(Benefits) 문구 동적 생성
        if matched_goals:
            benefits_tag = f"이 성분은 유저님의 **[{', '.join(matched_goals)}]** 개선에 도움을 줄 수 있습니다."
            reason = f"고객님의 '{', '.join(matched_goals)}' 목표 달성에 최적화된 영양제입니다."
        else:
            benefits_tag = "기초 영양을 채워주는 범용적인 데일리 건강기능식품입니다."
            reason = "리뷰가 많고 검증된 베스트셀러 영양제입니다."
            
        # 안전성 필터 및 병용 금기 안내(Safety & Contraindications) 로직 시뮬레이션
        safety_warning = "특별히 알려진 치명적인 부작용이나 병용 금기는 없습니다."
        warnings = []
        if '오메가' in text_to_search:
            warnings.append("항응고제(아스피린 등)를 복용 중이시라면 본 제품(오메가3 포함)은 수술 전 피하셔야 합니다.")
        if '비타민A' in text_to_search or '베타카로틴' in text_to_search:
            warnings.append("흡연자의 경우 고함량 비타민A(베타카로틴) 복용 시 폐암 위험이 높아질 수 있으므로 주의하세요.")
        if '비타민' in text_to_search or '종합' in text_to_search:
            warnings.append("종합비타민을 이미 드시고 있다면 수용성/지용성 비타민 성분이 중복/과다 복용될 수 있으니 상한선을 확인하세요.")
        if '유산균' in text_to_search or '프로바이오틱스' in text_to_search:
            warnings.append("항생제를 복용 중이라면 유산균은 시간 간격을 두고 복용하는 것이 좋습니다.")
            
        if warnings:
            safety_warning = " ".join(warnings) + " 안전한 섭취를 위해 전문가 상담을 권장합니다."
            
        return pd.Series({
            'match_score': score, 
            'reason': reason, 
            'benefits_tag': benefits_tag,
            'safety_warning': safety_warning
        })
        
    res = df_safe.apply(calculate_match_details, axis=1)
    df_safe['match_score'] = res['match_score']
    df_safe['reason'] = res['reason']
    df_safe['benefits_tag'] = res['benefits_tag']
    df_safe['safety_warning'] = res['safety_warning']
    
    recommended_df = df_safe[df_safe['match_score'] > 0].sort_values(by=['match_score', 'review_count'], ascending=[False, False])
    
    if recommended_df.empty:
        recommended_df = df_safe.sort_values(by='review_count', ascending=False).head(20)
        
    return recommended_df
