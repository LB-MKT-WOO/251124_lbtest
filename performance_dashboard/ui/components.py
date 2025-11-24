"""UI components for the dashboard."""

import streamlit as st
import pandas as pd
import numpy as np


def create_kpi_card(label, value, format_str="{:,.0f}", delta=None, delta_format="{:+.1%}"):
    """KPI 카드 생성"""
    col1, col2 = st.columns([1, 2])
    with col1:
        st.caption(label)
    with col2:
        if isinstance(value, (int, float, np.floating)) and not pd.isna(value):
            value_text = format_str.format(value)
        else:
            value_text = "-"
        if delta is None or pd.isna(delta):
            st.markdown(f"<h3 style='margin:0'>{value_text}</h3>", unsafe_allow_html=True)
        else:
            delta_text = delta_format.format(delta)
            color = "green" if delta >= 0 else "red"
            st.markdown(f"<h3 style='margin:0'>{value_text} <span style='font-size:0.8em;color:{color};'>({delta_text})</span></h3>", unsafe_allow_html=True)

