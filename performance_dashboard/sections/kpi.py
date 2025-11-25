"""KPI Board section."""

import streamlit as st
import numpy as np

from performance_dashboard.ui.components import create_kpi_card
from performance_dashboard.utils.helpers import split_periods


def render_kpi_section(fdf):
    """KPI Board 섹션 렌더링"""
    st.header("📋 KPI Board")
    
    cur7, prv7 = split_periods(fdf, 7)
    
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        create_kpi_card("비용", fdf["cost"].sum(), format_str="₩{:,.0f}")
    with kpi_cols[1]:
        create_kpi_card("설치", fdf["installs"].sum())
    with kpi_cols[2]:
        create_kpi_card("회원가입", fdf["signup_7d"].sum())
    with kpi_cols[3]:
        create_kpi_card("지갑개설", fdf["create_account_7d"].sum())
    with kpi_cols[4]:
        create_kpi_card("청약금", fdf["initial_offering_revenue_30d"].sum(), format_str="₩{:,.0f}")
    
    kpi_cols2 = st.columns(5)
    with kpi_cols2[0]:
        create_kpi_card("CPI", (fdf["cost"].sum()/fdf["installs"].sum()) if fdf["installs"].sum()>0 else np.nan, format_str="₩{:,.0f}")
    with kpi_cols2[1]:
        create_kpi_card("회원가입 단가", (fdf["cost"].sum()/fdf["signup_7d"].sum()) if fdf["signup_7d"].sum()>0 else np.nan, format_str="₩{:,.0f}")
    with kpi_cols2[2]:
        create_kpi_card("지갑개설 단가", (fdf["cost"].sum()/fdf["create_account_7d"].sum()) if fdf["create_account_7d"].sum()>0 else np.nan, format_str="₩{:,.0f}")
    with kpi_cols2[3]:
        create_kpi_card("입금 ROAS", (fdf["deposit_revenue_30d"].sum()/fdf["cost"].sum()*100) if fdf["cost"].sum()>0 else np.nan, format_str="{:.2f}%")
    with kpi_cols2[4]:
        create_kpi_card("청약 ROAS", (fdf["initial_offering_revenue_30d"].sum()/fdf["cost"].sum()*100) if fdf["cost"].sum()>0 else np.nan, format_str="{:.2f}%")
    
    st.divider()

