"""Data preprocessing and derived metrics calculation."""

import pandas as pd
import numpy as np
import streamlit as st

from performance_dashboard.config import DATE_COL, METRICS, REQUIRED_COLS
from performance_dashboard.utils.helpers import safe_divide


@st.cache_data(show_spinner=False, max_entries=1)
def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:
    """데이터 전처리 및 파생 지표 계산"""
    df = df.copy()
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼 누락: {missing}")

    # Date 처리
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    df = df.dropna(subset=[DATE_COL])
    df.sort_values(DATE_COL, inplace=True)

    # 숫자형 캐스팅
    for c in METRICS:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # 파생 지표
    df["CTR"] = safe_divide(df["clicks"], df["impressions"])
    df["CPC"] = safe_divide(df["cost"], df["clicks"])
    df["CPI"] = safe_divide(df["cost"], df["installs"])
    df["Signup_CVR_7d"] = safe_divide(df["signup_7d"], df["installs"])
    df["Create_Account_CVR_7d"] = safe_divide(df["create_account_7d"], df["installs"])
    df["Deposit_Rate_1d"] = safe_divide(df["deposit_1d"], df["create_account_7d"])
    df["Deposit_Rate_30d"] = safe_divide(df["deposit_30d"], df["create_account_7d"])
    df["ARPU_1d"] = safe_divide(df["deposit_revenue_1d"], df["installs"])
    df["ARPU_30d"] = safe_divide(df["deposit_revenue_30d"], df["installs"])
    df["ARPPU_1d"] = safe_divide(df["deposit_revenue_1d"], df["deposit_1d"])
    df["ARPPU_30d"] = safe_divide(df["deposit_revenue_30d"], df["deposit_30d"])
    df["ROAS_1d"] = safe_divide(df["deposit_revenue_1d"], df["cost"])
    df["ROAS_30d"] = safe_divide(df["deposit_revenue_30d"], df["cost"])
    df["CAC_create_account_7d"] = safe_divide(df["cost"], df["create_account_7d"])
    df["CPS_deposit_30d"] = safe_divide(df["cost"], df["deposit_30d"])
    df["Offering_ROI_30d"] = safe_divide(df["initial_offering_revenue_30d"], df["cost"])

    # 날짜 파생
    df["date"] = df[DATE_COL].dt.date
    df["week"] = df[DATE_COL].dt.to_period("W").apply(lambda r: r.start_time.date())
    df["month"] = df[DATE_COL].dt.to_period("M").astype(str)

    return df

