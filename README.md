# Git Doc Gen

Git 커밋 히스토리를 시각적인 마크다운 문서로 변환하는 CLI 도구입니다. 각 커밋의 변경사항을 이미지로 시각화하여 개발자들이 프로젝트의 변경 내역을 쉽게 이해할 수 있도록 돕습니다.

## 주요 기능

- 🔗 GitHub URL 또는 로컬 Git 저장소 지원
- 📊 커밋별 변경사항을 시각적 이미지로 생성
- 📝 구조화된 마크다운 문서 자동 생성
- 🎯 커밋 해시 리스트 파일 지원
- 📈 진행 상황 실시간 표시
- 🛡️ 강력한 오류 처리 및 로깅

## 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/git-doc-gen.git
cd git-doc-gen

# 의존성 설치
pip install -r requirements.txt

# 패키지 설치
pip install -e .
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

## 예제

### 기본 사용

```bash
# GitHub 저장소 분석
git-doc-gen --url "https://github.com/facebook/react/tree/main"

# 출력 디렉토리 지정
git-doc-gen --url "https://github.com/user/repo" --output "./docs"

# 파일 필터링
git-doc-gen --local "." --exclude-patterns "*.test.js,*.spec.ts"
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

- Python 3.8 이상
- Git이 설치되어 있어야 함
- 인터넷 연결 (GitHub 저장소 분석 시)

## 문제 해결

### 일반적인 문제

1. **권한 오류**: 비공개 저장소의 경우 GitHub 토큰 설정 필요
2. **메모리 부족**: `--max-files` 옵션으로 처리 파일 수 제한
3. **이미지 생성 실패**: matplotlib 폰트 설정 확인

### 로그 확인

```bash
# 상세 로그 활성화
git-doc-gen --url "..." --verbose

# 로그 파일 확인
cat git-doc-gen.log
```

## 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 라이센스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.