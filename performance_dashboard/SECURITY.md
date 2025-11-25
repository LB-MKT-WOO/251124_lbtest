# 보안 가이드 (Security Guide)

## 🔒 보안 체크리스트

### ✅ 완료된 보안 조치

1. **민감 정보 관리**
   - ✅ Google Sheets 인증 정보는 Streamlit Secrets 사용
   - ✅ 로컬 개발용 인증 파일 경로는 환경 변수로 설정 가능
   - ✅ `.gitignore`에 모든 민감 정보 파일 제외 설정

2. **입력 검증**
   - ✅ `gspread_reader.py`에 URL 및 시트 이름 검증 추가
   - ✅ `product_loader.py`에 파일 경로 검증 및 path traversal 방지
   - ✅ JSON 파일 형식 검증 추가

3. **에러 처리**
   - ✅ 민감 정보가 로그에 출력되지 않도록 처리
   - ✅ 상세한 에러 메시지는 debug 레벨로만 출력
   - ✅ 사용자에게는 일반적인 에러 메시지만 표시

4. **의존성 관리**
   - ✅ `requirements.txt`에 버전 범위 지정으로 보안 업데이트 가능
   - ✅ 주요 패키지 버전 고정

### 📋 배포 전 확인 사항

#### 1. 환경 변수 설정

다음 환경 변수를 설정하거나 Streamlit Secrets를 사용하세요:

```bash
# 선택사항 (기본값이 있음)
GOOGLE_SHEET_URL=<your-sheet-url>
GOOGLE_SHEET_NAME=<your-sheet-name>
GOOGLE_CREDENTIALS_FILE=<path-to-credentials-file>
```

#### 2. Streamlit Secrets 설정

Streamlit Cloud 배포 시 `.streamlit/secrets.toml` 또는 Streamlit Cloud Secrets에 다음을 추가:

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

#### 3. 파일 권한 확인

- 인증 파일은 읽기 전용 권한으로 설정
- `.streamlit/secrets.toml`은 600 권한 권장

#### 4. Git 커밋 전 확인

다음 파일들이 `.gitignore`에 포함되어 있는지 확인:
- `*.json` (인증 파일)
- `.streamlit/secrets.toml`
- `__pycache__/`
- `.env` 파일

### 🚨 보안 주의사항

1. **절대 하드코딩하지 마세요**
   - API 키, 비밀번호, 인증 토큰은 코드에 직접 작성하지 마세요
   - 환경 변수나 Secrets 사용

2. **로그에 민감 정보 출력 금지**
   - 인증 정보, 토큰, 비밀번호는 로그에 출력하지 마세요
   - 디버그 로그에도 민감 정보 포함 금지

3. **파일 경로 검증**
   - 사용자 입력을 파일 경로로 사용할 때는 반드시 검증
   - Path traversal 공격 방지

4. **의존성 업데이트**
   - 정기적으로 `requirements.txt`의 패키지 업데이트 확인
   - 보안 취약점이 발견된 패키지는 즉시 업데이트

### 🔍 보안 점검 항목

- [ ] 모든 민감 정보가 환경 변수 또는 Secrets로 관리됨
- [ ] `.gitignore`에 민감 정보 파일이 포함됨
- [ ] 하드코딩된 비밀번호/키가 없음
- [ ] 입력 검증이 모든 사용자 입력에 적용됨
- [ ] 에러 메시지에 민감 정보가 포함되지 않음
- [ ] 파일 경로 검증이 구현됨
- [ ] 의존성 패키지가 최신 보안 패치 적용됨

### 📞 보안 이슈 발견 시

보안 취약점을 발견한 경우:
1. 즉시 해당 기능 비활성화
2. 관련 팀에 보고
3. 취약점 패치 후 재배포

