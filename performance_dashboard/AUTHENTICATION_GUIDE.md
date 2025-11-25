# 인증 및 권한 부여 가이드 (Authentication & Authorization Guide)

## 📋 개요

이 대시보드는 Google Sheets에서 데이터를 읽기 위해 **Google Service Account**를 사용합니다. 
Service Account는 애플리케이션이 Google API에 접근할 수 있도록 하는 특별한 계정입니다.

## 🔐 인증 방법

### 방법 1: Streamlit Secrets (배포 환경 권장)

Streamlit Cloud나 배포 환경에서는 **Secrets**를 사용하는 것이 가장 안전합니다.

### 방법 2: JSON 파일 (로컬 개발용)

로컬 개발 환경에서는 JSON 인증 파일을 사용할 수 있습니다.

---

## 📝 단계별 설정 가이드

### 1단계: Google Cloud Console에서 Service Account 생성

#### 1.1 프로젝트 선택 또는 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 상단에서 프로젝트 선택 또는 새 프로젝트 생성
   - 프로젝트 이름: 예) `performance-dashboard`

#### 1.2 API 활성화

1. 좌측 메뉴에서 **"API 및 서비스"** → **"라이브러리"** 클릭
2. 다음 API를 검색하고 활성화:
   - **Google Sheets API** ✅
   - **Google Drive API** ✅

#### 1.3 Service Account 생성

1. **"API 및 서비스"** → **"사용자 인증 정보"** 클릭
2. 상단 **"+ 사용자 인증 정보 만들기"** → **"서비스 계정"** 선택
3. 서비스 계정 정보 입력:
   - **서비스 계정 이름**: `performance-dashboard-reader`
   - **서비스 계정 ID**: 자동 생성 (예: `performance-dashboard-reader@your-project.iam.gserviceaccount.com`)
   - **설명**: (선택사항) "Performance Dashboard용 Google Sheets 읽기 전용 계정"
4. **"만들기"** 클릭

#### 1.4 역할 부여 (선택사항)

1. 역할 선택 화면에서 **"건너뛰기"** 클릭 (나중에 수정 가능)
2. **"완료"** 클릭

#### 1.5 키(JSON) 생성

1. 생성된 서비스 계정을 클릭
2. **"키"** 탭 클릭
3. **"키 추가"** → **"새 키 만들기"** 선택
4. 키 유형: **JSON** 선택
5. **"만들기"** 클릭
6. JSON 파일이 자동으로 다운로드됩니다 ⚠️ **이 파일을 안전하게 보관하세요!**

---

### 2단계: Google Sheets에 권한 부여

Service Account가 Google Sheets에 접근하려면 **스프레드시트에 직접 공유 권한을 부여**해야 합니다.

#### 2.1 Service Account 이메일 주소 확인

