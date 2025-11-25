"""Funnel section."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from performance_dashboard.utils.helpers import get_gradient_colors


def render_funnel_section(fdf):
    """Funnel 섹션 렌더링"""
    st.header("📊 Funnel")
    
    F_IMP = fdf["impressions"].sum()
    F_CLK = fdf["clicks"].sum()
    F_INS = fdf["installs"].sum()
    F_SGN = fdf["signup_7d"].sum()
    F_ACC = fdf["create_account_7d"].sum()
    F_DEP = fdf["deposit_30d"].sum()
    F_IO = fdf["initial_offering_30d"].sum()
    
    fun = pd.DataFrame({
        "Stage": ["Install", "Signup", "Create Account", "Deposit", "Initial Offering"],
        "Count": [F_INS, F_SGN, F_ACC, F_DEP, F_IO]
    })
    
    c_a, c_b, c_c = st.columns(3)
    
    with c_a:
        _render_funnel_chart(fun)
    
    with c_b:
        _render_conversion_rates(F_IMP, F_CLK, F_INS, F_SGN, F_ACC, F_DEP)
    
    with c_c:
        _render_cost_metrics(F_IMP, F_CLK, F_INS, F_SGN, F_ACC, fdf["cost"].sum())
    
    st.divider()


def _render_funnel_chart(fun):
    """퍼널 전환 차트"""
    st.subheader("**퍼널 전환 차트**")
    maxc = float(fun["Count"].max() or 0)
    fun["left"] = (maxc - fun["Count"]) / 2
    fun["right"] = fun["left"] + fun["Count"]
    
    ordered = ["Install", "Signup", "Create Account", "Deposit", "Initial Offering"]
    green_range = get_gradient_colors("green", 5, "lightblue")
    
    funnel_chart = (
        alt.Chart(fun)
        .mark_rect()
        .encode(
            y=alt.Y(
                "Stage:N",
                sort=ordered,
                title=None,
                axis=alt.Axis(ticks=False, domain=False, labelPadding=8),
                scale=alt.Scale(paddingInner=0, paddingOuter=0),
            ),
            x=alt.X("left:Q", axis=None, title=None, scale=alt.Scale(domain=[0, maxc])),
            x2="right:Q",
            color=alt.Color("Stage:N", legend=None,
                           scale=alt.Scale(domain=ordered, range=green_range)),
            tooltip=["Stage", "Count"],
        )
        .properties(height=alt.Step(44))
        .configure_view(strokeWidth=0)
    )
    
    st.altair_chart(funnel_chart, use_container_width=True)


def _render_conversion_rates(F_IMP, F_CLK, F_INS, F_SGN, F_ACC, F_DEP):
    """단계별 전환율 테이블"""
    st.subheader("**단계별 전환율**")
    conv = {
        "CTR": (F_CLK / F_IMP) if F_IMP > 0 else np.nan,
        "설치율": (F_INS / F_CLK) if F_CLK > 0 else np.nan,
        "회원가입률": (F_SGN / F_INS) if F_INS > 0 else np.nan,
        "지갑개설률": (F_ACC / F_SGN) if F_SGN > 0 else np.nan,
        "예치금입금율": (F_DEP / F_ACC) if F_ACC > 0 else np.nan,
    }
    conv_df = pd.DataFrame({"Metric": list(conv.keys()), "Rate": list(conv.values())})
    conv_df["Rate"] = conv_df["Rate"].apply(lambda x: f"{x:.1%}" if pd.notna(x) else "-")
    st.dataframe(conv_df, hide_index=True, use_container_width=True)


def _render_cost_metrics(F_IMP, F_CLK, F_INS, F_SGN, F_ACC, F_COST):
    """단계별 단가 테이블"""
    st.subheader("**단계별 단가**")
    cost_metrics = {
        "CPM": (F_COST / F_IMP * 1000) if F_IMP > 0 else np.nan,
        "CPC": (F_COST / F_CLK) if F_CLK > 0 else np.nan,
        "CPI": (F_COST / F_INS) if F_INS > 0 else np.nan,
        "회원가입단가": (F_COST / F_SGN) if F_SGN > 0 else np.nan,
        "지갑개설단가": (F_COST / F_ACC) if F_ACC > 0 else np.nan,
    }
    cost_df = pd.DataFrame({"Metric": list(cost_metrics.keys()), "Cost": list(cost_metrics.values())})
    cost_df["Cost"] = cost_df["Cost"].apply(lambda x: f"₩{x:,.0f}" if pd.notna(x) else "-")
    st.dataframe(cost_df, hide_index=True, use_container_width=True)

