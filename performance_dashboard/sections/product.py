"""Product analysis section."""

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

from performance_dashboard.data.product_loader import load_product_dates
from performance_dashboard.utils.helpers import safe_divide


def render_product_section(df):
    """Product 섹션 렌더링"""
    st.divider()
    st.header("📊 건물별 전환 데이터")
    st.markdown("product 기준 : 건물 공개일 ~ 청약 종료일")
    
    products = load_product_dates()
    
    if not products:
        st.warning("Product 날짜 파일을 확인해주세요.")
        return
    
    # 전체 Product 비교
    _render_all_products_comparison(df, products)
    
    st.divider()
    
    # 개별 Product 상세 분석
    _render_individual_product_analysis(df, products)


def _render_all_products_comparison(df, products):
    """전체 Product 비교 차트"""
    st.subheader("전체 비교")
    
    all_products_data = []
    for product in products:
        product_start = pd.to_datetime(product['start_date']).date()
        product_end = pd.to_datetime(product['end_date']).date()
        product_df = df[(df['date'] >= product_start) & (df['date'] <= product_end)].copy()
        
        if len(product_df) > 0:
            total_cost = product_df['cost'].sum()
            total_installs = product_df['installs'].sum()
            total_signup = product_df['signup_7d'].sum()
            total_create_account = product_df['create_account_7d'].sum()
            total_deposit_30d = product_df['deposit_30d'].sum()
            total_initial_offering_30d = product_df['initial_offering_30d'].sum()
            total_deposit_revenue_30d = product_df['deposit_revenue_30d'].sum()
            total_initial_offering_revenue_30d = product_df['initial_offering_revenue_30d'].sum()
            
            all_products_data.append({
                'product_name': product['name'],
                'product_id': product['id'],
                'theme_color': product.get('theme_color', '#1f77b4'),
                '비용': total_cost,
                '설치': total_installs,
                '회원가입': total_signup,
                '지갑개설': total_create_account,
                '입금건수': total_deposit_30d,
                '청약건수': total_initial_offering_30d,
                'CPI': total_cost / total_installs if total_installs > 0 else 0,
                '회원가입단가': total_cost / total_signup if total_signup > 0 else 0,
                '지갑개설단가': total_cost / total_create_account if total_create_account > 0 else 0,
                '회원가입률': total_signup / total_installs if total_installs > 0 else 0,
                '지갑개설률': total_create_account / total_installs if total_installs > 0 else 0,
                '입금전환율': total_deposit_30d / total_create_account if total_create_account > 0 else 0,
                '청약전환율': total_initial_offering_30d / total_create_account if total_create_account > 0 else 0,
                '입금 ROAS': total_deposit_revenue_30d / total_cost if total_cost > 0 else 0,
                '청약 ROAS': total_initial_offering_revenue_30d / total_cost if total_cost > 0 else 0,
                '입금액': total_deposit_revenue_30d,
                '청약금액': total_initial_offering_revenue_30d,
            })
    
    if not all_products_data:
        st.warning("표시할 Product 데이터가 없습니다.")
        return
    
    compare_df = pd.DataFrame(all_products_data)
    
    # 메트릭 선택 UI
    col_metric1, col_metric2, col_metric3, col_metric4 = st.columns([1, 1, 1, 1])
    
    with col_metric1:
        metric_options = {
            '비용': {'format': '₩{:,.0f}', 'axis_format': ',.0f', 'type': 'cost'},
            '설치': {'format': '{:,.0f}', 'axis_format': ',.0f', 'type': 'count'},
            '회원가입': {'format': '{:,.0f}', 'axis_format': ',.0f', 'type': 'count'},
            '지갑개설': {'format': '{:,.0f}', 'axis_format': ',.0f', 'type': 'count'},
            '입금건수': {'format': '{:,.0f}', 'axis_format': ',.0f', 'type': 'count'},
            '청약건수': {'format': '{:,.0f}', 'axis_format': ',.0f', 'type': 'count'},
            'CPI': {'format': '₩{:,.0f}', 'axis_format': ',.0f', 'type': 'cost'},
            '회원가입단가': {'format': '₩{:,.0f}', 'axis_format': ',.0f', 'type': 'cost'},
            '지갑개설단가': {'format': '₩{:,.0f}', 'axis_format': ',.0f', 'type': 'cost'},
            '회원가입률': {'format': '{:.1%}', 'axis_format': '%', 'type': 'rate'},
            '지갑개설률': {'format': '{:.1%}', 'axis_format': '%', 'type': 'rate'},
            '입금전환율': {'format': '{:.1%}', 'axis_format': '%', 'type': 'rate'},
            '청약전환율': {'format': '{:.1%}', 'axis_format': '%', 'type': 'rate'},
            '입금 ROAS': {'format': '{:.1%}', 'axis_format': '%', 'type': 'ratio'},
            '청약 ROAS': {'format': '{:.1%}', 'axis_format': '%', 'type': 'ratio'},
            '입금액': {'format': '₩{:,.0f}', 'axis_format': ',.0f', 'type': 'revenue'},
            '청약금액': {'format': '₩{:,.0f}', 'axis_format': ',.0f', 'type': 'revenue'},
        }
        
        selected_metric = st.selectbox(
            "비교할 메트릭 선택",
            list(metric_options.keys()),
            index=14,
            key="product_comparison_metric"
        )
    
    with col_metric2:
        sort_order = st.selectbox("정렬", ["기본", "내림차순", "오름차순"], index=0, key="product_sort_order")
    
    with col_metric3:
        product_names_list = compare_df['product_name'].tolist()
        selected_product_names = st.multiselect(
            "건물명 선택",
            product_names_list,
            default=[],
            key="product_name_filter"
        )
    
    # 필터링
    all_product_names = set(product_names_list)
    selected_set = set(selected_product_names)
    
    if len(selected_product_names) == 0 or selected_set == all_product_names:
        filtered_df = compare_df.copy()
        show_top_n = True
    else:
        filtered_df = compare_df[compare_df['product_name'].isin(selected_product_names)].copy()
        show_top_n = False
    
    if filtered_df.empty:
        st.warning("선택한 건물에 대한 데이터가 없습니다.")
        return
    
    with col_metric4:
        total_products = len(filtered_df)
        max_slider_value = max(2, total_products) if total_products == 1 else total_products
        
        if show_top_n:
            if total_products == 1:
                st.caption("상위 n개만 표시")
                st.text("1")
                top_n = 1
            else:
                top_n = st.slider("상위 n개만 표시", min_value=1, max_value=max_slider_value, value=total_products, key="product_top_n")
        else:
            top_n = len(filtered_df)
            if total_products == 1:
                st.caption("상위 n개만 표시")
                st.text("1")
            else:
                st.slider("상위 n개만 표시", min_value=1, max_value=max_slider_value, value=top_n, key="product_top_n", disabled=True)
    
    # 정렬 및 선택
    if sort_order == "기본":
        compare_df_sorted = filtered_df.sort_values('product_id', ascending=True).head(top_n)
    else:
        ascending = (sort_order == "오름차순")
        compare_df_sorted = filtered_df.sort_values(selected_metric, ascending=ascending).head(top_n)
    
    # 차트 생성
    metric_config = metric_options[selected_metric]
    
    if metric_config['type'] == 'rate':
        y_axis_format = '%'
        tooltip_format = '.1%'
    elif metric_config['type'] == 'ratio':
        y_axis_format = '%'
        tooltip_format = '.1%'
    else:
        y_axis_format = metric_config['axis_format']
        tooltip_format = metric_config['axis_format']
    
    filtered_color_map = compare_df.set_index('product_name')['theme_color'].to_dict()
    color_domain = compare_df_sorted['product_name'].tolist()
    color_range = [filtered_color_map.get(name, '#1f77b4') for name in color_domain]
    
    if sort_order == "기본":
        x_sort = alt.EncodingSortField(field='product_id', order='ascending')
    else:
        ascending = (sort_order == "오름차순")
        x_sort = alt.EncodingSortField(field=selected_metric, order='descending' if not ascending else 'ascending')
    
    chart_compare = alt.Chart(compare_df_sorted).mark_bar().encode(
        x=alt.X('product_name:N',
               title='Product',
               sort=x_sort,
               axis=alt.Axis(labelAngle=-45)),
        y=alt.Y(f'{selected_metric}:Q',
               title=selected_metric,
               axis=alt.Axis(format=y_axis_format)),
        color=alt.Color('product_name:N',
                       legend=None,
                       scale=alt.Scale(domain=color_domain, range=color_range)),
        tooltip=[
            alt.Tooltip('product_name:N', title='건물명'),
            alt.Tooltip('product_id:N', title='product_id'),
            alt.Tooltip(f'{selected_metric}:Q',
                       title=selected_metric,
                       format=tooltip_format)
        ]
    ).properties(height=400).interactive()
    
    st.altair_chart(chart_compare, use_container_width=True)
    
    # 상세 테이블
    with st.expander("📋 전체 Product 상세 데이터", expanded=False):
        display_df = compare_df_sorted.drop(columns=['theme_color']).copy()
        styled_df = display_df.style.format({
            '비용': '{:,.0f}',
            '설치': '{:,.0f}',
            '회원가입': '{:,.0f}',
            '지갑개설': '{:,.0f}',
            '입금건수': '{:,.0f}',
            '청약건수': '{:,.0f}',
            'CPI': '{:,.0f}',
            '회원가입단가': '{:,.0f}',
            '지갑개설단가': '{:,.0f}',
            '회원가입률': '{:.1%}',
            '지갑개설률': '{:.1%}',
            '입금전환율': '{:.1%}',
            '청약전환율': '{:.1%}',
            '입금 ROAS': '{:.1%}',
            '청약 ROAS': '{:.1%}',
            '입금액': '{:,.0f}',
            '청약금액': '{:,.0f}',
        })
        st.dataframe(styled_df, use_container_width=True, hide_index=True)


