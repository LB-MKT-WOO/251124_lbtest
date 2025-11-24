# 배포 체크리스트 (Deployment Checklist)

## 📋 파일 의존성 확인

### ✅ 필수 파일 존재 확인

다음 파일들이 모두 존재하는지 확인하세요:

#### 핵심 파일
- [ ] `performance_dashboard/__init__.py`
- [ ] `performance_dashboard/__main__.py`
- [ ] `performance_dashboard/main.py` - 메인 진입점
- [ ] `performance_dashboard/app.py` - 대시보드 로직
- [ ] `performance_dashboard/config.py` - 설정 파일
- [ ] `performance_dashboard/requirements.txt` - 패키지 의존성

#### 데이터 모듈
- [ ] `performance_dashboard/data/__init__.py`
- [ ] `performance_dashboard/data/gspread_reader.py` - **Google Sheets 읽기 (필수)**
- [ ] `performance_dashboard/data/loader.py` - gspread_reader를 import
- [ ] `performance_dashboard/data/preprocessor.py`
- [ ] `performance_dashboard/data/product_loader.py`

#### 섹션 모듈
- [ ] `performance_dashboard/sections/__init__.py`
- [ ] `performance_dashboard/sections/kpi.py`
- [ ] `performance_dashboard/sections/trend.py`
- [ ] `performance_dashboard/sections/funnel.py`
- [ ] `performance_dashboard/sections/segment.py`
- [ ] `performance_dashboard/sections/product.py`

#### UI 모듈
- [ ] `performance_dashboard/ui/__init__.py`
- [ ] `performance_dashboard/ui/components.py`
- [ ] `performance_dashboard/ui/sidebar.py`

#### 유틸리티 모듈
- [ ] `performance_dashboard/utils/__init__.py`
- [ ] `performance_dashboard/utils/helpers.py`

#### 설정 파일
- [ ] `configs/product_dates.json` - **상위 디렉토리에 있어야 함**

### 🔗 Import 체인 확인

다음 import 경로가 모두 올바른지 확인:

```
main.py
  └─> app.py
       ├─> config.py
       ├─> data/loader.py
       │    └─> data/gspread_reader.py ✅ (필수)
       ├─> data/preprocessor.py
       ├─> ui/sidebar.py
       ├─> sections/kpi.py
       ├─> sections/trend.py
       ├─> sections/funnel.py
       ├─> sections/segment.py
       └─> sections/product.py
            └─> data/product_loader.py
                 └─> config.py (PRODUCT_DATES_FILE)
```

### 📁 경로 문제 확인

#### 1. `configs/product_dates.json` 경로

이 파일은 상위 디렉토리에 있어야 합니다:
```
module/
├── configs/
│   └── product_dates.json  ← 여기에 있어야 함
└── performance_dashboard/
    └── config.py  ← 이 파일에서 참조
```

**해결 방법:**
- `configs` 폴더를 루트 디렉토리에 포함시키거나
- 환경 변수 `PRODUCT_DATES_FILE`로 절대 경로 지정

#### 2. `main.py`의 경로 처리

`main.py`는 부모 디렉토리를 sys.path에 추가합니다. 배포 시에도 정상 작동하는지 확인하세요.

### 🧪 배포 전 테스트

#### 1. Import 테스트

```python
# Python에서 직접 테스트
python -c "from performance_dashboard.app import run_dashboard; print('✅ Import 성공')"
```

#### 2. 파일 존재 확인 스크립트

```python
import os
from pathlib import Path

required_files = [
    "performance_dashboard/__init__.py",
    "performance_dashboard/main.py",
    "performance_dashboard/app.py",
    "performance_dashboard/config.py",
    "performance_dashboard/data/gspread_reader.py",
    "performance_dashboard/data/loader.py",
    "performance_dashboard/data/preprocessor.py",
    "performance_dashboard/data/product_loader.py",
    "performance_dashboard/utils/helpers.py",
    "configs/product_dates.json",
]

missing = []
for file in required_files:
    if not Path(file).exists():
        missing.append(file)

if missing:
    print("❌ 누락된 파일:")
    for f in missing:
        print(f"  - {f}")
else:
    print("✅ 모든 필수 파일 존재")
```

#### 3. Streamlit 실행 테스트

```bash
streamlit run performance_dashboard/main.py
```

실행 시 다음 오류가 없는지 확인:
- `ModuleNotFoundError`
- `FileNotFoundError`
- `ImportError`

### ⚠️ 주의사항

1. **`gspread_reader.py`는 필수입니다**
   - 이 파일이 없으면 데이터를 로드할 수 없습니다
   - `data/loader.py`가 이 파일을 import합니다

2. **`configs/product_dates.json` 경로**
   - 상대 경로이므로 배포 시 현재 작업 디렉토리에 따라 달라질 수 있습니다
   - 환경 변수 `PRODUCT_DATES_FILE`로 절대 경로 지정 권장

3. **모든 `__init__.py` 파일 필요**
   - Python 패키지로 인식되려면 각 디렉토리에 `__init__.py`가 필요합니다

### 🔧 문제 해결

#### ImportError 발생 시

1. **`ModuleNotFoundError: No module named 'performance_dashboard'`**
   - 루트 디렉토리에서 실행했는지 확인
   - `main.py`의 경로 처리 로직 확인

2. **`FileNotFoundError: configs/product_dates.json`**
   - `configs` 폴더가 루트에 있는지 확인
   - 환경 변수 `PRODUCT_DATES_FILE` 설정

3. **`ImportError: cannot import name 'read_google_sheet_to_df'`**
   - `data/gspread_reader.py` 파일 존재 확인
   - 파일 내용에 함수가 정의되어 있는지 확인

### 📦 GitHub 배포 시 포함할 파일

다음 파일들이 모두 포함되어야 합니다:

```
.gitignore
requirements.txt
configs/
  └── product_dates.json
performance_dashboard/
  ├── __init__.py
  ├── __main__.py
  ├── main.py
  ├── app.py
  ├── config.py
  ├── requirements.txt
  ├── data/
  │   ├── __init__.py
  │   ├── gspread_reader.py  ← 필수
  │   ├── loader.py
  │   ├── preprocessor.py
  │   └── product_loader.py
  ├── sections/
  │   ├── __init__.py
  │   ├── kpi.py
  │   ├── trend.py
  │   ├── funnel.py
  │   ├── segment.py
  │   └── product.py
  ├── ui/
  │   ├── __init__.py
  │   ├── components.py
  │   └── sidebar.py
  └── utils/
      ├── __init__.py
      └── helpers.py
```

### ✅ 최종 확인

배포 전 다음을 확인하세요:

- [ ] 모든 필수 파일이 존재함
- [ ] 모든 `__init__.py` 파일이 존재함
- [ ] `gspread_reader.py` 파일이 존재함
- [ ] `configs/product_dates.json` 경로가 올바름
- [ ] Import 테스트 통과
- [ ] Streamlit 실행 테스트 통과
- [ ] `.gitignore`에 민감 정보 제외 설정됨

