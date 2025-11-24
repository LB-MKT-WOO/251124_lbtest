"""Trend section with various trend charts."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from performance_dashboard.utils.helpers import add_time_bucket, safe_divide, get_bucket_aggregation


def render_trend_section(fdf, granularity):
    """Trend 섹션 렌더링"""
    st.header("📈 Trend")
    
    bd = add_time_bucket(fdf, granularity)
    
    col_t1, col_t2, col_t3 = st.columns(3)
    
    # 전환값 추이
    with col_t1:
        _render_conversion_trend(bd)
    
    # 퍼널 전환율 추이
    with col_t2:
        _render_funnel_conversion_trend(bd)
    
    # 단가 추이
    with col_t3:
        _render_cost_trend(bd)
    
    col_t4, col_t5 = st.columns(2)
    
    # 지표 추이 비교
    with col_t4:
        _render_metric_comparison(bd)
    
    # 세그먼트별 추이 비교
    with col_t5:
        _render_segment_trend_comparison(fdf, granularity)
    
    st.divider()


def _render_conversion_trend(bd):
    """전환값 추이 차트"""
    st.subheader("**전환값 추이**")
    tmp = get_bucket_aggregation(bd, ["cost", "signup_7d", "create_account_7d"])
    
    base = alt.Chart(tmp).encode(x=alt.X("bucket:T", title=None, axis=alt.Axis(format='%m/%d')))
    
    # 공통 색/범례 (한글 라벨 기준)
    color_scale = alt.Scale(
        domain=["비용", "회원가입", "지갑개설"],
        range=["#1f77b4", "#ff7f0e", "#2ca02c"]
    )
    color_enc = alt.Color(
        "metric_label:N",
        scale=color_scale,
        title=None,
        sort=["비용", "회원가입", "지갑개설"],
        legend=alt.Legend(title=None)
    )
    
    # 왼쪽 축: Cost → "비용"
    cost_line = (
        base
        .transform_calculate(metric='"Cost"', value="datum.cost", metric_label='"비용"')
        .mark_line(strokeDash=[4, 2])
        .encode(
            y=alt.Y("value:Q", axis=alt.Axis(title=None, format="~s")),
            color=color_enc,
            tooltip=[alt.Tooltip("bucket:T", format='%m/%d'), "metric_label:N", "value:Q"]
        )
    )
    
    # 오른쪽 축: signup_7d → "회원가입", create_account_7d → "지갑개설"
    right_lines = (
        base
        .transform_fold(["signup_7d", "create_account_7d"], as_=["metric", "value"])
        .transform_calculate(
            metric_label="datum.metric === 'signup_7d' ? '회원가입' : "
                         "(datum.metric === 'create_account_7d' ? '지갑개설' : datum.metric)"
        )
        .mark_line()
        .encode(
            y=alt.Y("value:Q", axis=alt.Axis(orient="right", title=None, format="~s")),
            color=color_enc,
            tooltip=[alt.Tooltip("bucket:T", format='%m/%d'), "metric_label:N", "value:Q"]
        )
    )
    
    chart = (
        alt.layer(cost_line, right_lines)
        .resolve_scale(y="independent")
        .properties(height=260)
        .interactive()
    )
    
    st.altair_chart(chart, use_container_width=True)


def _render_funnel_conversion_trend(bd):
    """퍼널 전환율 추이 차트"""
    st.subheader("**퍼널 전환율 추이**")
    tmp2 = get_bucket_aggregation(bd, ["installs", "signup_7d", "create_account_7d"])
    
    # 전환율 계산 (0 나눗셈 방지)
    tmp2["회원가입률"] = np.where(tmp2["installs"] > 0, tmp2["signup_7d"] / tmp2["installs"], np.nan)
    tmp2["지갑개설률"] = np.where(tmp2["signup_7d"] > 0, tmp2["create_account_7d"] / tmp2["signup_7d"], np.nan)
    
    # Long 형태로 변환
    rate_m = tmp2.melt(
        id_vars=["bucket"],
        value_vars=["회원가입률", "지갑개설률"],
        var_name="전환",
        value_name="Rate"
    )
    
    # 색/범례 정의
    color_scale = alt.Scale(
        domain=["회원가입률", "지갑개설률"],
        range=["#ff7f0e", "#2ca02c"]
    )
    
    chart2 = (
        alt.Chart(rate_m)
        .mark_line()
        .encode(
            x=alt.X("bucket:T", title=None, axis=alt.Axis(format='%m/%d')),
            y=alt.Y("Rate:Q", axis=alt.Axis(title=None, format=".0%")),
            color=alt.Color("전환:N", title=None, scale=color_scale),
            tooltip=[
                alt.Tooltip("bucket:T", title="Bucket", format='%m/%d'),
                alt.Tooltip("전환:N", title="지표"),
                alt.Tooltip("Rate:Q", title="전환율", format=".1%")
            ]
        )
        .transform_filter(alt.datum.Rate != None)
        .properties(height=260)
        .interactive()
    )
    
    st.altair_chart(chart2, use_container_width=True)


def _render_cost_trend(bd):
    """단가 추이 차트"""
    st.subheader("단가 추이")
    
    # 집계 & 계산
    cols = ["cost", "installs", "signup_7d", "create_account_7d"]
    if "impressions" in bd.columns:
        cols.append("impressions")
    agg = get_bucket_aggregation(bd, cols)
    
    if "impressions" in agg.columns:
        agg["CPM"] = np.where(agg["impressions"] > 0, agg["cost"] / agg["impressions"] * 1000.0, np.nan)
    agg["CPI"] = np.where(agg["installs"] > 0, agg["cost"] / agg["installs"], np.nan)
    agg["회원가입단가"] = np.where(agg["signup_7d"] > 0, agg["cost"] / agg["signup_7d"], np.nan)
    agg["지갑개설단가"] = np.where(agg["create_account_7d"] > 0, agg["cost"] / agg["create_account_7d"], np.nan)
    
    series = ["CPI", "회원가입단가", "지갑개설단가"]
    if "CPM" in agg.columns:
        series = ["CPM"] + series
    
    cost_m = agg.melt(
        id_vars=["bucket"],
        value_vars=series,
        var_name="지표",
        value_name="CostMetric"
    )
    
    # 인코딩 공통(범례/색/선스타일)
    color_scale = alt.Scale(
        domain=series,
        range=["#9467bd", "#1f77b4", "#ff7f0e", "#2ca02c"][:len(series)]
    )
    color_enc = alt.Color(
        "지표:N", scale=color_scale, sort=series,
        legend=alt.Legend(title=None, orient="top", direction="horizontal",
                         symbolStrokeWidth=3, symbolSize=120, labelFontSize=12, padding=6)
    )
    
    dash_scale = alt.Scale(
        domain=series,
        range=[[2, 2], [6, 3], [], []][:len(series)]
    )
    dash_enc = alt.StrokeDash("지표:N", scale=dash_scale, legend=None)
    
    base = alt.Chart(cost_m).encode(x=alt.X("bucket:T", title=None, axis=alt.Axis(format='%m/%d')))
    
    # 왼쪽 축: CPM/CPI/회원가입단가
    left_series = [s for s in series if s != "지갑개설단가"]
    left_lines = (
        base.transform_filter(alt.FieldOneOfPredicate(field="지표", oneOf=left_series))
        .mark_line()
        .encode(
            y=alt.Y("CostMetric:Q", axis=alt.Axis(title=None, format=",.0f")),
            color=color_enc,
            strokeDash=dash_enc,
            tooltip=[
                alt.Tooltip("bucket:T", title="Bucket", format='%m/%d'),
                alt.Tooltip("지표:N"),
                alt.Tooltip("CostMetric:Q", title="단가", format=",.0f")
            ]
        )
    )
    
    # 오른쪽 축: 지갑개설단가
    right_line = (
        base.transform_filter(alt.datum.지표 == "지갑개설단가")
        .mark_line()
        .encode(
            y=alt.Y("CostMetric:Q", axis=alt.Axis(orient="right", title="지갑개설단가", format=",.0f")),
            color=color_enc,
            strokeDash=dash_enc,
            tooltip=[
                alt.Tooltip("bucket:T", title="Bucket", format='%m/%d'),
                alt.Tooltip("지표:N"),
                alt.Tooltip("CostMetric:Q", title="단가", format=",.0f")
            ]
        )
    )
    
    chart2 = (
        alt.layer(left_lines, right_line)
        .resolve_scale(y="independent")
        .properties(height=260)
        .interactive()
    )
    
    st.altair_chart(chart2, use_container_width=True)
    
    if "CPM" not in agg.columns:
        st.caption("※ `impressions` 컬럼이 없어 CPM은 제외되었습니다. (계산식: cost / impressions × 1000)")


def _render_metric_comparison(bd):
    """지표 추이 비교 차트"""
    # 집계 데이터 준비
    cols = ["cost", "installs", "signup_7d", "create_account_7d"]
    if "impressions" in bd.columns:
        cols.append("impressions")
    agg = get_bucket_aggregation(bd, cols)
    
    # 날짜 컬럼 확인 및 처리
    candidate_dates = ["date", "bucket", "day", "event_date"]
    date_col = next((c for c in candidate_dates if c in agg.columns), None)
    if date_col is None:
        st.error("날짜 컬럼이 필요합니다. (가능한 이름: date, bucket, day, event_date)")
        return
    
    agg[date_col] = pd.to_datetime(agg[date_col], errors="coerce")
    agg.dropna(subset=[date_col], inplace=True)
    
    # 파생 지표 추가
    if "signup_7d" in agg.columns:
        agg["회원가입"] = agg["signup_7d"]
    if "create_account_7d" in agg.columns:
        agg["지갑개설"] = agg["create_account_7d"]
    if {"signup_7d", "installs"}.issubset(agg.columns):
        agg["회원가입률"] = safe_divide(agg["signup_7d"], agg["installs"])
    if {"create_account_7d", "installs"}.issubset(agg.columns):
        agg["지갑개설률"] = safe_divide(agg["create_account_7d"], agg["installs"])
    if {"cost", "installs"}.issubset(agg.columns):
        agg["CPI"] = safe_divide(agg["cost"], agg["installs"])
    if {"cost", "signup_7d"}.issubset(agg.columns):
        agg["회원가입단가"] = safe_divide(agg["cost"], agg["signup_7d"])
    if {"cost", "create_account_7d"}.issubset(agg.columns):
        agg["지갑개설 단가"] = safe_divide(agg["cost"], agg["create_account_7d"])
    
    # 일자 집계
    sum_cols = [c for c in ["installs", "signup_7d", "create_account_7d", "cost"] if c in agg.columns]
    mean_cols = [c for c in ["회원가입", "지갑개설", "회원가입률", "지갑개설률", "CPI", "회원가입단가", "지갑개설 단가"] if c in agg.columns]
    ts = (
        agg.groupby(date_col, as_index=False)
        .agg({**{c: "sum" for c in sum_cols}, **{c: "mean" for c in mean_cols}})
    )
    
    # 사용자 선택
    all_opts = [c for c in ["회원가입", "지갑개설", "회원가입률", "지갑개설률", "CPI", "회원가입단가", "지갑개설 단가"] if c in ts.columns]
    st.subheader("지표 추이 비교")
    selected = st.multiselect("지표 선택(복수가능)", all_opts, default=[x for x in ["회원가입", "지갑개설"] if x in all_opts])
    if not selected:
        st.info("최소 1개 이상 선택하세요.")
        return
    
    # 자동 포맷/스케일 결정
    rate_set = {"회원가입률", "지갑개설률"}
    only_rates = set(selected).issubset(rate_set) and len(selected) > 0
    
    plot_df = ts[[date_col] + selected].copy()
    
    if only_rates:
        melt_df = plot_df.melt(id_vars=[date_col], var_name="지표", value_name="값")
        y_enc = alt.Y("값:Q", title="값 (%)", axis=alt.Axis(format="%"))
        val_format = "%"
    else:
        for col in selected:
            if col in rate_set and col in plot_df.columns:
                plot_df[col] = plot_df[col] * 100
        melt_df = plot_df.melt(id_vars=[date_col], var_name="지표", value_name="값")
        y_enc = alt.Y("값:Q", title="값", axis=alt.Axis(format=".2f"))
        val_format = ".2f"
    
    # 차트
    left_metrics = [m for m in selected if m not in rate_set]
    right_metrics = [m for m in selected if m in rate_set]
    
    if left_metrics and right_metrics:
        # 보조 Y축(두 축) 버전
        left_df = ts[[date_col] + left_metrics].copy()
        right_df = ts[[date_col] + right_metrics].copy()
        
        left_long = left_df.melt(id_vars=[date_col], var_name="지표", value_name="값")
        right_long = right_df.melt(id_vars=[date_col], var_name="지표", value_name="값")
        
        color_domain = left_metrics + right_metrics
        color_enc = alt.Color(
            "지표:N",
            title="지표",
            scale=alt.Scale(scheme="category10", domain=color_domain)
        )
        
        left_chart = (
            alt.Chart(left_long)
            .mark_line(point=True)
            .encode(
                x=alt.X(f"{date_col}:T", title="날짜", axis=alt.Axis(format='%m/%d')),
                y=alt.Y("값:Q", title="값", axis=alt.Axis(format=",.0f", orient="left")),
                color=color_enc,
                tooltip=[
                    alt.Tooltip(f"{date_col}:T", title="날짜", format='%m/%d'),
                    alt.Tooltip("지표:N"),
                    alt.Tooltip("값:Q", title="값", format=".2f"),
                ],
            )
        )
        
        right_chart = (
            alt.Chart(right_long)
            .mark_line(point=True)
            .encode(
                x=alt.X(f"{date_col}:T", title="날짜", axis=alt.Axis(format='%m/%d')),
                y=alt.Y("값:Q", title="전환율(%)", axis=alt.Axis(format="%", orient="right")),
                color=color_enc,
                tooltip=[
                    alt.Tooltip(f"{date_col}:T", title="날짜", format='%m/%d'),
                    alt.Tooltip("지표:N"),
                    alt.Tooltip("값:Q", title="값", format="%"),
                ],
            )
        )
        
        chart = alt.layer(left_chart, right_chart).resolve_scale(y="independent").properties(height=360).interactive()
        st.altair_chart(chart, use_container_width=True)
    else:
        # 단일 축 버전
        plot_df = ts[[date_col] + selected].copy()
        only_rates = set(selected).issubset(rate_set) and len(selected) > 0
        
        if only_rates:
            long_df = plot_df.melt(id_vars=[date_col], var_name="지표", value_name="값")
            y_enc = alt.Y("값:Q", title="값(%)", axis=alt.Axis(format="%"))
            val_format = "%"
        else:
            long_df = plot_df.melt(id_vars=[date_col], var_name="지표", value_name="값")
            y_enc = alt.Y("값:Q", title="값", axis=alt.Axis(format=",.0f"))
            val_format = ",.0f"
        
        chart = (
            alt.Chart(long_df)
            .mark_line(point=False)
            .encode(
                x=alt.X(f"{date_col}:T", title="날짜", axis=alt.Axis(format='%m/%d')),
                y=y_enc,
                color=alt.Color("지표:N", title="지표", scale=alt.Scale(scheme="category10")),
                tooltip=[
                    alt.Tooltip(f"{date_col}:T", title="날짜", format='%m/%d'),
                    alt.Tooltip("지표:N"),
                    alt.Tooltip("값:Q", title="값", format=val_format),
                ],
            )
            .properties(height=360)
            .interactive()
        )
        st.altair_chart(chart, use_container_width=True)


def _render_segment_trend_comparison(fdf, granularity):
    """세그먼트별 추이 비교 차트"""
    working_df = add_time_bucket(fdf, granularity)
    st.subheader("세그먼트별 추이 비교")
    
    date_col = "bucket"
    working_df[date_col] = pd.to_datetime(working_df[date_col], errors="coerce")
    working_df.dropna(subset=[date_col], inplace=True)
    
    # 파생 지표 추가
    if "signup_7d" in working_df.columns:
        working_df["회원가입"] = working_df["signup_7d"]
    if "create_account_7d" in working_df.columns:
        working_df["지갑개설"] = working_df["create_account_7d"]
    if {"signup_7d", "installs"}.issubset(working_df.columns):
        working_df["회원가입률"] = safe_divide(working_df["signup_7d"], working_df["installs"])
    if {"create_account_7d", "installs"}.issubset(working_df.columns):
        working_df["지갑개설률"] = safe_divide(working_df["create_account_7d"], working_df["installs"])
    if {"cost", "installs"}.issubset(working_df.columns):
        working_df["CPI"] = safe_divide(working_df["cost"], working_df["installs"])
    if {"cost", "signup_7d"}.issubset(working_df.columns):
        working_df["회원가입단가"] = safe_divide(working_df["cost"], working_df["signup_7d"])
    if {"cost", "create_account_7d"}.issubset(working_df.columns):
        working_df["지갑개설 단가"] = safe_divide(working_df["cost"], working_df["create_account_7d"])
    
    col_t5_1, col_t5_2, col_t5_3 = st.columns(3)
    with col_t5_1:
        dim_candidates = [c for c in ["source", "campaign_name", "sub_campaign_name", "creative_name"] if c in working_df.columns]
        if not dim_candidates:
            st.error("분해 가능한 컬럼이 없습니다.")
            return
        dim_col = st.selectbox("비교 기준", dim_candidates, index=0, key="segment_trend_comparison")
    
    with col_t5_2:
        metric_options = [c for c in ["회원가입", "지갑개설", "회원가입률", "지갑개설률", "CPI", "회원가입단가", "지갑개설 단가"] if c in working_df.columns]
        metric = st.selectbox("비교 지표", metric_options, index=0, key="segment_trend_metric")
    
    rate_set = {"회원가입률", "지갑개설률"}
    
    # 시간 x 분해축으로 집계 (캐싱 불가능 - dim_col이 동적이므로 직접 계산)
    grp_cols = [date_col, dim_col]
    base = working_df.copy()
    sum_map = {c: "sum" for c in ["installs", "signup_7d", "create_account_7d", "cost"] if c in base.columns}
    g = base.groupby(grp_cols, as_index=False).agg(sum_map)
    
    # 그룹 단위 파생 재계산
    if {"signup_7d", "installs"}.issubset(g.columns):
        g["회원가입률"] = safe_divide(g["signup_7d"], g["installs"])
    if {"create_account_7d", "installs"}.issubset(g.columns):
        g["지갑개설률"] = safe_divide(g["create_account_7d"], g["installs"])
    if {"cost", "installs"}.issubset(g.columns):
        g["CPI"] = safe_divide(g["cost"], g["installs"])
    if {"cost", "signup_7d"}.issubset(g.columns):
        g["회원가입단가"] = safe_divide(g["cost"], g["signup_7d"])
    if {"cost", "create_account_7d"}.issubset(g.columns):
        g["지갑개설 단가"] = safe_divide(g["cost"], g["create_account_7d"])
    if "signup_7d" in g.columns:
        g["회원가입"] = g["signup_7d"]
    if "create_account_7d" in g.columns:
        g["지갑개설"] = g["create_account_7d"]
    
    with col_t5_3:
        topk_default = 8
        k = st.slider("표시할 상위 카테고리 수", min_value=3, max_value=20, value=topk_default, step=1)
    
    if metric in rate_set:
        order_df = g.groupby(dim_col, as_index=False)[metric].mean().sort_values(metric, ascending=False)
    else:
        order_df = g.groupby(dim_col, as_index=False)[metric].sum().sort_values(metric, ascending=False)
    
    top_values = order_df.head(k)[dim_col].astype(str).tolist()
    g["_dim_str"] = g[dim_col].astype(str)
    plot_df = g[g["_dim_str"].isin(top_values)].copy()
    
    # 차트
    is_rate = metric in rate_set
    y_axis = alt.Y("값:Q",
                   title="전환율 (%)" if is_rate else "값",
                   axis=alt.Axis(format="%" if is_rate else ",.0f"))
    
    long_df = plot_df[[date_col, "_dim_str", metric]].rename(columns={metric: "값"})
    
    chart = (
        alt.Chart(long_df)
        .mark_line(point=False)
        .encode(
            x=alt.X(f"{date_col}:T", title="날짜", axis=alt.Axis(format='%m/%d')),
            y=y_axis,
            color=alt.Color("_dim_str:N", title=dim_col, scale=alt.Scale(scheme="category10")),
            tooltip=[
                alt.Tooltip(f"{date_col}:T", title="날짜", format='%m/%d'),
                alt.Tooltip("_dim_str:N", title=dim_col),
                alt.Tooltip("값:Q", title="값", format="%" if is_rate else ",.0f"),
            ],
        )
        .properties(height=380)
        .interactive()
    )
    
    st.altair_chart(chart, use_container_width=True)

