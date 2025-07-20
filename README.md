# Git Doc Gen

Git 커밋 히스토리를 시각적인 마크다운 문서로 변환하는 CLI 도구입니다. 각 커밋의 변경사항을 GitHub 스타일의 side-by-side diff 이미지로 시각화하여 개발자들이 프로젝트의 변경 내역을 쉽게 이해할 수 있도록 돕습니다.

## 개요

`git-doc-gen`은 Git 저장소의 커밋 히스토리를 분석하여 각 커밋의 변경사항을 시각적으로 표현하는 문서를 자동으로 생성합니다. 코드 리뷰, 프로젝트 문서화, 개발 과정 분석 등에 유용하게 사용할 수 있습니다.

## 주요 기능

- 🔗 GitHub URL 또는 로컬 Git 저장소 지원
- 📊 GitHub 스타일의 side-by-side diff 시각화
- 📝 구조화된 마크다운 문서 자동 생성
- 🎯 커밋 해시 리스트 파일 지원
- 🌿 브랜치별 커밋 필터링 (브랜치 고유 커밋만 추출)
- 🌍 한글 지원 (시스템 폰트 자동 감지)
- 📈 진행 상황 실시간 표시 (Rich 라이브러리 사용)
- 🛡️ 강력한 오류 처리 및 로깅
- 🎨 가독성 높은 큰 폰트 크기

## 설치

### 방법 1: pip를 통한 설치 (권장)

```bash
# PyPI에서 직접 설치 (향후 지원 예정)
# pip install git-doc-gen
```

### 방법 2: 소스코드에서 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/git-doc-gen.git
cd git-doc-gen

# 가상환경 생성 및 활성화 (권장)
python -m venv venv
source venv/bin/activate  # Windows의 경우: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 패키지 설치 (개발 모드)
pip install -e .
```

### 빠른 시작

```bash
# 설치 확인
git-doc-gen --help

# 현재 디렉토리의 Git 저장소 분석
git-doc-gen --local . 
```

## 사용법

### GitHub 저장소 분석

```bash
git-doc-gen --url "https://github.com/user/repo/tree/main"
```

### 로컬 저장소 분석

```bash
git-doc-gen --local "/path/to/repo" --branch "feature-branch"
```

### 특정 커밋 리스트 분석

```bash
# commit-list.txt 파일에 커밋 해시를 한 줄씩 작성
git-doc-gen --commits "commit-list.txt"
```

### 옵션

- `--output`: 출력 디렉토리 지정 (기본값: ./output)
- `--max-files`: 커밋당 최대 처리 파일 수 (기본값: 10)
- `--image-width`: 생성 이미지 너비 (기본값: 1200px)
- `--exclude-patterns`: 제외할 파일 패턴 (예: "*.lock,node_modules/*")
- `--all-commits`: 브랜치의 모든 커밋 포함 (기본값: 브랜치 고유 커밋만)
- `--verbose`: 상세 로깅 활성화

## 출력 구조

```
output/
├── commit-history.md    # 메인 문서
└── images/             # diff 이미지들
    ├── 001-99b27b44.png
    ├── 002-a1b2c3d4.png
    └── ...
```

### 생성되는 문서 구조
- 커밋별로 섹션 분리
- 각 커밋에 대한 메타데이터 (작성자, 날짜, 메시지)
- 변경된 파일 목록과 통계
- GitHub 스타일의 시각적 diff 이미지
- 목차 자동 생성

## 예제

### 기본 사용

```bash
# GitHub 저장소 분석
git-doc-gen --url "https://github.com/facebook/react/tree/main"

# 출력 디렉토리 지정
git-doc-gen --url "https://github.com/user/repo" --output "./docs"

# 파일 필터링
git-doc-gen --local "." --exclude-patterns "*.test.js,*.spec.ts"

# 브랜치 고유 커밋만 분석 (기본값)
git-doc-gen --url "https://github.com/user/repo/tree/feature-branch"

# 브랜치의 모든 커밋 포함
git-doc-gen --url "https://github.com/user/repo/tree/feature-branch" --all-commits
```

### 커밋 리스트 파일 형식

```text
# commit-list.txt
99b27b44e8c3c5c35275aef7bf30fd6d7789efd7
a1b2c3d4e5f6789012345678901234567890abcd
# 주석은 무시됩니다
00d700850ad0db71ac79b1f0d5117005e3f6d537
```

## 요구사항

### 시스템 요구사항
- Python 3.8 이상
- Git 2.0 이상
- 운영체제: Windows, macOS, Linux

### Python 패키지
- gitpython >= 3.1.0
- matplotlib >= 3.5.0
- Pillow >= 9.0.0
- requests >= 2.25.0
- rich >= 10.0.0
- PyYAML >= 5.4.0

### 선택사항
- 인터넷 연결 (GitHub 저장소 분석 시)
- 한글 폰트 (한글 커밋 메시지 렌더링 시)

## 시각화 특징

### GitHub 스타일 Side-by-Side Diff
- 삭제된 코드는 왼쪽에 빨간색으로 표시
- 추가된 코드는 오른쪽에 초록색으로 표시
- 라인 번호 자동 추적
- GitHub과 동일한 색상 스키마 사용

### 한글 지원
- macOS: AppleGothic 폰트 자동 사용
- Windows: Malgun Gothic 폰트 자동 사용
- Linux: DejaVu Sans 폰트 사용

## 문제 해결

### 일반적인 문제

1. **권한 오류**: 비공개 저장소의 경우 GitHub 토큰 설정 필요
   ```bash
   export GITHUB_TOKEN="your-github-token"
   git-doc-gen --url "https://github.com/private/repo"
   ```

2. **메모리 부족**: `--max-files` 옵션으로 처리 파일 수 제한
   ```bash
   git-doc-gen --local . --max-files 5
   ```

3. **이미지 생성 실패**: matplotlib 백엔드 설정
   ```bash
   export MPLBACKEND=Agg  # 헤드리스 환경에서
   ```

4. **한글 깨짐**: 시스템 폰트가 자동으로 감지되지만, 문제가 있을 경우 시스템에 한글 폰트 설치 필요
   - macOS: 기본 설치된 AppleGothic 사용
   - Windows: `Malgun Gothic` 설치 확인
   - Linux: `sudo apt-get install fonts-nanum` (Ubuntu/Debian)

### 로그 확인

```bash
# 상세 로그 활성화
git-doc-gen --url "..." --verbose

# 로그 파일 확인
cat git-doc-gen.log
```

### 디버깅 팁

1. **단일 커밋 테스트**
   ```bash
   echo "커밋해시" > test-commit.txt
   git-doc-gen --commits test-commit.txt --verbose
   ```

2. **특정 파일 제외**
   ```bash
   git-doc-gen --local . --exclude-patterns "*.log,*.tmp,dist/*"
   ```

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 라이센스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.