"""
데이터 로더 유틸리티 (data_loader.py)
작성자: Antigravity
작성일: 2026-07-11
역할: 영양제 데이터셋을 로드하고 전처리하며, Streamlit의 st.cache_data를 활용해 성능을 최적화합니다.
"""

import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="데이터를 불러오는 중입니다...")
def load_supplement_data(file_path='3team_proj/data/올리브영_영양제_수집데이터.csv'):
    """
    올리브영 영양제 데이터를 로드하고 전처리합니다.
    """
    try:
        df = pd.read_csv(file_path)
        
        # 기본 전처리
        df['price_org'] = df['price_org'].fillna(df['price_cur'])
        df['score'] = df['score'].fillna(0.0)
        df['review_count'] = df['review_count'].str.replace(',', '').str.replace('건', '').str.replace('+', '', regex=False).fillna('0').astype(int)
        df['tags_clean'] = df['tags'].fillna('')
        
        return df
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()
