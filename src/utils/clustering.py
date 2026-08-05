"""
RFM 기반 고객 군집화 분석 유틸리티 (clustering.py)
작성자: Antigravity
작성일: 2026-08-01
역할: 가상의 RFM 데이터를 생성하고, K-Means 알고리즘을 사용해 4개 군집(VIP, 잠재 충성, 이탈 위험, 신규)으로 세분화하며 현재 사용자의 군집을 추정합니다.
"""

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

@st.cache_data(show_spinner="가상 고객 RFM 데이터를 생성 중입니다...")
def generate_rfm_data(n_samples=500):
    """
    데모용 가상 RFM 고객 데이터를 생성합니다.
    """
    np.random.seed(42)
    
    # 4가지 서로 다른 분포를 가진 가상 데이터 생성하여 병합
    # 1. VIP성향 (최근 구매, 고빈도, 고금액)
    n1 = int(n_samples * 0.2)
    r1 = np.random.randint(1, 15, n1) # 1~15일
    f1 = np.random.randint(10, 30, n1)
    m1 = np.random.randint(100000, 300000, n1)
    
    # 2. 잠재충성성향 (최근 구매, 중빈도, 중금액)
    n2 = int(n_samples * 0.3)
    r2 = np.random.randint(5, 30, n2)
    f2 = np.random.randint(4, 15, n2)
    m2 = np.random.randint(30000, 150000, n2)
    
    # 3. 신규성향 (최근 구매, 저빈도, 저~중금액)
    n3 = int(n_samples * 0.25)
    r3 = np.random.randint(1, 10, n3)
    f3 = np.random.randint(1, 4, n3)
    m3 = np.random.randint(10000, 50000, n3)
    
    # 4. 이탈위험성향 (오래된 구매, 저~중빈도, 저금액)
    n4 = n_samples - n1 - n2 - n3
    r4 = np.random.randint(60, 180, n4)
    f4 = np.random.randint(1, 10, n4)
    m4 = np.random.randint(10000, 80000, n4)
    
    r = np.concatenate([r1, r2, r3, r4])
    f = np.concatenate([f1, f2, f3, f4])
    m = np.concatenate([m1, m2, m3, m4])
    
    df = pd.DataFrame({
        'Recency': r,
        'Frequency': f,
        'Monetary': m
    })
    
    # 약간의 노이즈 추가
    df['Recency'] = np.clip(df['Recency'] + np.random.normal(0, 2, n_samples), 1, 365).astype(int)
    df['Frequency'] = np.clip(df['Frequency'] + np.random.normal(0, 1, n_samples), 1, 50).astype(int)
    df['Monetary'] = np.clip(df['Monetary'] + np.random.normal(0, 5000, n_samples), 5000, 500000).astype(int)
    
    return df

@st.cache_resource(show_spinner="고객 군집화 모델(K-Means)을 학습 중입니다...")
def run_kmeans(df):
    """
    RFM 데이터를 표준화하고 K-Means를 돌려 4개 군집으로 분류합니다.
    (VIP, 잠재 충성 고객, 신규 고객, 이탈 위험 고객)
    """
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[['Recency', 'Frequency', 'Monetary']])
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    clusters = kmeans.fit_predict(scaled_data)
    
    # 각 군집의 평균값을 확인하여 이름을 매핑합니다.
    temp_df = df.copy()
    temp_df['Cluster'] = clusters
    
    cluster_centers = temp_df.groupby('Cluster').mean()
    
    # Monetary가 가장 높은 것을 VIP (3)
    # Recency가 가장 높은(가장 오래된) 것을 이탈 위험 (0)
    # 나머지를 Frequency로 구분: Frequency가 낮으면 신규 (1), 높으면 잠재 충성 (2)
    
    sorted_idx = np.argsort(cluster_centers['Monetary'].values)
    vip_cluster = sorted_idx[-1]
    
    rec_sorted_idx = np.argsort(cluster_centers['Recency'].values)
    churn_cluster = rec_sorted_idx[-1]
    
    # VIP와 이탈이 아닌 나머지 둘 찾기
    remains = [i for i in range(4) if i not in [vip_cluster, churn_cluster]]
    
    if len(remains) == 2:
        if cluster_centers.loc[remains[0], 'Frequency'] > cluster_centers.loc[remains[1], 'Frequency']:
            loyal_cluster = remains[0]
            new_cluster = remains[1]
        else:
            loyal_cluster = remains[1]
            new_cluster = remains[0]
    else:
        # Fallback 
        new_cluster = remains[0] if remains else 0
        loyal_cluster = remains[1] if len(remains)>1 else 1

    mapping = {
        vip_cluster: '👑 VIP 고객',
        loyal_cluster: '🚀 잠재 충성 고객',
        new_cluster: '🌱 신규 고객',
        churn_cluster: '⚠️ 이탈 위험 고객'
    }
    
    return kmeans, scaler, mapping, temp_df['Cluster'].map(mapping).values

def get_current_user_cluster(answers):
    """
    문진에서 얻은 예산과 영양제 개수 정보를 바탕으로
    가상의 RFM 값을 추정하고 군집을 반환합니다.
    """
    budget_map = {
        "1~3만원": 20000,
        "3~5만원": 40000,
        "5~10만원": 75000,
        "10만원 이상": 150000
    }
    
    # 기본값 처리
    m = budget_map.get(answers.get('budget', "3~5만원"), 40000)
    
    current_supplements = answers.get('current_supplements', [])
    f = len([s for s in current_supplements if s != '없음']) * 3  # 기본적으로 1개당 빈도수 3정도로 가정
    f = max(1, f)
    
    # 현재 로그인된(혹은 막 설문을 마친) 유저이므로 최근성은 매우 좋음(작음)
    r = 2 
    
    # 예산이 10만원 이상이거나, 여러 영양제를 먹고 있으면 VIP 확률 높임
    if m >= 150000 and f >= 6:
        cluster = '👑 VIP 고객'
        msg = "유저님은 영양 관리에 적극적인 VIP! 프리미엄 제품군을 추천합니다."
    elif m >= 75000:
        cluster = '🚀 잠재 충성 고객'
        msg = "꾸준히 건강을 관리하는 유저님을 위해 혜택 가득한 정기구독을 제안합니다."
    elif f <= 3:
        cluster = '🌱 신규 고객'
        msg = "영양 관리를 막 시작하셨군요! 기초 영양을 탄탄히 다져줄 베스트셀러를 추천합니다."
    else:
        cluster = '⚠️ 이탈 위험 고객'
        msg = "오랜만에 찾아주셨네요! 유저님만을 위한 맞춤 혜택을 확인해 보세요."
        
    return cluster, msg