def _render_individual_product_analysis(df, products):
    """개별 Product 상세 분석"""
    st.markdown("### 🔍 개별 Product 상세 분석")
    
    product_names = [f"{p['name']}" for p in products]
    selected_idx = st.selectbox(
        "청약 Product 선택",
        range(len(products)),
        format_func=lambda i: product_names[i],
        key="product_selector"
    )
    
    selected_product = products[selected_idx]
    product_start = pd.to_datetime(selected_product['start_date']).date()
    product_end = pd.to_datetime(selected_product['end_date']).date()
    
    st.info(f"**{selected_product['name']}** | 기간: {product_start} ~ {product_end}")
    
    product_df = df[(df['date'] >= product_start) & (df['date'] <= product_end)].copy()
    
    if len(product_df) == 0:
        st.warning(f"선택한 기간({product_start} ~ {product_end})에 데이터가 없습니다.")
        return
    
    # 전체 집계
    total_cost = product_df['cost'].sum()
    total_installs = product_df['installs'].sum()
    total_signup = product_df['signup_7d'].sum()
    total_create_account = product_df['create_account_7d'].sum()
    total_deposit_30d = product_df['deposit_30d'].sum()
    total_initial_offering_30d = product_df['initial_offering_30d'].sum()
    total_deposit_revenue_30d = product_df['deposit_revenue_30d'].sum()
    total_initial_offering_revenue_30d = product_df['initial_offering_revenue_30d'].sum()
    
    # 단가 계산
    cpi = safe_divide(np.array([total_cost]), np.array([total_installs]))[0]
    signup_cost = safe_divide(np.array([total_cost]), np.array([total_signup]))[0]
    cac_create = safe_divide(np.array([total_cost]), np.array([total_create_account]))[0]
    offering_cost = safe_divide(np.array([total_cost]), np.array([total_initial_offering_30d]))[0]
    
    # ROAS 계산
    deposit_roas = safe_divide(np.array([total_deposit_revenue_30d]), np.array([total_cost]))[0]
    initial_offering_roas = safe_divide(np.array([total_initial_offering_revenue_30d]), np.array([total_cost]))[0]
    
    # 전환율 계산
    cvr_signup = safe_divide(np.array([total_signup]), np.array([total_installs]))[0]
    cvr_create_account = safe_divide(np.array([total_create_account]), np.array([total_installs]))[0]
    cvr_deposit = safe_divide(np.array([total_deposit_30d]), np.array([total_create_account]))[0]
    cvr_initial_offering = safe_divide(np.array([total_initial_offering_30d]), np.array([total_create_account]))[0]
    
    # 퍼널, 단가, ROAS 분석
    st.markdown("#### 📈 퍼널 전환율 분석 & 💰 단가 분석 & 📊 ROAS 분석")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        _render_product_funnel(total_installs, total_signup, total_create_account, total_deposit_30d, total_initial_offering_30d,
                              cvr_signup, cvr_create_account, cvr_deposit, cvr_initial_offering)
    
    with col2:
        _render_product_cost_comparison(cpi, signup_cost, cac_create, offering_cost)
    
    with col3:
        _render_product_roas_comparison(deposit_roas, initial_offering_roas)
    
    st.divider()
    
    # Source별 성과 비교
    _render_product_source_comparison(product_df)


