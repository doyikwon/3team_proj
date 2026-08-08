"""
고객 군집화 및 RFM 분석 화면 (04_Clustering.py)
작성자: Antigravity
작성일: 2026-08-01
역할: RFM 고객 데이터를 기반으로 군집 분석을 수행하고, 3D 시각화 및 군집별 비즈니스 액션 플랜을 제공합니다.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import silhouette_samples, silhouette_score
from sklearn.decomposition import PCA
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.clustering import generate_rfm_data, run_kmeans

st.set_page_config(page_title="NutriFit | 고객 군집화", page_icon="👥", layout="wide")

st.title("👥 고객 군집화 및 RFM 시각화 고도화")
st.markdown("K-Means를 활용한 구매 패턴 분석과 함께, 군집화 품질을 검증하는 다차원 평가 지표를 제공합니다.")

# 1. 데이터 생성 및 모델 학습
df = generate_rfm_data()
kmeans, scaler, mapping, labels = run_kmeans(df)

df['Cluster'] = labels

# 로그 변환 (1을 더해 0 또는 음수 방지)
df['Log_R'] = np.log1p(df['Recency'])
df['Log_F'] = np.log1p(df['Frequency'])
df['Log_M'] = np.log1p(df['Monetary'])

# 2. 평가 지표 및 축소 계산 (빠른 연산을 위해 캐싱 불필요 수준이지만 구성상 직접 수행)
scaled_data = scaler.transform(df[['Recency', 'Frequency', 'Monetary']])
silhouette_vals = silhouette_samples(scaled_data, kmeans.labels_)
sil_score = silhouette_score(scaled_data, kmeans.labels_)

pca = PCA(n_components=2)
pca_res = pca.fit_transform(scaled_data)
df['PCA1'] = pca_res[:, 0]
df['PCA2'] = pca_res[:, 1]
df['Silhouette'] = silhouette_vals
df['Cluster_Label'] = kmeans.labels_

colors = {
    '👑 VIP 고객': '#E91E63',
    '🚀 잠재 충성 고객': '#FF9800',
    '🌱 신규 고객': '#4CAF50',
    '⚠️ 이탈 위험 고객': '#9E9E9E'
}

# ==========================================
# [섹션 1] 상단: RFM 분포 3D 서브플롯 (1x3)
# ==========================================
st.subheader("📊 다차원 RFM 세그먼트 시각화")
st.write("원본 데이터 분포, 비대칭성을 해소한 로그 변환 분포, 최종 군집 결과를 3D로 비교합니다.")

fig_top = make_subplots(
    rows=1, cols=3, 
    specs=[[{'type': 'scatter3d'}, {'type': 'scatter3d'}, {'type': 'scatter3d'}]],
    subplot_titles=("1. 원본 RFM 분포", "2. 로그 변환(Log) RFM 분포", "3. 세그먼트 군집 결과 (원본 기준)")
)

# 서브플롯 1: 원본
fig_top.add_trace(
    go.Scatter3d(
        x=df['Recency'], y=df['Frequency'], z=df['Monetary'],
        mode='markers', marker=dict(size=3, color='#78909C', opacity=0.5), name='원본'
    ), row=1, col=1
)

# 서브플롯 2: 로그 변환
fig_top.add_trace(
    go.Scatter3d(
        x=df['Log_R'], y=df['Log_F'], z=df['Log_M'],
        mode='markers', marker=dict(size=3, color='#5C6BC0', opacity=0.5), name='로그변환'
    ), row=1, col=2
)

# 서브플롯 3: 군집 결과 (원본 축 기준)
for cluster_name, color in colors.items():
    c_data = df[df['Cluster'] == cluster_name]
    fig_top.add_trace(
        go.Scatter3d(
            x=c_data['Recency'], y=c_data['Frequency'], z=c_data['Monetary'],
            mode='markers', marker=dict(size=4, color=color, opacity=0.8), name=cluster_name
        ), row=1, col=3
    )

fig_top.update_layout(height=500, margin=dict(l=0, r=0, b=0, t=30), showlegend=False)
st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")

# ==========================================
# [섹션 2] 하단: 군집화 결과 평가 서브플롯 (1x3)
# ==========================================
st.subheader("📈 군집화 결과 검증 및 평가")
st.write(f"실루엣 스코어(평균): **{sil_score:.3f}** | 스케일링된 데이터를 바탕으로 군집의 특성과 응집도를 평가합니다.")

fig_bottom = make_subplots(
    rows=1, cols=3,
    specs=[[{'type': 'polar'}, {'type': 'xy'}, {'type': 'xy'}]],
    subplot_titles=("1. 군집별 RFM 스케일 평균 (Radar)", "2. PCA 2D 군집 경계 확인", "3. 실루엣 분석 (Silhouette)")
)

# 평가 1: Radar Chart (스케일된 값의 평균)
# 스케일된 데이터를 DataFrame에 합쳐서 평균 구하기
scaled_df = pd.DataFrame(scaled_data, columns=['R', 'F', 'M'])
scaled_df['Cluster'] = df['Cluster']
radar_mean = scaled_df.groupby('Cluster').mean().reset_index()

for _, row in radar_mean.iterrows():
    cluster_name = row['Cluster']
    fig_bottom.add_trace(
        go.Scatterpolar(
            r=[row['R'], row['F'], row['M'], row['R']],
            theta=['Recency', 'Frequency', 'Monetary', 'Recency'],
            fill='toself', name=cluster_name,
            line=dict(color=colors.get(cluster_name, '#000'))
        ), row=1, col=1
    )

# 평가 2: PCA 2D Scatter
for cluster_name, color in colors.items():
    c_data = df[df['Cluster'] == cluster_name]
    fig_bottom.add_trace(
        go.Scatter(
            x=c_data['PCA1'], y=c_data['PCA2'],
            mode='markers', marker=dict(color=color, opacity=0.6, size=6),
            name=cluster_name, showlegend=False
        ), row=1, col=2
    )
fig_bottom.update_xaxes(title_text="PCA Component 1", row=1, col=2)
fig_bottom.update_yaxes(title_text="PCA Component 2", row=1, col=2)

# 평가 3: Silhouette Analysis (Horizontal Bar)
# 실루엣 값을 정렬하여 칼 모양을 만듭니다.
df_sorted = df.sort_values(by=['Cluster_Label', 'Silhouette'], ascending=[True, True]).reset_index(drop=True)
df_sorted['Y_Index'] = df_sorted.index

for cluster_name, color in colors.items():
    c_data = df_sorted[df_sorted['Cluster'] == cluster_name]
    fig_bottom.add_trace(
        go.Bar(
            x=c_data['Silhouette'], y=c_data['Y_Index'],
            orientation='h',
            marker=dict(color=color, line=dict(width=0)),
            name=cluster_name, showlegend=False
        ), row=1, col=3
    )

# 평균 실루엣 스코어 기준선
fig_bottom.add_vline(x=sil_score, line_dash="dash", line_color="red", row=1, col=3, annotation_text="Avg", annotation_position="top left")
fig_bottom.update_xaxes(title_text="Silhouette Coefficient", row=1, col=3)
fig_bottom.update_yaxes(showticklabels=False, row=1, col=3)

fig_bottom.update_layout(height=450, margin=dict(l=20, r=20, b=40, t=40))
st.plotly_chart(fig_bottom, use_container_width=True)

st.markdown("---")

# ==========================================
# [섹션 3] 비즈니스 액션 플랜
# ==========================================
st.subheader("💡 세그먼트별 비즈니스 액션 플랜")
c1, c2 = st.columns(2)
c3, c4 = st.columns(2)

with c1:
    with st.container(border=True):
        st.markdown(f"<h3 style='color: {colors['👑 VIP 고객']}'>👑 VIP 고객</h3>", unsafe_allow_html=True)
        st.markdown("**특징:** 최근에 방문했고, 자주 구매하며, 구매 금액이 매우 높은 핵심 고객층")
        st.info("**Action Plan:**\n- VVIP 전용 한정판 영양제 우선 구매권 제공\n- 프리미엄 정기구독 서비스 제안\n- 1:1 맞춤형 전문가 건강 상담 서비스 제공")

with c2:
    with st.container(border=True):
        st.markdown(f"<h3 style='color: {colors['🚀 잠재 충성 고객']}'>🚀 잠재 충성 고객</h3>", unsafe_allow_html=True)
        st.markdown("**특징:** 꾸준히 구매하지만 구매 금액이나 빈도를 조금 더 늘릴 여지가 있는 고객층")
        st.success("**Action Plan:**\n- 묶음 상품(번들) 할인 혜택 제공\n- 연관 영양제(예: 비타민C 구매자에게 유산균 추천) 크로스셀링(Cross-selling)\n- 멤버십 등급 상향을 위한 조건부 쿠폰 발급")

with c3:
    with st.container(border=True):
        st.markdown(f"<h3 style='color: {colors['🌱 신규 고객']}'>🌱 신규 고객</h3>", unsafe_allow_html=True)
        st.markdown("**특징:** 가입 또는 최초 구매가 최근이지만 아직 추가 구매가 없는 고객층")
        st.warning("**Action Plan:**\n- 웰컴 쿠폰팩 및 첫 구매 감사 편지 발송\n- 베스트셀러 및 입문용 영양제(예: 종합비타민) 추천\n- 섭취 알림 푸시로 서비스 재방문 유도")

with c4:
    with st.container(border=True):
        st.markdown(f"<h3 style='color: {colors['⚠️ 이탈 위험 고객']}'>⚠️ 이탈 위험 고객</h3>", unsafe_allow_html=True)
        st.markdown("**특징:** 구매한 지 오래되었으며 전체 구매 빈도와 금액도 낮은 고객층")
        st.error("**Action Plan:**\n- 컴백 유도 파격 할인 쿠폰(예: 50% 할인) 발송\n- 최근 건강 트렌드나 신제품을 담은 뉴스레터 발송\n- 불만족 원인 파악을 위한 짧은 설문 진행 및 리워드 지급")
