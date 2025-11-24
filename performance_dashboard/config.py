"""Configuration constants for the performance dashboard."""

import os
from pathlib import Path

# Google Sheets configuration
# 환경 변수에서 읽거나 기본값 사용 (배포 시 환경 변수로 설정)
SHEET_URL = os.getenv(
    "GOOGLE_SHEET_URL",
    "https://docs.google.com/spreadsheets/d/13cgCbIF_R4ubaNyIKdW0YY3VUZM0TUozRR3GyZ6vl8A/edit?gid=965675010"
)
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME", "raw(META,UAC,Twitter)")

# 인증 파일 경로 (로컬 환경용, 배포 환경에서는 Streamlit Secrets 사용)
# Streamlit Cloud에서는 Secrets를 사용하므로 파일 경로는 None이어도 됨
# 환경 변수로 경로 지정 가능
_creds_path_env = os.getenv("GOOGLE_CREDENTIALS_FILE")
if _creds_path_env and os.path.exists(_creds_path_env):
    CREDENTIALS_FILE = _creds_path_env
else:
    # 기본 경로는 로컬 개발용 (파일이 존재할 때만 사용)
    _default_creds_path = os.path.join(
        os.path.expanduser('~'), 
        'access_file', 
        'python-project-389308-bccaee8d3d37.json'
    )
    CREDENTIALS_FILE = _default_creds_path if os.path.exists(_default_creds_path) else None

# Data schema
DIMENSIONS = ["source", "campaign_name", "creative_name", "sub_campaign_name"]
DATE_COL = "Date"
METRICS = [
    "impressions", "clicks", "installs", "cost",
    "create_account_7d", "deposit_1d", "deposit_30d",
    "initial_offering_30d", "integration_account_7d", "signup_7d",
    "trade_buy_1d", "trade_buy_7d",
    "deposit_revenue_1d", "deposit_revenue_30d", "initial_offering_revenue_30d"
]
REQUIRED_COLS = [DATE_COL] + DIMENSIONS + METRICS

# Product dates file
# 배포 시 경로 문제를 방지하기 위해 여러 경로를 시도
# 1. 환경 변수로 지정된 경로
# 2. 현재 파일 기준 상위 디렉토리의 configs 폴더
# 3. 현재 작업 디렉토리의 configs 폴더
_product_dates_env = os.getenv("PRODUCT_DATES_FILE")
if _product_dates_env and os.path.exists(_product_dates_env):
    PRODUCT_DATES_FILE = _product_dates_env
else:
    # 현재 파일 위치 기준으로 상위 디렉토리의 configs 폴더 찾기
    _config_dir = Path(__file__).parent.parent / "configs"
    _product_dates_path = _config_dir / "product_dates.json"
    
    if _product_dates_path.exists():
        PRODUCT_DATES_FILE = str(_product_dates_path)
    else:
        # 현재 작업 디렉토리 기준으로 시도
        _cwd_config = Path("configs") / "product_dates.json"
        if _cwd_config.exists():
            PRODUCT_DATES_FILE = str(_cwd_config.resolve())
        else:
            # 기본값 (상대 경로, 배포 시 주의 필요)
            PRODUCT_DATES_FILE = os.path.join("configs", "product_dates.json")