def _render_product_funnel(total_installs, total_signup, total_create_account, total_deposit_30d, total_initial_offering_30d,
                          cvr_signup, cvr_create_account, cvr_deposit, cvr_initial_offering):
    """Product 퍼널 차트"""
    st.markdown("**퍼널 전환율 분석**")
    funnel_values = [total_installs, total_signup, total_create_account, total_deposit_30d, total_initial_offering_30d]
    funnel_stages = ['설치', '회원가입', '지갑개설', '입금', '청약']
    max_value = max(funnel_values) if funnel_values else 1
    num_stages = len(funnel_stages)
    
    y_scale = alt.Scale(domain=[-0.5, num_stages-0.5], reverse=True)
    x_scale = alt.Scale(domain=[-max_value*0.25, max_value])
    y_axis = None
    x_axis = None
    
    funnel_data = pd.DataFrame({
        '단계': funnel_stages,
        '수치': funnel_values,
        'left': [(max_value - v) / 2 for v in funnel_values],
        'right': [(max_value + v) / 2 for v in funnel_values],
        'y_pos': list(range(num_stages)),
        'y_pos2': [y + 1 for y in range(num_stages)],
        'y_pos_center': [y + 0.5 for y in range(num_stages)],
        'label_x': [-max_value*0.2] * num_stages
    })
    
    conversion_configs = [
        (cvr_signup, total_installs, 1),
        (safe_divide(np.array([total_create_account]), np.array([total_signup]))[0], total_signup, 2),
        (cvr_deposit, total_create_account, 3),
        (safe_divide(np.array([total_initial_offering_30d]), np.array([total_deposit_30d]))[0], total_deposit_30d, 4)
    ]
    
    conversion_data = []
    for cvr, denominator, stage_idx in conversion_configs:
        if not np.isnan(cvr) and denominator > 0 and stage_idx < num_stages:
            stage_row = funnel_data.iloc[stage_idx]
            center_x = (stage_row['left'] + stage_row['right']) / 2
            bg_width = max_value * 0.1
            bg_height = 0.4
            conversion_data.append({
                'y_pos_center': stage_row['y_pos_center'],
                'x_pos': center_x,
                'text': f'{cvr:.1%}',
                'bg_x1': center_x - bg_width / 2,
                'bg_x2': center_x + bg_width / 2,
                'bg_y1': stage_row['y_pos_center'] - bg_height / 2,
                'bg_y2': stage_row['y_pos_center'] + bg_height / 2
            })
    
    funnel_base = alt.Chart(funnel_data).mark_rect().encode(
        y=alt.Y('y_pos:Q', scale=y_scale, axis=y_axis),
        y2='y_pos2:Q',
        x=alt.X('left:Q', scale=x_scale, axis=x_axis),
        x2='right:Q',
        color=alt.Color('단계:N', legend=None, scale=alt.Scale(scheme='category10')),
        tooltip=[alt.Tooltip('수치:Q', title='전환수', format=',.0f')]
    ).properties(height=300)
    
    stage_labels = alt.Chart(funnel_data).mark_text(
        align='right', baseline='middle', fontSize=12, fontWeight='normal'
    ).encode(
        y=alt.Y('y_pos_center:Q', scale=y_scale, axis=y_axis),
        x=alt.X('label_x:Q', scale=x_scale),
        text='단계:N',
        tooltip=[]
    )
    
    chart_layers = [funnel_base, stage_labels]
    if conversion_data:
        conversion_df = pd.DataFrame(conversion_data)
        conversion_bg = alt.Chart(conversion_df).mark_rect(
            fill='black', fillOpacity=0.5, cornerRadius=8
        ).encode(
            y=alt.Y('bg_y1:Q', scale=y_scale, axis=y_axis),
            y2='bg_y2:Q',
            x=alt.X('bg_x1:Q', scale=x_scale),
            x2='bg_x2:Q',
            tooltip=[]
        )
        conversion_labels = alt.Chart(conversion_df).mark_text(
            align='center', baseline='middle', fontSize=10,
            fontWeight='normal', fill='white'
        ).encode(
            y=alt.Y('y_pos_center:Q', scale=y_scale, axis=y_axis),
            x=alt.X('x_pos:Q', scale=x_scale),
            text='text:N',
            tooltip=[]
        )
        chart_layers.extend([conversion_bg, conversion_labels])
    
    funnel_chart = alt.layer(*chart_layers).configure_view(strokeWidth=0)
    st.altair_chart(funnel_chart, use_container_width=True)


