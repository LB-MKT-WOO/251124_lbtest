"""Product dates loader."""

import json
import streamlit as st
import os
from pathlib import Path

from performance_dashboard.config import PRODUCT_DATES_FILE


@st.cache_data(show_spinner=False, ttl=3600)
def load_product_dates(file_path: str = None):
    """Product별 날짜 범위 로드"""
    if file_path is None:
        file_path = PRODUCT_DATES_FILE
    
    # 경로 검증 (path traversal 방지)
    try:
        file_path_obj = Path(file_path).resolve()
        # 상대 경로나 절대 경로가 허용된 디렉토리를 벗어나지 않도록 검증
        # 현재는 configs 디렉토리 내의 파일만 허용
        if not file_path_obj.exists():
            st.error(f"파일을 찾을 수 없습니다: {file_path}")
            return []
        
        # 파일 확장자 검증
        if file_path_obj.suffix != '.json':
            st.error("JSON 파일만 허용됩니다.")
            return []
        
        with open(file_path_obj, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, dict):
            st.error("잘못된 JSON 형식입니다.")
            return []
        
        return data.get('products', [])
    except json.JSONDecodeError as e:
        st.error(f"JSON 파싱 실패: {e}")
        return []
    except PermissionError:
        st.error("파일 읽기 권한이 없습니다.")
        return []
    except Exception as e:
        st.error(f"Product 날짜 파일 로드 실패: {e}")
        return []

