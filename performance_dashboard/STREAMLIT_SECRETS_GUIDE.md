# Streamlit Secrets 설정 가이드

## 🔐 Google Sheets 인증 설정

Streamlit Cloud에서 배포할 때는 Secrets를 사용하여 Google Service Account 인증 정보를 제공해야 합니다.

## 설정 방법

### 1. Streamlit Cloud에서 Secrets 설정

1. Streamlit Cloud 대시보드에서 앱 선택
2. "Settings" → "Secrets" 클릭
3. 다음 형식으로 Secrets 추가:

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

### 2. Google Service Account JSON 파일에서 정보 추출

1. Google Cloud Console에서 Service Account JSON 파일 다운로드
2. JSON 파일의 내용을 위 형식에 맞게 Secrets에 입력
3. `private_key`의 경우 `\n`을 실제 줄바꿈으로 변환해야 함

### 3. Secrets 파일 예시

로컬 테스트를 위해 `.streamlit/secrets.toml` 파일을 만들 수도 있습니다:

```toml
[google_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----"""
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

**주의**: `.streamlit/secrets.toml` 파일은 절대 Git에 커밋하지 마세요!

## 🔒 보안 주의사항

- Secrets는 절대 코드에 하드코딩하지 마세요
- `.streamlit/secrets.toml`은 `.gitignore`에 추가되어 있어야 합니다
- Streamlit Cloud의 Secrets는 암호화되어 저장됩니다

## ✅ 확인 방법

Secrets가 제대로 설정되었는지 확인하려면:

```python
import streamlit as st

if 'google_credentials' in st.secrets:
    st.success("✅ Secrets 설정 완료")
else:
    st.error("❌ Secrets 설정 필요")
```