def _render_product_cost_comparison(cpi, signup_cost, cac_create, offering_cost):
    """Product 단가 비교 차트"""
    st.markdown("**단가 비교**")
    cost_data = pd.DataFrame({
        '단가유형': ['CPI', '회원가입단가', '지갑개설단가', '청약단가'],
        '단가': [
            cpi if not np.isnan(cpi) else 0,
            signup_cost if not np.isnan(signup_cost) else 0,
            cac_create if not np.isnan(cac_create) else 0,
            offering_cost if not np.isnan(offering_cost) else 0
        ]
    })
    
    cost_chart = alt.Chart(cost_data).mark_bar().encode(
        x=alt.X('단가유형:N', sort=['CPI', '회원가입단가', '지갑개설단가', '청약단가'], title='단가 유형'),
        y=alt.Y('단가:Q', title='단가 (₩)'),
        color=alt.Color('단가유형:N', legend=None, scale=alt.Scale(scheme='set2')),
        tooltip=[
            alt.Tooltip('단가유형:N', title='단가 유형'),
            alt.Tooltip('단가:Q', title='단가', format=',.0f')
        ]
    ).properties(height=300).interactive()
    
    st.altair_chart(cost_chart, use_container_width=True)


def _render_product_roas_comparison(deposit_roas, initial_offering_roas):
    """Product ROAS 비교 차트"""
    st.markdown("**ROAS 비교**")
    roas_data = pd.DataFrame({
        'ROAS유형': ['입금 ROAS', '청약 ROAS'],
        'ROAS': [
            deposit_roas if not np.isnan(deposit_roas) else 0,
            initial_offering_roas if not np.isnan(initial_offering_roas) else 0
        ]
    })
    
    roas_chart = alt.Chart(roas_data).mark_bar().encode(
        x=alt.X('ROAS유형:N', sort=['입금 ROAS', '청약 ROAS'], title='ROAS 유형'),
        y=alt.Y('ROAS:Q', title='ROAS'),
        color=alt.Color('ROAS유형:N', legend=None, scale=alt.Scale(
            domain=['입금 ROAS', '청약 ROAS'],
            range=['#1f77b4', '#ff7f0e']
        )),
        tooltip=[
            alt.Tooltip('ROAS유형:N', title='ROAS 유형'),
            alt.Tooltip('ROAS:Q', title='ROAS', format='.2f')
        ]
    ).properties(height=300).interactive()
    
    st.altair_chart(roas_chart, use_container_width=True)


