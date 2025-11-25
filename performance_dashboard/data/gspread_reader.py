"""Google Sheets reader module."""

import gspread
import gspread_dataframe as gd
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import logging
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def read_google_sheet_to_df(sheet_url, sheet_name, credentials_file=None):
    """
    Google Sheets에서 데이터를 읽어 pandas DataFrame으로 변환
    
    Args:
        sheet_url (str): Google Sheets URL
        sheet_name (str): 시트 이름
        credentials_file (str, optional): Google Service Account 인증 파일 경로
                                         None이면 Streamlit Secrets에서 읽음
    
    Returns:
        pd.DataFrame: 시트 데이터를 담은 DataFrame, 실패시 None
    """
    # 입력 검증
    if not sheet_url or not isinstance(sheet_url, str):
        logger.error("❌ 유효하지 않은 sheet_url입니다.")
        return None
    
    if not sheet_name or not isinstance(sheet_name, str):
        logger.error("❌ 유효하지 않은 sheet_name입니다.")
        return None
    
    try:
        import streamlit as st
        
        # Google Sheets API 스코프 설정
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]
        
        logger.info("🔐 Google Sheets 인증 중...")
        
        # 인증 정보 가져오기 (Secrets 우선, 파일 경로는 대체)
        credentials = None
        
        # 1. Streamlit Secrets에서 시도
        try:
            if hasattr(st, 'secrets') and 'google_credentials' in st.secrets:
                creds_dict = dict(st.secrets['google_credentials'])
                # 민감 정보는 로그에 출력하지 않음
                credentials = ServiceAccountCredentials.from_json_keyfile_dict(
                    creds_dict, scope
                )
                logger.info("✅ Streamlit Secrets에서 인증 정보 로드 성공")
        except KeyError as e:
            logger.debug(f"Streamlit Secrets에 'google_credentials' 키가 없습니다: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Streamlit Secrets에서 인증 정보 로드 실패: {str(e)}")
        
        # 2. 파일 경로에서 시도 (Secrets가 없거나 실패한 경우)
        if credentials is None and credentials_file:
            try:
                creds_path = Path(credentials_file)
                if creds_path.exists() and creds_path.is_file():
                    credentials = ServiceAccountCredentials.from_json_keyfile_name(
                        str(creds_path), scope
                    )
                    logger.info("✅ 파일 경로에서 인증 정보 로드 성공")
                else:
                    logger.error(f"❌ 인증 파일을 찾을 수 없습니다: {credentials_file}")
                    return None
            except Exception as e:
                logger.error(f"❌ 인증 파일 읽기 실패: {str(e)}")
                return None
        
        # 3. 인증 정보가 없으면 오류
        if credentials is None:
            logger.error("❌ 인증 정보를 찾을 수 없습니다. Streamlit Secrets 또는 파일 경로를 확인하세요.")
            return None
        
        client = gspread.authorize(credentials)
        
        logger.info("📊 스프레드시트 열기 중...")
        # 스프레드시트 열기
        try:
            doc = client.open_by_url(sheet_url)
        except gspread.exceptions.SpreadsheetNotFound:
            logger.error(f"❌ 스프레드시트를 찾을 수 없습니다. URL을 확인하세요.")
            return None
        except gspread.exceptions.APIError as e:
            logger.error(f"❌ Google Sheets API 오류: {str(e)}")
            return None
        
        logger.info(f"📋 시트 '{sheet_name}' 찾는 중...")
        # 시트 찾기
        sheet = None
        try:
            for worksheet in doc.worksheets():
                if worksheet.title == sheet_name:
                    sheet = worksheet
                    break
        except Exception as e:
            logger.error(f"❌ 시트 목록 조회 실패: {str(e)}")
            return None
        
        if sheet is None:
            try:
                available_sheets = [ws.title for ws in doc.worksheets()]
                logger.error(f"❌ 시트 '{sheet_name}'을 찾을 수 없습니다.")
                logger.error(f"사용 가능한 시트: {available_sheets}")
            except Exception:
                logger.error(f"❌ 시트 '{sheet_name}'을 찾을 수 없습니다.")
            return None
        
        logger.info("📖 데이터 읽기 중...")
        # 모든 데이터 읽기
        try:
            data = sheet.get_all_records()
        except Exception as e:
            logger.error(f"❌ 데이터 읽기 실패: {str(e)}")
            return None
        
        if not data:
            logger.warning("⚠️ 시트에 데이터가 없습니다.")
            return pd.DataFrame()
        
        # DataFrame으로 변환
        try:
            df = pd.DataFrame(data)
        except Exception as e:
            logger.error(f"❌ DataFrame 변환 실패: {str(e)}")
            return None
        
        logger.info(f"✅ 데이터 읽기 완료: {len(df)} 행, {len(df.columns)} 열")
        logger.debug(f"📊 컬럼: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Google Sheets 읽기 실패: {str(e)}")
        import traceback
        logger.debug(traceback.format_exc())
        return None