다운로드한 JSON 파일을 열어 `client_email` 값을 확인하세요:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "performance-dashboard-reader@your-project.iam.gserviceaccount.com",  ← 이 값
  ...
}
```

또는 Google Cloud Console에서:
1. 서비스 계정 목록에서 계정 클릭
2. **"세부정보"** 탭에서 이메일 주소 확인

#### 2.2 Google Sheets에 공유 권한 부여

1. 접근하려는 Google Sheets 열기
2. 우측 상단 **"공유"** 버튼 클릭
3. **"사용자 및 그룹 추가"** 입력란에 Service Account 이메일 주소 입력:
   ```
   performance-dashboard-reader@your-project.iam.gserviceaccount.com
   ```
4. 권한: **"뷰어"** 선택 (읽기 전용)
5. **"알림 보내기"** 체크 해제 (Service Account는 이메일을 받지 않음)
6. **"공유"** 클릭

✅ **완료!** 이제 Service Account가 해당 스프레드시트를 읽을 수 있습니다.

---

### 3단계: 인증 정보 설정

#### 방법 A: Streamlit Secrets (배포 환경)

##### Streamlit Cloud에서 설정

1. Streamlit Cloud 대시보드 접속
2. 앱 선택 → **"Settings"** → **"Secrets"** 클릭
3. 다음 형식으로 Secrets 추가:

```toml
[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
client_email = "performance-dashboard-reader@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/performance-dashboard-reader%40your-project.iam.gserviceaccount.com"
```

**JSON 파일에서 값 추출 방법:**

1. 다운로드한 JSON 파일 열기
2. 각 필드를 위 형식에 맞게 복사:
   - `project_id` → `project_id`
   - `private_key_id` → `private_key_id`
   - `private_key` → `private_key` (전체 키, `\n` 포함)
   - `client_email` → `client_email`
   - `client_id` → `client_id`
   - 나머지 필드도 동일하게 복사

**중요:** `private_key`는 여러 줄이므로 `\n`을 실제 줄바꿈으로 변환하거나, TOML의 `"""` 형식 사용:

```toml
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
(여러 줄의 키 내용)
...
-----END PRIVATE KEY-----"""
```

##### 로컬 테스트용 Secrets 파일

로컬에서 테스트하려면 `.streamlit/secrets.toml` 파일 생성:

```bash
mkdir -p .streamlit
```

`.streamlit/secrets.toml` 파일 생성:

```toml
[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----"""
client_email = "performance-dashboard-reader@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/performance-dashboard-reader%40your-project.iam.gserviceaccount.com"
```

⚠️ **주의:** `.streamlit/secrets.toml`은 `.gitignore`에 포함되어 있어야 합니다!

#### 방법 B: JSON 파일 (로컬 개발용)

1. 다운로드한 JSON 파일을 안전한 위치에 저장:
   ```
   ~/access_file/python-project-389308-bccaee8d3d37.json
   ```
   또는 원하는 경로에 저장

2. 환경 변수로 경로 지정 (선택사항):
   ```bash
   export GOOGLE_CREDENTIALS_FILE=/path/to/your/credentials.json
   ```

3. 또는 `config.py`의 기본 경로에 파일 배치

---

## ✅ 인증 확인

### 방법 1: 코드로 확인

대시보드 실행 시 로그에서 확인:

```
✅ Streamlit Secrets에서 인증 정보 로드 성공
또는
✅ 파일 경로에서 인증 정보 로드 성공
```

### 방법 2: 테스트 스크립트

```python
import streamlit as st
from performance_dashboard.data.gspread_reader import read_google_sheet_to_df
from performance_dashboard.config import SHEET_URL, SHEET_NAME, CREDENTIALS_FILE

# 인증 테스트
df = read_google_sheet_to_df(SHEET_URL, SHEET_NAME, CREDENTIALS_FILE)
if df is not None:
    st.success(f"✅ 인증 성공! 데이터 {len(df)}행 로드됨")
else:
    st.error("❌ 인증 실패 또는 권한 없음")
```

---

## 🔒 권한 요약

### 필요한 권한

1. **Google Sheets API** - 활성화 필요
2. **Google Drive API** - 활성화 필요
3. **스프레드시트 공유 권한** - "뷰어" 권한 부여

### 권한 범위 (Scope)

코드에서 사용하는 권한 범위:

```python
scope = [
    'https://spreadsheets.google.com/feeds',  # Google Sheets 읽기
    'https://www.googleapis.com/auth/drive'   # Google Drive 접근
]
```

이 범위는 **읽기 전용**입니다. 데이터를 수정하거나 삭제할 수 없습니다.

---

## 🚨 문제 해결

### 문제 1: "인증 정보를 찾을 수 없습니다"

**원인:**
- Streamlit Secrets에 `google_credentials` 키가 없음
- JSON 파일 경로가 잘못됨

**해결:**
1. Streamlit Secrets 확인
2. JSON 파일 경로 확인
3. 환경 변수 `GOOGLE_CREDENTIALS_FILE` 설정 확인

### 문제 2: "스프레드시트를 찾을 수 없습니다"

**원인:**
- Service Account에 스프레드시트 공유 권한이 없음
- 스프레드시트 URL이 잘못됨

**해결:**
1. Google Sheets에서 Service Account 이메일로 공유 권한 부여
2. `SHEET_URL` 확인

### 문제 3: "API 오류: 403 Forbidden"

**원인:**
- Google Sheets API 또는 Drive API가 활성화되지 않음
- Service Account에 권한이 없음

**해결:**
1. Google Cloud Console에서 API 활성화 확인
2. 스프레드시트 공유 권한 확인

### 문제 4: "시트를 찾을 수 없습니다"

**원인:**
- `SHEET_NAME`이 실제 시트 이름과 일치하지 않음

**해결:**
1. Google Sheets에서 실제 시트 이름 확인
2. `config.py`의 `SHEET_NAME` 수정

---

## 📚 참고 자료

- [Google Service Account 문서](https://cloud.google.com/iam/docs/service-accounts)
- [Google Sheets API 문서](https://developers.google.com/sheets/api)
- [Streamlit Secrets 문서](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

---

## ✅ 체크리스트

배포 전 다음을 확인하세요:

- [ ] Google Cloud Console에서 프로젝트 생성
- [ ] Google Sheets API 활성화
- [ ] Google Drive API 활성화
- [ ] Service Account 생성
- [ ] Service Account JSON 키 다운로드
- [ ] Google Sheets에 Service Account 이메일로 공유 권한 부여
- [ ] Streamlit Secrets 설정 (배포 환경)
- [ ] 또는 JSON 파일 경로 설정 (로컬 환경)
- [ ] 인증 테스트 성공

---

## 🔐 보안 주의사항

1. **JSON 키 파일은 절대 Git에 커밋하지 마세요**
2. **`.streamlit/secrets.toml`도 Git에 커밋하지 마세요**
3. **Service Account는 최소 권한 원칙 적용** (읽기 전용)
4. **JSON 키 파일을 분실하면 즉시 삭제하고 새로 생성하세요**

