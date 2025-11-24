# 빠른 인증 설정 가이드 (Quick Setup)

## 🚀 5분 안에 설정하기

### 1️⃣ Google Cloud Console 설정 (2분)

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택 또는 생성
3. **API 및 서비스** → **라이브러리**에서 다음 API 활성화:
   - ✅ Google Sheets API
   - ✅ Google Drive API
4. **API 및 서비스** → **사용자 인증 정보** → **+ 사용자 인증 정보 만들기** → **서비스 계정**
5. 서비스 계정 이름 입력 (예: `dashboard-reader`) → **만들기**
6. **키** 탭 → **키 추가** → **새 키 만들기** → **JSON** 선택 → **만들기**
7. 다운로드된 JSON 파일 저장 ⚠️ **안전하게 보관!**

### 2️⃣ Google Sheets 권한 부여 (1분)

1. 접근할 Google Sheets 열기
2. **공유** 버튼 클릭
3. JSON 파일의 `client_email` 값 입력 (예: `dashboard-reader@project.iam.gserviceaccount.com`)
4. 권한: **뷰어** 선택
5. **알림 보내기** 체크 해제
6. **공유** 클릭

### 3️⃣ 인증 정보 설정 (2분)

#### 옵션 A: Streamlit Cloud (배포용)

1. Streamlit Cloud → 앱 선택 → **Settings** → **Secrets**
2. JSON 파일 내용을 TOML 형식으로 변환하여 입력:

```toml
[google_credentials]
type = "service_account"
project_id = "복사"
private_key_id = "복사"
private_key = """-----BEGIN PRIVATE KEY-----
(여러 줄의 키 내용 복사)
-----END PRIVATE KEY-----"""
client_email = "복사"
client_id = "복사"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "복사"
```

#### 옵션 B: 로컬 개발용

1. JSON 파일을 안전한 위치에 저장 (예: `~/access_file/credentials.json`)
2. 환경 변수 설정:
   ```bash
   export GOOGLE_CREDENTIALS_FILE=~/access_file/credentials.json
   ```

또는 `.streamlit/secrets.toml` 파일 생성 (위와 동일한 형식)

### ✅ 완료!

대시보드를 실행하면 자동으로 인증됩니다.

```bash
streamlit run performance_dashboard/main.py
```

---

## 🔍 JSON 파일에서 필요한 값 찾기

다운로드한 JSON 파일을 열면 다음과 같은 구조입니다:

```json
{
  "type": "service_account",
  "project_id": "your-project-12345",           ← 이것
  "private_key_id": "abc123...",                  ← 이것
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",  ← 이것 (전체)
  "client_email": "dashboard-reader@project.iam.gserviceaccount.com",  ← 이것
  "client_id": "123456789",                      ← 이것
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."  ← 이것
}
```

각 값을 Streamlit Secrets에 복사하세요.

---

## ⚠️ 자주 발생하는 오류

### "인증 정보를 찾을 수 없습니다"
→ Streamlit Secrets에 `[google_credentials]` 섹션이 있는지 확인

### "스프레드시트를 찾을 수 없습니다"
→ Google Sheets에서 Service Account 이메일로 공유 권한 부여했는지 확인

### "API 오류: 403"
→ Google Cloud Console에서 Google Sheets API와 Drive API가 활성화되었는지 확인

---

더 자세한 내용은 [AUTHENTICATION_GUIDE.md](./AUTHENTICATION_GUIDE.md)를 참조하세요.

