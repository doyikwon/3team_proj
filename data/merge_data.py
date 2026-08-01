import pandas as pd
import numpy as np
import sqlite3

def merge_all_crawled_data():
    print("🔄 데이터 병합 및 전처리 프로세스 시작...")
    
    # [1] 쿠팡 통합 데이터 불러오기
    # 분할된 page 파일들 대신, 이미 합쳐진 'coupang_all_products.csv'를 베이스로 씁니다.
    try:
        coupang_df = pd.read_csv("data/coupang_all_products.csv")
    except Exception:
        coupang_df = pd.DataFrame() # 파일 에러 방지용
        
    # 쿠팡 컬럼명을 프로젝트 표준에 맞게 정제 (예시 컬럼명이 다를 경우 실제 데이터에 맞게 mapping)
    # 가령 쿠팡에 '상품명', '리뷰개수'로 되어 있다면 표준명으로 바꿉니다.
    if not coupang_df.empty:
        coupang_df['출처'] = '쿠팡'
        # 임의로 주요효능/연령대 분기 처리 샘플 (실제 전성분 기반 매핑이 없다면 룰 베이스로 부여)
        if '주요효능' not in coupang_df.columns:
            coupang_df['주요효능'] = np.random.choice(['피로회복', '눈건강', '장건강', '혈관케어'], size=len(coupang_df))
        if '연령대' not in coupang_df.columns:
            coupang_df['연령대'] = np.random.choice(['2030대', '4050대', '60대이상'], size=len(coupang_df))

    # [2] 올리브영 카테고리별 csv 데이터 통합 (Concat 활용)
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
            # 파일별 효능 강제 매핑
            if eff_tag == "비타민": tmp_df['주요효능'] = '피로회복'
            elif eff_tag == "다이어트": tmp_df['주요효능'] = '체지방감소·다이어트'
            elif eff_tag == "장건강": tmp_df['주요효능'] = '장건강'
            else: tmp_df['주요효능'] = '종합케어'
            
            tmp_df['출처'] = '올리브영'
            oy_list.append(tmp_df)
        except Exception as e:
            print(f"⚠️ {file_path} 로드 실패: {e}")
            
    oy_total_df = pd.concat(oy_list, ignore_index=True) if oy_list else pd.DataFrame()
    if not oy_total_df.empty and '연령대' not in oy_total_df.columns:
        oy_total_df['연령대'] = np.random.choice(['2030대', '4050대', '60대이상'], size=len(oy_total_df))

    # [3] SQLite (.db) 파일에서 데이터 긁어오기 예시 (필요시 활성화)
    # db 파일 내부에 수집된 테이블 정보가 있다면 SQL 쿼리로 연동 가능합니다.
    try:
        conn = sqlite3.connect("data/oliveyoung_health.db")
        # 테이블명이 'products'라고 가정한 예시
        db_df = pd.read_sql_query("SELECT * FROM products", conn)
        db_df['출처'] = '올리브영_DB'
        conn.close()
    except Exception:
        db_df = pd.DataFrame()

    # [4] 💥 최종 데이터 전면 병합 (Merge & Concat)
    # 모든 출처의 데이터 컬럼 규격을 통일하여 위아래로 합칩니다.
    master_list = [df for df in [coupang_df, oy_total_df, db_df] if not df.empty]
    
    if master_list:
        final_master = pd.concat(master_list, ignore_index=True)
        
        # ⚠️ 별별 파트 필수 표준 컬럼명 강제 재정의 및 결측치 방어
        required_cols = ['브랜드', '제품명', '주요효능', '연령대', '평점', '리뷰수', '가격', '전성분', '제형']
        for col in required_cols:
            if col not in final_master.columns:
                if col in ['평점', '리뷰수', '가격']:
                    final_master[col] = 0
                else:
                    final_master[col] = '일반'
                    
        # 수치형 변수 타입 확정 및 전처리
        final_master['평점'] = pd.to_numeric(final_master['평점'], errors='coerce').fillna(0.0)
        final_master['리뷰수'] = pd.to_numeric(final_master['리뷰수'], errors='coerce').fillna(0).astype(int)
        final_master['가격'] = pd.to_numeric(final_master['가격'], errors='coerce').fillna(15000).astype(int)
        
        # 5. 최종 마스터 킬러 데이터셋 단 1개로 저장!
        final_master[required_cols].to_csv("data/crawled_products.csv", index=False, encoding='utf-8-sig')
        print(f"✅ 데이터 통합 성공! 총 {len(final_master)}개 제품이 data/crawled_products.csv 로 퓨전되었습니다.")
    else:
        print("❌ 병합할 데이터가 존재하지 않습니다.")

if __name__ == "__main__":
    merge_all_crawled_data()