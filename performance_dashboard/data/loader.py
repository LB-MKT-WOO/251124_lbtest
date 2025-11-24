"""Data loading from Google Sheets."""

import pandas as pd
import streamlit as st

from performance_dashboard.data.gspread_reader import read_google_sheet_to_df


@st.cache_data(show_spinner=True, ttl=3600, max_entries=1)
def load_mother_data(sheet_url: str, sheet_name: str, cred_file: str) -> pd.DataFrame:
    """구글 시트 데이터 로드 (캐시됨)"""
    df = read_google_sheet_to_df(sheet_url, sheet_name, cred_file)
    if df is None:
        return pd.DataFrame()
    return df


def clear_data_cache():
    """데이터 로딩 캐시 초기화"""
    load_mother_data.clear()