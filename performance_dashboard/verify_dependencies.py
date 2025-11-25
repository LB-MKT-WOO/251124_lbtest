"""배포 전 파일 의존성 검증 스크립트

이 스크립트는 배포 전에 모든 필수 파일과 import 경로가 올바른지 확인합니다.
사용법: python performance_dashboard/verify_dependencies.py
"""

import sys
import os
from pathlib import Path
from importlib import import_module
import traceback

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 색상 출력 (선택사항)
try:
    from colorama import init, Fore, Style
    init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = RESET = ""

def check_file_exists(file_path, description=""):
    """파일 존재 여부 확인"""
    path = Path(file_path)
    exists = path.exists()
    status = f"{GREEN}✅{RESET}" if exists else f"{RED}❌{RESET}"
    print(f"{status} {file_path} {description}")
    return exists

def check_import(module_name, description=""):
    """모듈 import 가능 여부 확인"""
    try:
        import_module(module_name)
        print(f"{GREEN}✅{RESET} import {module_name} {description}")
        return True
    except ImportError as e:
        print(f"{RED}❌{RESET} import {module_name} 실패: {e}")
        return False
    except Exception as e:
        print(f"{YELLOW}⚠️{RESET} import {module_name} 오류: {e}")
        return False

def main():
    """메인 검증 함수"""
    print("=" * 60)
    print("배포 전 파일 의존성 검증")
    print("=" * 60)
    print()
    
    # 현재 디렉토리 확인
    cwd = Path.cwd()
    print(f"현재 작업 디렉토리: {cwd}")
    print()
    
    # 필수 파일 목록
    required_files = [
        ("performance_dashboard/__init__.py", "패키지 초기화"),
        ("performance_dashboard/__main__.py", "모듈 실행 진입점"),
        ("performance_dashboard/main.py", "메인 진입점"),
        ("performance_dashboard/app.py", "대시보드 로직"),
        ("performance_dashboard/config.py", "설정 파일"),
        ("performance_dashboard/requirements.txt", "패키지 의존성"),
        ("performance_dashboard/data/__init__.py", "데이터 모듈 초기화"),
        ("performance_dashboard/data/gspread_reader.py", "Google Sheets 읽기 (필수)"),
        ("performance_dashboard/data/loader.py", "데이터 로더"),
        ("performance_dashboard/data/preprocessor.py", "데이터 전처리"),
        ("performance_dashboard/data/product_loader.py", "Product 로더"),
        ("performance_dashboard/sections/__init__.py", "섹션 모듈 초기화"),
        ("performance_dashboard/sections/kpi.py", "KPI 섹션"),
        ("performance_dashboard/sections/trend.py", "Trend 섹션"),
        ("performance_dashboard/sections/funnel.py", "Funnel 섹션"),
        ("performance_dashboard/sections/segment.py", "Segment 섹션"),
        ("performance_dashboard/sections/product.py", "Product 섹션"),
        ("performance_dashboard/ui/__init__.py", "UI 모듈 초기화"),
        ("performance_dashboard/ui/components.py", "UI 컴포넌트"),
        ("performance_dashboard/ui/sidebar.py", "사이드바"),
        ("performance_dashboard/utils/__init__.py", "유틸리티 모듈 초기화"),
        ("performance_dashboard/utils/helpers.py", "유틸리티 함수"),
        ("configs/product_dates.json", "Product 날짜 설정 (상위 디렉토리)"),
    ]
    
    print("📁 필수 파일 확인")
    print("-" * 60)
    file_results = []
    for file_path, description in required_files:
        exists = check_file_exists(file_path, description)
        file_results.append((file_path, exists))
    print()
    
    # Import 테스트
    print("📦 Import 경로 확인")
    print("-" * 60)
    
    # 부모 디렉토리를 path에 추가 (main.py와 동일한 로직)
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    
    import_results = []
    
    # 핵심 모듈
    import_tests = [
        ("performance_dashboard", "메인 패키지"),
        ("performance_dashboard.config", "설정 모듈"),
        ("performance_dashboard.app", "앱 모듈"),
        ("performance_dashboard.data.gspread_reader", "Google Sheets 읽기 (필수)"),
        ("performance_dashboard.data.loader", "데이터 로더"),
        ("performance_dashboard.data.preprocessor", "데이터 전처리"),
        ("performance_dashboard.data.product_loader", "Product 로더"),
        ("performance_dashboard.utils.helpers", "유틸리티 함수"),
        ("performance_dashboard.ui.sidebar", "사이드바"),
        ("performance_dashboard.ui.components", "UI 컴포넌트"),
        ("performance_dashboard.sections.kpi", "KPI 섹션"),
        ("performance_dashboard.sections.trend", "Trend 섹션"),
        ("performance_dashboard.sections.funnel", "Funnel 섹션"),
        ("performance_dashboard.sections.segment", "Segment 섹션"),
        ("performance_dashboard.sections.product", "Product 섹션"),
    ]
    
    for module_name, description in import_tests:
        success = check_import(module_name, description)
        import_results.append((module_name, success))
    print()
    
    # 함수 존재 확인
    print("🔧 핵심 함수 확인")
    print("-" * 60)
    
    function_checks = []
    
    try:
        from performance_dashboard.data.gspread_reader import read_google_sheet_to_df
        print(f"{GREEN}✅{RESET} read_google_sheet_to_df 함수 존재")
        function_checks.append(True)
    except Exception as e:
        print(f"{RED}❌{RESET} read_google_sheet_to_df 함수 없음: {e}")
        function_checks.append(False)
    
    try:
        from performance_dashboard.data.loader import load_mother_data
        print(f"{GREEN}✅{RESET} load_mother_data 함수 존재")
        function_checks.append(True)
    except Exception as e:
        print(f"{RED}❌{RESET} load_mother_data 함수 없음: {e}")
        function_checks.append(False)
    
    try:
        from performance_dashboard.app import run_dashboard
        print(f"{GREEN}✅{RESET} run_dashboard 함수 존재")
        function_checks.append(True)
    except Exception as e:
        print(f"{RED}❌{RESET} run_dashboard 함수 없음: {e}")
        function_checks.append(False)
    print()
    
    # 설정 값 확인
    print("⚙️ 설정 값 확인")
    print("-" * 60)
    
    try:
        from performance_dashboard.config import (
            SHEET_URL, SHEET_NAME, CREDENTIALS_FILE, 
            PRODUCT_DATES_FILE, DIMENSIONS, METRICS
        )
        print(f"{GREEN}✅{RESET} 설정 값 로드 성공")
        print(f"   SHEET_URL: {'설정됨' if SHEET_URL else '없음'}")
        print(f"   SHEET_NAME: {SHEET_NAME}")
        print(f"   CREDENTIALS_FILE: {'설정됨' if CREDENTIALS_FILE else '없음 (Secrets 사용)'}")
        print(f"   PRODUCT_DATES_FILE: {PRODUCT_DATES_FILE}")
        
        # PRODUCT_DATES_FILE 경로 확인
        if Path(PRODUCT_DATES_FILE).exists():
            print(f"   {GREEN}✅{RESET} PRODUCT_DATES_FILE 경로 유효")
        else:
            print(f"   {YELLOW}⚠️{RESET} PRODUCT_DATES_FILE 경로 없음: {PRODUCT_DATES_FILE}")
    except Exception as e:
        print(f"{RED}❌{RESET} 설정 값 로드 실패: {e}")
        traceback.print_exc()
    print()
    
    # 결과 요약
    print("=" * 60)
    print("검증 결과 요약")
    print("=" * 60)
    
    missing_files = [f for f, exists in file_results if not exists]
    failed_imports = [m for m, success in import_results if not success]
    failed_functions = [i for i, success in enumerate(function_checks) if not success]
    
    if not missing_files and not failed_imports and not failed_functions:
        print(f"{GREEN}✅ 모든 검증 통과! 배포 준비 완료.{RESET}")
        return 0
    else:
        print(f"{RED}❌ 일부 검증 실패:{RESET}")
        if missing_files:
            print(f"\n누락된 파일 ({len(missing_files)}개):")
            for f in missing_files:
                print(f"  - {f}")
        if failed_imports:
            print(f"\nImport 실패 ({len(failed_imports)}개):")
            for m in failed_imports:
                print(f"  - {m}")
        if failed_functions:
            print(f"\n함수 확인 실패 ({len(failed_functions)}개)")
        print(f"\n{YELLOW}⚠️ 위 문제를 해결한 후 다시 배포하세요.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

