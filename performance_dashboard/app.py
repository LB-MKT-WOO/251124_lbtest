"""Main Streamlit application entry point."""

import streamlit as st
import altair as alt


def run_dashboard():
    """Run the dashboard application."""
    # Lazy imports for faster initial loading
    from performance_dashboard.config import SHEET_URL, SHEET_NAME, CREDENTIALS_FILE
    from performance_dashboard.data.loader import load_mother_data
    from performance_dashboard.data.preprocessor import preprocess_df
    from performance_dashboard.ui.sidebar import render_sidebar_filters
    from performance_dashboard.sections.kpi import render_kpi_section
    from performance_dashboard.sections.trend import render_trend_section
    from performance_dashboard.sections.funnel import render_funnel_section
    from performance_dashboard.sections.segment import render_segment_section
    from performance_dashboard.sections.product import render_product_section
    
    # 기본 설정
    st.set_page_config(page_title="Performance Dashboard", layout="wide", page_icon="📈")
    alt.data_transformers.disable_max_rows()

    # 데이터 로딩
    try:
        mother_data = load_mother_data(SHEET_URL, SHEET_NAME, CREDENTIALS_FILE)
        if mother_data is None or mother_data.empty:
            st.error("구글 스프레드시트에서 데이터를 가져올 수 없습니다. 인증/권한을 확인하세요.")
            st.stop()
    except Exception as e:
        st.error(f"데이터 로딩 중 오류: {e}")
        st.stop()

    # 데이터 전처리
    try:
        df = preprocess_df(mother_data)
    except Exception as e:
        st.error(f"데이터 전처리 에러: {e}")
        st.stop()

    # 사이드바 필터 및 필터링된 데이터
    fdf, granularity, start_d, end_d = render_sidebar_filters(df)

    if fdf.empty:
        st.warning("선택한 필터에 해당하는 데이터가 없습니다.")
        st.stop()

    # 섹션 렌더링
    render_kpi_section(fdf)
    render_trend_section(fdf, granularity)
    render_funnel_section(fdf)
    render_segment_section(fdf)
    render_product_section(df)


if __name__ == "__main__":
    run_dashboard()

