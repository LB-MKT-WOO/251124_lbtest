# Performance Dashboard

성과 대시보드 애플리케이션

## 🚀 빠른 시작

### 로컬 실행

```bash
streamlit run performance_dashboard/main.py
```

### 설치

```bash
pip install -r requirements.txt
```

## 📁 프로젝트 구조

```
performance_dashboard/
├── main.py              # 메인 진입점
├── app.py               # 대시보드 로직
├── config.py            # 설정 파일
├── data/                # 데이터 로딩 및 전처리
├── sections/            # 대시보드 섹션들
│   ├── kpi.py
│   ├── trend.py
│   ├── funnel.py
│   ├── segment.py
│   └── product.py
├── ui/                  # UI 컴포넌트
├── utils/               # 유틸리티 함수
└── requirements.txt     # 패키지 의존성
```

## ⚙️ 설정

### Google Sheets 설정

`config.py`에서 다음 설정을 확인하세요:

- `SHEET_URL`: Google Sheets URL
- `SHEET_NAME`: 시트 이름
- `CREDENTIALS_FILE`: 인증 파일 경로

### Product 날짜 설정

`configs/product_dates.json` 파일을 확인하세요.

## 📦 배포

배포 가이드는 [DEPLOYMENT.md](./DEPLOYMENT.md)를 참조하세요.

## 🔧 개발

### 주요 기능

- KPI Board: 주요 지표 대시보드
- Trend Analysis: 추이 분석
- Funnel Analysis: 퍼널 분석
- Segment Comparison: 세그먼트별 비교
- Product Analysis: 건물별 전환 데이터 분석

## 📝 라이선스

내부 사용

