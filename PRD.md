# Git Commit Documentation Generator - PRD

## 개요

Git 브랜치의 모든 커밋에 대해 시간순으로 정렬된 마크다운 문서를 생성하는 CLI
도구입니다. 각 커밋의 변경사항을 side-by-side diff 이미지로 시각화하여 다른
개발자들의 이해를 돕습니다.

## 목표

개발자들이 브랜치의 변경 히스토리를 빠르게 이해할 수 있도록 시각적이고 구조화된
문서를 자동 생성합니다.

## 기능 요구사항

### 1. 입력 처리

- **GitHub URL 지원**: `https://github.com/user/repo/tree/branch-name` 형식
- **로컬 Git 저장소**: 디렉토리 경로 입력
- **커밋 해시 리스트**: 텍스트 파일(.txt) 지원
  - 파일 형식: 한 줄에 하나의 커밋 해시
  - 예: `commit-list.txt`

### 2. 커밋 정보 수집

- 브랜치의 모든 커밋을 시간순으로 정렬
- 각 커밋에서 다음 정보 추출:
  - 커밋 해시 (짧은 형식: 8자리)
  - 커밋 메시지
  - 변경된 파일 목록
  - 파일별 diff 정보

### 3. Diff 이미지 생성

- **지원 파일 형식**: 텍스트 파일만 (_.md, _.java, _.py, _.js, _.txt, _.json,
  _.xml, _.yml, \*.yaml 등)
- **바이너리 파일**: 무시
- **이미지 생성 도구**:
  - Python: `diff2html-cli` + `wkhtmltopdf` 조합
  - 또는 `matplotlib`을 사용한 커스텀 diff 시각화
- **파일명 규칙**: `001-{8자리-커밋해시}.png`, `002-{8자리-커밋해시}.png`
- **크기 제한**: 한 커밋당 변경사항이 100줄 이상이면 주요 변경사항만 요약

### 4. 마크다운 문서 생성

- **출력 형식**:

```markdown
# Git Commit History - {브랜치명}

## {8자리-커밋해시} - {커밋메시지}

![diff](./images/001-{커밋해시}.png)

### 주요 변경사항

- {변경사항 요약}

---
```

### 5. 파일 구조

```
프로젝트-루트/
├── output/
│   ├── commit-history.md
│   └── images/
│       ├── 001-99b27b44.png
│       ├── 002-99b27b44.png
│       └── 003-00d70085.png
```

## 기술 요구사항

### 언어 및 프레임워크

- **Python 3.8+** (선호)
- **주요 라이브러리**:
  - `GitPython`: Git 작업 처리
  - `requests`: GitHub API 호출
  - `Pillow`: 이미지 처리
  - `matplotlib`: diff 시각화
  - `click`: CLI 인터페이스
  - `rich`: 콘솔 출력 개선

### CLI 인터페이스

```bash
# GitHub 저장소
git-doc-gen --url "https://github.com/user/repo/tree/main"

# 로컬 저장소
git-doc-gen --local "/path/to/repo" --branch "feature-branch"

# 커밋 해시 리스트
git-doc-gen --commits "commit-list.txt"

# 출력 디렉토리 지정
git-doc-gen --url "github-url" --output "./documentation"
```

## 성능 요구사항

- **처리 속도**: 커밋당 평균 2-3초
- **메모리 사용량**: 최대 512MB
- **파일 크기 제한**:
  - 단일 파일 diff: 최대 1000줄
  - 커밋당 총 변경: 최대 5000줄

## 오류 처리

### 예상 오류 상황

1. **네트워크 오류**: GitHub API 접근 실패
2. **권한 오류**: 비공개 저장소 접근
3. **Git 오류**: 잘못된 브랜치명 또는 커밋 해시
4. **파일 시스템 오류**: 출력 디렉토리 생성 실패

### 오류 대응

- 사용자 친화적인 오류 메시지 제공
- 진행 상황 표시 (프로그레스 바)
- 실패한 커밋 건너뛰기 옵션
- 로그 파일 생성 (`git-doc-gen.log`)

## 사용자 경험

### 진행 상황 표시

```
📁 저장소 분석 중...
🔍 커밋 수집 중... (25/50)
🖼️  이미지 생성 중... (10/25)
📝 문서 작성 중...
✅ 완료! output/commit-history.md 확인해주세요.
```

### 설정 옵션

- `--max-files`: 커밋당 최대 처리 파일 수 (기본값: 10)
- `--image-width`: 생성 이미지 너비 (기본값: 1200px)
- `--exclude-patterns`: 제외할 파일 패턴 (예: "_.lock,node_modules/_")

## 확장 가능성

### 향후 개선 사항

1. **다양한 출력 형식**: HTML, PDF 지원
2. **GitHub Integration**: GitHub Pages 자동 배포
3. **템플릿 시스템**: 커스터마이즈 가능한 문서 템플릿
4. **브랜치 비교**: 두 브랜치 간 차이점 분석
5. **통계 정보**: 코드 변경량, 기여자 정보 등

이 PRD로 개발을 진행하시겠습니까? 추가로 수정하거나 보완할 부분이 있다면
알려주세요.