def _render_product_source_comparison(product_df):
    """Product Source별 성과 비교"""
    st.markdown("#### 📋 Source별 성과 비교")
    
    source_agg = product_df.groupby('source').agg({
        'cost': 'sum',
        'installs': 'sum',
        'signup_7d': 'sum',
        'create_account_7d': 'sum',
        'deposit_30d': 'sum',
        'initial_offering_30d': 'sum',
        'deposit_revenue_30d': 'sum',
        'initial_offering_revenue_30d': 'sum'
    }).reset_index()
    
    # Source별 파이 차트
    st.markdown("**Source별 분포**")
    pie_col1, pie_col2 = st.columns(2)
    
    with pie_col1:
        _render_source_pie_chart(source_agg, 'installs', '설치')
        _render_source_pie_chart(source_agg, 'create_account_7d', '지갑개설')
    
    with pie_col2:
        _render_source_pie_chart(source_agg, 'signup_7d', '회원가입')
        _render_source_pie_chart(source_agg, 'initial_offering_revenue_30d', '청약금액')
    
    st.divider()
    
    # Source별 성과 테이블
    st.markdown("**Source별 상세 성과 테이블**")
    source_agg['CPI'] = safe_divide(source_agg['cost'], source_agg['installs'])
    source_agg['회원가입률'] = safe_divide(source_agg['signup_7d'], source_agg['installs'])
    source_agg['지갑개설률'] = safe_divide(source_agg['create_account_7d'], source_agg['installs'])
    source_agg['입금전환율_30d'] = safe_divide(source_agg['deposit_30d'], source_agg['create_account_7d'])
    source_agg['청약전환율_30d'] = safe_divide(source_agg['initial_offering_30d'], source_agg['create_account_7d'])
    source_agg['Deposit_ROAS_30d'] = safe_divide(source_agg['deposit_revenue_30d'], source_agg['cost'])
    source_agg['InitialOffering_ROAS_30d'] = safe_divide(source_agg['initial_offering_revenue_30d'], source_agg['cost'])
    
    display_cols = [
        'source', 'cost', 'installs', 'CPI', '회원가입률', '지갑개설률',
        '입금전환율_30d', '청약전환율_30d', 'Deposit_ROAS_30d', 'InitialOffering_ROAS_30d',
        'deposit_revenue_30d', 'initial_offering_revenue_30d'
    ]
    source_agg = source_agg[[c for c in display_cols if c in source_agg.columns]]
    
    source_styler = source_agg.style.format({
        'cost': '{:,.0f}',
        'installs': '{:,.0f}',
        'CPI': '{:,.0f}',
        '회원가입률': '{:.1%}',
        '지갑개설률': '{:.1%}',
        '입금전환율_30d': '{:.1%}',
        '청약전환율_30d': '{:.1%}',
        'Deposit_ROAS_30d': '{:.2f}',
        'InitialOffering_ROAS_30d': '{:.2f}',
        'deposit_revenue_30d': '{:,.0f}',
        'initial_offering_revenue_30d': '{:,.0f}'
    })
    
    st.dataframe(source_styler, use_container_width=True, hide_index=True)


def _render_source_pie_chart(source_agg, column, title):
    """Source별 파이 차트"""
    pie_data = source_agg[['source', column]].copy()
    pie_data = pie_data[pie_data[column] > 0]
    if len(pie_data) > 0:
        pie = alt.Chart(pie_data).mark_arc(innerRadius=0).encode(
            theta=alt.Theta(f'{column}:Q', stack=True),
            color=alt.Color('source:N', scale=alt.Scale(scheme='category10'), legend=alt.Legend(title='Source')),
            tooltip=[
                alt.Tooltip('source:N', title='Source'),
                alt.Tooltip(f'{column}:Q', title=title, format=',.0f')
            ]
        ).properties(title=title, height=250)
        st.altair_chart(pie, use_container_width=True)

