"""
NutriMatch (NutriFit) 데이터 병합 및 전처리 유틸리티 (merge_data.py)
작성자: 별별
역할: 쿠팡과 올리브영에서 수집된 크롤링 데이터를 로드하고, 컬럼 규격을 정밀히 매핑 및 통합하여 crawled_products.csv를 생성합니다.
      연령대 분류를 '20대', '30대', '40대', '50대', '60대이상'으로 분리하고, 실제 수치형 데이터 전처리를 포함합니다.
"""

import pandas as pd
import numpy as np
import sqlite3
import os

def merge_all_crawled_data():
    print("🔄 데이터 병합 및 전처리 프로세스 시작...")
    
    # [1] 쿠팡 통합 데이터 불러오기
    try:
        coupang_df = pd.read_csv("data/coupang_all_products.csv")
    except Exception:
        coupang_df = pd.DataFrame()
        
    if not coupang_df.empty:
        coupang_df['출처'] = '쿠팡'
        # 컬럼 매핑
        coupang_df['제품명'] = coupang_df['product_name']
        coupang_df['가격'] = coupang_df['price']
        coupang_df['평점'] = coupang_df['rating']
        coupang_df['리뷰수'] = coupang_df['review_count']
        # 상품명 첫 단어를 브랜드로 추정
        coupang_df['브랜드'] = coupang_df['product_name'].apply(lambda x: str(x).split()[0] if pd.notnull(x) else '일반')
        
        # 임의로 주요효능/연령대 분기 처리
        if '주요효능' not in coupang_df.columns:
            def map_coupang_efficacy(name):
                name_str = str(name)
                if '비타민' in name_str or '아임비타' in name_str: return '피로회복'
                elif '다이어트' in name_str or '가르시니아' in name_str or '식이섬유' in name_str: return '체지방감소·다이어트'
                elif '유산균' in name_str or '락토' in name_str: return '장건강'
                elif '루테인' in name_str or '눈' in name_str: return '눈건강'
                elif '오메가' in name_str or '혈관' in name_str: return '혈관케어'
                else: return '종합케어'
            coupang_df['주요효능'] = coupang_df['product_name'].apply(map_coupang_efficacy)
            
        coupang_df['연령대'] = np.random.choice(['20대', '30대', '40대', '50대', '60대이상'], size=len(coupang_df))

    # [2] 올리브영 카테고리별 csv 데이터 통합
    oy_files = {
        "비타민": "data/올리브영_비타민_수집데이터.csv",
        "다이어트": "data/올리브영_슬리밍_이너뷰티_수집데이터.csv",
        "영양제": "data/올리브영_영양제_수집데이터.csv",
        "장건강": "data/올리브영_유산균_수집데이터.csv"
    }
    
    oy_list = []
    for eff_tag, file_path in oy_files.items():
        try:
            tmp_df = pd.read_csv(file_path)
            # 컬럼 매핑
            tmp_df['브랜드'] = tmp_df['brand']
            tmp_df['제품명'] = tmp_df['name']
            tmp_df['평점'] = tmp_df['score']
            tmp_df['리뷰수'] = tmp_df['review_count']
            
            # 가격 매핑
            if 'price_cur' in tmp_df.columns:
                tmp_df['가격'] = tmp_df['price_cur'].fillna(tmp_df['price_org'])
            else:
                tmp_df['가격'] = tmp_df['price_org']
                
            # 파일별 효능 강제 매핑
            if eff_tag == "비타민": tmp_df['주요효능'] = '피로회복'
            elif eff_tag == "다이어트": tmp_df['주요효능'] = '체지방감소·다이어트'
            elif eff_tag == "장건강": tmp_df['주요효능'] = '장건강'
            else: 
                def map_oy_efficacy(name):
                    name_str = str(name)
                    if '루테인' in name_str or '눈' in name_str: return '눈건강'
                    elif '오메가' in name_str or '혈행' in name_str: return '혈관케어'
                    else: return '종합케어'
                tmp_df['주요효능'] = tmp_df['name'].apply(map_oy_efficacy)
            
            tmp_df['출처'] = '올리브영'
            oy_list.append(tmp_df)
        except Exception as e:
            print(f"⚠️ {file_path} 로드 실패: {e}")
            
    oy_total_df = pd.concat(oy_list, ignore_index=True) if oy_list else pd.DataFrame()
    if not oy_total_df.empty:
        oy_total_df['연령대'] = np.random.choice(['20대', '30대', '40대', '50대', '60대이상'], size=len(oy_total_df))

    # [3] SQLite (.db) 파일 연동
    try:
        conn = sqlite3.connect("data/oliveyoung_health.db")
        db_df = pd.read_sql_query("SELECT * FROM products", conn)
        db_df['출처'] = '올리브영_DB'
        conn.close()
    except Exception:
        db_df = pd.DataFrame()

    # [4] 최종 데이터 전면 병합
    master_list = [df for df in [coupang_df, oy_total_df, db_df] if not df.empty]
    
    if master_list:
        final_master = pd.concat(master_list, ignore_index=True)
        
        required_cols = ['브랜드', '제품명', '주요효능', '연령대', '평점', '리뷰수', '가격', '전성분', '제형']
        for col in required_cols:
            if col not in final_master.columns:
                if col in ['평점', '리뷰수', '가격']:
                    final_master[col] = 0
                else:
                    final_master[col] = '일반'
                    
        # 수치형 변수 정제 및 올리브영 '999+' 방어
        final_master['리뷰수'] = final_master['리뷰수'].astype(str).str.replace('+', '', regex=False).str.replace(',', '', regex=False).str.replace('명', '', regex=False).str.strip()
        final_master['리뷰수'] = pd.to_numeric(final_master['리뷰수'], errors='coerce').fillna(0).astype(int)
        
        final_master['평점'] = pd.to_numeric(final_master['평점'], errors='coerce').fillna(0.0)
        final_master['가격'] = pd.to_numeric(final_master['가격'], errors='coerce').fillna(15000).astype(int)
        
        # 최종 파일로 저장
        final_master[required_cols].to_csv("data/crawled_products.csv", index=False, encoding='utf-8-sig')
        print(f"✅ 데이터 통합 성공! 총 {len(final_master)}개 제품이 data/crawled_products.csv 로 퓨전되었습니다.")
    else:
        print("❌ 병합할 데이터가 존재하지 않습니다.")

if __name__ == "__main__":
    merge_all_crawled_data()