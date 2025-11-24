# 배포 가이드 (Deployment Guide)

## 📋 배포 전 확인 사항

### 1. 필수 파일 확인

#### ✅ 필수 파일 목록
- [ ] `performance_dashboard/main.py` - 메인 진입점
- [ ] `performance_dashboard/app.py` - 대시보드 로직
- [ ] `performance_dashboard/config.py` - 설정 파일
- [ ] `requirements.txt` - 패키지 의존성
- [ ] `configs/product_dates.json` - Product 날짜 정보 (상위 디렉토리)
- [ ] `performance_dashboard/data/gspread_reader.py` - Google Sheets 읽기 모듈

#### 📁 디렉토리 구조
```
performance_dashboard/
├── __init__.py
├── __main__.py
├── main.py              # ← 메인 진입점
├── app.py
├── config.py
├── requirements.txt     # ← 패키지 의존성
├── DEPLOYMENT.md        # ← 이 파일
├── data/
├── sections/
├── ui/
└── utils/
```

### 2. 환경 변수 및 설정

#### 🔐 Google Sheets 인증
- [ ] Google Service Account 인증 파일 경로 확인
- [ ] `config.py`의 `CREDENTIALS_FILE` 경로 수정 또는 환경 변수 사용
- [ ] 배포 플랫폼에 인증 파일 업로드 또는 Secrets 설정

#### 📊 Google Sheets 접근 권한
- [ ] Google Sheets URL 확인 (`SHEET_URL`)
- [ ] 시트 이름 확인 (`SHEET_NAME`)
- [ ] Service Account에 시트 읽기 권한 부여

#### 📅 Product 날짜 파일
- [ ] `configs/product_dates.json` 파일 존재 확인
- [ ] 파일 경로가 `config.py`의 `PRODUCT_DATES_FILE`과 일치하는지 확인

### 3. 의존성 패키지

#### 📦 필수 패키지 설치
```bash
pip install -r requirements.txt
```

#### ✅ 패키지 목록
- streamlit (>=1.28.0)
- pandas (>=1.5.0)
- numpy (>=1.23.0)
- altair (>=5.0.0)
- matplotlib (>=3.6.0)
- gspread (>=5.0.0)
- gspread-dataframe (>=3.3.0)
- oauth2client (>=4.1.3)

### 4. 로컬 테스트

#### 🧪 실행 테스트
```bash
streamlit run performance_dashboard/main.py
```

#### ✅ 테스트 체크리스트
- [ ] 대시보드가 정상적으로 로드되는가?
- [ ] Google Sheets 데이터가 정상적으로 로드되는가?
- [ ] 모든 섹션이 정상적으로 표시되는가?
  - [ ] KPI Board
  - [ ] Trend 섹션
  - [ ] Funnel 섹션
  - [ ] Segment Comparison
  - [ ] Product Analysis
- [ ] 필터 기능이 정상 작동하는가?
- [ ] 차트가 정상적으로 렌더링되는가?

### 5. GitHub 배포 설정

#### 🌿 Branch 설정
- **Branch**: `main` (또는 기본 브랜치)
- **Main file path**: `performance_dashboard/main.py`

#### 📝 .gitignore 확인
다음 항목이 제외되어 있는지 확인:
```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
*.json  # 인증 파일은 제외 (Secrets 사용)
```

#### 🔒 민감 정보 관리
- [ ] Google Sheets 인증 파일을 `.gitignore`에 추가
- [ ] 배포 플랫폼의 Secrets/Environment Variables 사용
- [ ] `config.py`의 하드코딩된 경로를 환경 변수로 변경 고려

### 6. Streamlit Cloud 배포

#### ⚙️ 배포 설정
1. **Repository**: GitHub 저장소 URL
2. **Branch**: `main`
3. **Main file path**: `performance_dashboard/main.py`
4. **Python version**: `3.9` 이상 권장

#### 🔐 Secrets 설정
Streamlit Cloud의 Secrets에 다음을 추가 (자세한 내용은 `STREAMLIT_SECRETS_GUIDE.md` 참조):

```toml
[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

**참고**: `STREAMLIT_SECRETS_GUIDE.md` 파일에 자세한 설정 방법이 있습니다.

### 7. 배포 후 확인

#### ✅ 배포 후 체크리스트
- [ ] 대시보드가 정상적으로 접속되는가?
- [ ] 데이터 로딩이 정상 작동하는가?
- [ ] 모든 기능이 정상 작동하는가?
- [ ] 에러 로그 확인
- [ ] 성능 확인 (로딩 속도)

## 🚀 빠른 배포 체크리스트

```
□ requirements.txt 생성 및 확인
□ configs/product_dates.json 파일 존재 확인
□ gspread_reader.py 파일 존재 확인
□ Google Sheets 인증 설정 확인
□ 로컬 테스트 완료
□ .gitignore 설정 확인
□ GitHub에 푸시 완료
□ 배포 플랫폼 설정 완료
□ 배포 후 테스트 완료
```

## 📞 문제 해결

### 일반적인 문제

1. **ModuleNotFoundError**: `requirements.txt`의 패키지가 모두 설치되었는지 확인
2. **Google Sheets 접근 오류**: 인증 파일 경로 및 권한 확인
3. **파일 경로 오류**: `configs/product_dates.json` 경로 확인
4. **Import 오류**: `performance_dashboard/data/gspread_reader.py` 파일 위치 확인

### 로그 확인
배포 플랫폼의 로그를 확인하여 구체적인 오류 메시지를 확인하세요.

## 📚 추가 리소스

- [Streamlit Cloud 문서](https://docs.streamlit.io/streamlit-community-cloud)
- [Google Sheets API 문서](https://developers.google.com/sheets/api)

