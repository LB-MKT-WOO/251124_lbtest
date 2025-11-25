"""Segment comparison section."""

import streamlit as st
import pandas as pd

from performance_dashboard.utils.helpers import safe_divide, get_segment_aggregation


def render_segment_section(fdf):
    """세그먼트별 비교 섹션 렌더링"""
    st.header("세그먼트별 비교")
    
    col_seg, col_sort, col_min_inst = st.columns(3)
    with col_seg:
        seg = st.selectbox("비교 기준", ["source", "campaign_name", "sub_campaign_name", "creative_name"], index=0, key="segment_comparison")
    with col_min_inst:
        min_inst = st.slider("최소 설치수", 0, int(fdf["installs"].max() or 0), 0, step=10)
    
    cols_sum = ["impressions", "clicks", "installs", "signup_7d", "create_account_7d", "deposit_30d", "cost", "deposit_revenue_30d", "initial_offering_30d", "initial_offering_revenue_30d"]
    agg = get_segment_aggregation(fdf, seg, cols_sum)
    
    # 파생 컬럼
    agg["CTR"] = safe_divide(agg["clicks"], agg["impressions"])
    agg["설치율"] = safe_divide(agg["installs"], agg["clicks"])
    agg["회원가입률"] = safe_divide(agg["signup_7d"], agg["installs"])
    agg["지갑개설률"] = safe_divide(agg["create_account_7d"], agg["signup_7d"])
    agg["CPC"] = safe_divide(agg["cost"], agg["clicks"])
    agg["CPI"] = safe_divide(agg["cost"], agg["installs"])
    agg["회원가입단가"] = safe_divide(agg["cost"], agg["signup_7d"])
    agg["지갑개설단가"] = safe_divide(agg["cost"], agg["create_account_7d"])
    agg["입금 ROAS"] = safe_divide(agg["deposit_revenue_30d"], agg["cost"])
    agg["청약 ROAS"] = safe_divide(agg["initial_offering_revenue_30d"], agg["cost"])
    
    # 컬럼 이름 변경
    cols_value = ["노출", "클릭", "설치", "회원가입", "지갑개설", "입금", "비용", "입금액", "청약", "청약금"]
    col_dict = dict(zip(cols_sum, cols_value))
    agg = agg.rename(columns=col_dict)
    
    col_sort_list = ['CTR', '설치율', '회원가입률', '지갑개설률', 'CPC', 'CPI', '회원가입단가', '지갑개설단가', '입금 ROAS', '청약 ROAS', '비용', '노출', '설치', '클릭', '회원가입', '지갑개설', '입금', '입금액', '청약', '청약금']
    agg = agg[[seg] + [c for c in col_sort_list if c in agg.columns]]
    
    # 필터(품질 가드)
    agg = agg[agg["설치"] >= min_inst]
    
    with col_sort:
        sort_key = st.selectbox("정렬 기준", col_sort_list, index=1, key="segment_sort")
        ascending = st.checkbox("오름차순 정렬", value=False)
    
    agg = agg.sort_values(sort_key, ascending=ascending)
    styler = agg.style.format({
        "CTR": "{:.1%}",
        "설치율": "{:.1%}",
        "회원가입률": "{:.1%}",
        "지갑개설률": "{:.1%}",
        "CPC": "{:,.0f}",
        "CPI": "{:,.0f}",
        "회원가입단가": "{:,.0f}",
        "지갑개설단가": "{:,.0f}",
        "입금 ROAS": "{:.1%}",
        "청약 ROAS": "{:.1%}",
        "설치": "{:,.0f}",
        "노출": "{:,.0f}",
        "입금액": "{:,.0f}",
        "청약금": "{:,.0f}",
        "클릭": "{:,.0f}",
        "회원가입": "{:,.0f}",
        "지갑개설": "{:,.0f}",
        "입금": "{:,.0f}",
        "비용": "{:,.0f}",
        "청약": "{:,.0f}",
    })
    
    st.dataframe(styler, use_container_width=True, hide_index=True)

