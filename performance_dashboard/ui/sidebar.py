"""Sidebar filters and controls."""

import streamlit as st
import pandas as pd

from performance_dashboard.utils.helpers import normalize_date_range
from performance_dashboard.data.loader import clear_data_cache


def create_multi_filter(df, column_name):
    """다중 선택 필터 생성"""
    unique_values = [str(x) for x in df[column_name].dropna().unique()]
    options = ["(All)"] + sorted(unique_values)
    selected = st.sidebar.multiselect(column_name, options, default=["(All)"])
    return selected


def apply_filter(series, selections):
    """필터 적용"""
    if "(All)" in selections or len(selections) == 0:
        return True
    return series.astype(str).isin(selections)


def render_sidebar_filters(df):
    """사이드바 필터 렌더링 및 필터링된 데이터 반환"""
    with st.sidebar:
        st.header("🔎 Filters")
        
        # 데이터 새로고침 버튼
        if st.button("🔄 데이터 새로고침", help="구글 스프레드시트 재조회(캐시 초기화)"):
            clear_data_cache()
            st.rerun()
    
    min_d, max_d = df["date"].min(), df["date"].max()
    
    # KST 기준 오늘 날짜 계산 (Streamlit 퀵 선택 버그 우회)
    today_kst = pd.Timestamp.now(tz="Asia/Seoul").date()
    max_pick = min(today_kst, max_d)  # KST 오늘과 데이터 최대일 중 작은 값 사용
    
    # 커스텀 프리셋 UI (Streamlit 퀵 선택 버그 우회)
    preset_options = ["최근 7일", "최근 30일", "최근 90일", "전체", "직접설정"]
    preset_choice = st.sidebar.selectbox("날짜 범위", preset_options, index=0)
    
    if preset_choice == "직접설정":
        raw_date = st.sidebar.date_input("기간 선택", (min_d, max_d), min_value=min_d, max_value=max_pick, key="date_range")
        start_d, end_d = normalize_date_range(raw_date, min_d, max_d)
    elif preset_choice == "최근 7일":
        start_d = max(min_d, today_kst - pd.Timedelta(days=6))
        end_d = min(max_pick, today_kst)
    elif preset_choice == "최근 30일":
        start_d = max(min_d, today_kst - pd.Timedelta(days=29))
        end_d = min(max_pick, today_kst)
    elif preset_choice == "최근 90일":
        start_d = max(min_d, today_kst - pd.Timedelta(days=89))
        end_d = min(max_pick, today_kst)
    else:  # All data
        start_d, end_d = min_d, max_d
    
    # 선택값 사후 클램프 (Streamlit 퀵 선택 버그 우회)
    end_d = min(end_d, max_pick)
    start_d = max(start_d, min_d)
    
    granularity = st.sidebar.selectbox("집계 단위", ["Daily", "Weekly", "Monthly"], index=0)
    
    # 세그먼트 필터 멀티셀렉트
    sel_source = create_multi_filter(df, "source")
    sel_campaign = create_multi_filter(df, "campaign_name")
    sel_sub_campaign = create_multi_filter(df, "sub_campaign_name")
    sel_creative = create_multi_filter(df, "creative_name")
    
    # 필터 적용 마스크
    mask = (df["date"] >= start_d) & (df["date"] <= end_d)
    mask = mask & apply_filter(df["source"], sel_source) \
               & apply_filter(df["campaign_name"], sel_campaign) \
               & apply_filter(df["sub_campaign_name"], sel_sub_campaign) \
               & apply_filter(df["creative_name"], sel_creative)
    
    fdf = df.loc[mask].copy()
    
    return fdf, granularity, start_d, end_d

