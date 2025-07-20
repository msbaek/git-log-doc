# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 개요

Git Doc Gen은 Git 커밋 히스토리를 시각적인 마크다운 문서로 변환하는 Python 기반 CLI 도구입니다. GitHub 스타일의 side-by-side diff 이미지를 생성하여 코드 변경사항을 시각화합니다.

## 개발 환경 설정

### 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 의존성 설치
```bash
pip install -r requirements.txt
```

### 개발 모드 설치
```bash
pip install -e .
```

## 주요 개발 명령어

### 패키지 실행
```bash
# 로컬 저장소 분석
git-doc-gen --local . --branch main

# GitHub 저장소 분석
git-doc-gen --url "https://github.com/user/repo/tree/branch"

# 특정 커밋 리스트 분석
git-doc-gen --commits commit-list.txt

# 상세 로그 활성화
git-doc-gen --local . --verbose
```

### 패키지 빌드
```bash
# 배포용 패키지 빌드
python setup.py sdist bdist_wheel
```

## 프로젝트 구조

### 핵심 모듈
- `src/cli.py`: CLI 진입점 및 명령어 처리
- `src/git_handler.py`: Git 저장소 작업 처리 (GitHub/로컬)
- `src/commit_processor.py`: 커밋 데이터 처리 및 필터링
- `src/diff_visualizer.py`: GitHub 스타일 diff 이미지 생성
- `src/markdown_generator.py`: 마크다운 문서 생성
- `src/progress_reporter.py`: Rich 라이브러리 기반 진행상황 표시

### 유틸리티
- `src/utils/logger.py`: 로깅 설정 및 관리
- `src/utils/errors.py`: 커스텀 예외 클래스

### 출력 구조
```
output/
├── commit-history.md    # 생성된 메인 문서
└── images/             # diff 시각화 이미지
    └── 001-hash.png
```

## 아키텍처 특징

### 모듈화된 설계
각 모듈은 독립적인 책임을 가지며, 의존성 주입을 통해 결합됩니다:
- GitHandler: 저장소 접근 추상화 (GitHub API/로컬 Git)
- CommitProcessor: 커밋 필터링 및 데이터 변환
- DiffVisualizer: matplotlib 기반 이미지 렌더링
- MarkdownGenerator: 템플릿 기반 문서 생성

### GitHub 저장소 처리
- URL 파싱으로 owner/repo/branch 추출
- 임시 디렉토리에 자동 클론
- 브랜치별 고유 커밋 필터링 지원

### 한글 폰트 처리
시스템별 자동 폰트 감지:
- macOS: AppleGothic
- Windows: Malgun Gothic  
- Linux: DejaVu Sans (fallback)

### 에러 처리
- 커스텀 예외 계층구조 (GitDocGenError 기반)
- 상세 로깅 및 사용자 친화적 에러 메시지
- 개별 커밋 실패 시 전체 프로세스 계속 진행

## 주요 CLI 옵션

- `--url`: GitHub 저장소 URL
- `--local`: 로컬 저장소 경로
- `--branch`: 분석할 브랜치 (기본: main)
- `--commits`: 커밋 해시 리스트 파일
- `--output`: 출력 디렉토리 (기본: ./output)
- `--max-files`: 커밋당 최대 파일 수 (기본: 10)
- `--exclude-patterns`: 제외 패턴 (예: "*.lock,node_modules/*")
- `--all-commits`: 브랜치 전체 커밋 포함
- `--verbose`: 상세 로깅 활성화

## 개발 시 주의사항

1. **의존성**: matplotlib 백엔드는 환경에 따라 설정 필요 (헤드리스 환경: `export MPLBACKEND=Agg`)
2. **메모리**: 대규모 diff의 경우 이미지 생성 시 메모리 사용량 고려
3. **GitHub API**: Rate limit 고려 (필요시 GITHUB_TOKEN 환경변수 설정)
4. **로그 파일**: `git-doc-gen.log`에 상세 로그 기록됨