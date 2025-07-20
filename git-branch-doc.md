# Git Branch 관련 대화 정리

## 1. git log main..feature 명령어

### 기본 개념
`git log main..feature`는 feature 브랜치에만 있고 main 브랜치에는 없는 커밋들을 보여주는 명령어입니다.

### feature가 main에 이미 merge된 경우의 동작

#### 1.1 Fast-forward merge인 경우
```
main: A---B---C---D---E
                    ^
                    feature도 여기 있음
```
- `git log main..feature` → **아무것도 출력되지 않음**
- main과 feature가 같은 커밋을 가리키므로 차이가 없음

#### 1.2 일반적인 merge (merge commit 생성)인 경우
```
      C---D (feature)
     /     \
A---B-------M (main)
```
- feature가 main에 merge되면:
  - `git log main..feature` → **아무것도 출력되지 않음**
  - feature의 모든 커밋이 이미 main의 히스토리에 포함됨

#### 1.3 부분적으로 merge된 경우
```
      C---D---E---F (feature)
     /     \
A---B-------M---G (main)
```
- D까지만 merge되고 E, F는 아직 merge 안 된 경우:
  - `git log main..feature` → **E, F만 출력됨**
  - merge되지 않은 커밋만 보여줌

### 효과적인 대안

#### merge된 커밋도 보고 싶을 때
```bash
# feature 브랜치의 모든 커밋 히스토리
git log --first-parent main..feature

# merge 전 feature 브랜치에만 있었던 커밋
git log main...feature --right-only

# 특정 시점의 feature 브랜치 커밋
git log main..feature@{1.week.ago}
```

#### merge 여부와 관계없이 feature 작업 추적
```bash
# feature 브랜치에서 작업한 모든 커밋 (merge commit 제외)
git log --no-merges --author="작업자" main...feature

# merge된 feature 브랜치의 원래 커밋들
git log --merges --grep="feature" main
```

#### 실용적인 접근 방법
```bash
# 1. merge 상태 확인
git branch --merged main | grep feature

# 2. merge되기 전 커밋 찾기
git reflog show feature | grep -B1 "merge"

# 3. 특정 기간 동안의 feature 작업
git log --since="2 weeks ago" --until="merge" feature
```

## 2. git reflog 명령어 상세 설명

### Reflog란?
**Reference Log**의 줄임말로, Git이 **로컬에서** HEAD와 브랜치 참조가 어떻게 변경되었는지 기록하는 로그입니다.

### 기본 사용법
```bash
git reflog feature
# 또는
git reflog show feature  # 같은 명령
```

### 출력 형식 예시
```
e3f1c2a feature@{0}: commit: Add new feature
b4d5e6f feature@{1}: commit: Fix bug in feature
a1b2c3d feature@{2}: checkout: moving from main to feature
9f8e7d6 feature@{3}: branch: Created from main
```

각 항목의 의미:
- `e3f1c2a`: 커밋 해시
- `feature@{0}`: 현재부터 몇 번째 이전 상태인지 (0이 가장 최근)
- `commit:`: 어떤 작업이 일어났는지
- `Add new feature`: 작업 설명

### Reflog가 기록하는 주요 작업들
- 브랜치 생성: `branch: Created from main`
- 커밋: `commit: Add feature`
- 브랜치 이동: `checkout: moving from main to feature`
- 리베이스: `rebase: Add feature`
- 리셋: `reset: moving to HEAD~1`
- Merge: `merge main: Fast-forward`

### 실용적인 사용 예시

#### 실수 복구
```bash
# 실수로 reset한 경우
git reset --hard HEAD~3  # 아, 실수!

# reflog로 이전 상태 확인
git reflog feature
# e3f1c2a feature@{1}: commit: Important work  <-- 이거 복구하고 싶음

# 복구
git reset --hard feature@{1}
```

#### merge 전 상태 찾기
```bash
# feature가 main에 merge된 후, merge 전 마지막 커밋 찾기
git reflog feature | grep -B1 "merge"
```

#### 특정 시점의 브랜치 상태
```bash
# 어제의 feature 브랜치 상태
git log feature@{1.day.ago}

# 5번째 이전 상태
git log feature@{5}

# 특정 시각
git log feature@{2024-01-20.14:30:00}
```

### Reflog vs Log 차이점

| 구분 | `git log` | `git reflog` |
|------|-----------|--------------|
| 범위 | 커밋 히스토리 | 브랜치/HEAD 변경 이력 |
| 공유 | 원격 저장소와 공유됨 | 로컬에만 존재 |
| 보존 | 영구적 | 기본 90일 후 삭제 |
| 내용 | 커밋 관계 | 브랜치가 가리킨 위치들 |

### 주의사항
1. **로컬 전용**: reflog는 로컬 저장소에만 존재하며, push/pull되지 않습니다
2. **만료 기간**: 기본적으로 90일 후 자동 삭제됩니다
3. **디스크 공간**: reflog는 추가 디스크 공간을 사용합니다

## 3. Reflog를 시간순으로 정렬하기

`git reflog`는 기본적으로 **최신순(newest first)**으로 출력됩니다. 이를 **시간순(oldest first)**으로 바꾸는 방법들:

### 간단한 방법
```bash
# Linux/Mac에서 tac 사용
git reflog feature | tac

# Mac에서 tac이 없는 경우
git reflog feature | tail -r

# Windows PowerShell
git reflog feature | Select -Last 1000 | Sort-Object -Descending
```

### 다양한 정렬 방법
```bash
# sed를 사용한 방법
git reflog feature | sed '1!G;h;$!d'

# awk를 사용한 방법
git reflog feature | awk '{a[NR]=$0} END {for(i=NR;i>=1;i--) print a[i]}'

# Python 원라이너
git reflog feature | python -c "import sys; print(''.join(reversed(sys.stdin.readlines())))"
```

### 날짜 정보와 함께 정렬
```bash
# 날짜 정보 포함하여 출력 후 정렬
git reflog feature --date=iso | tac

# Unix timestamp로 변환 후 정렬
git reflog feature --format="%ct %h %gs" | sort -n | cut -d' ' -f2-
```

### Git 별칭 설정
```bash
# Git 별칭 추가
git config --global alias.reflog-chrono '!git reflog "$@" | tac'

# 사용
git reflog-chrono feature
```

## 4. tac 명령어 설명

### 이름의 의미
`tac`는 **`cat`의 역순**입니다.
- `cat` = con**cat**enate (연결하다)
- `tac` = `cat`을 거꾸로 쓴 것

### 기본 동작
```bash
# cat: 파일을 위에서 아래로 출력
cat file.txt
Line 1
Line 2
Line 3

# tac: 파일을 아래에서 위로 출력
tac file.txt
Line 3
Line 2
Line 1
```

### 주요 옵션
```bash
# -s: 구분자 지정 (기본값: 줄바꿈)
echo "A,B,C,D" | tac -s ","
D,C,B,A,
```

### 시스템별 대안
- **macOS**: `tail -r` 또는 `brew install coreutils` 후 `gtac` 사용
- **Windows**: PowerShell에서 `Get-Content file.txt | Sort-Object -Descending`

### Git과 함께 사용하는 예시
```bash
# 커밋 메시지 역순
git log --oneline | tac

# reflog를 시간순으로
git reflog | tac

# 브랜치 생성 시간순 (오래된 것부터)
git for-each-ref --sort=committerdate --format='%(refname:short)' | tac
```

## 5. 프로젝트 적용 시 고려사항

### git-doc-gen 도구에서의 활용
```python
def get_branch_commits(repo, branch_name, base_branch='main'):
    """브랜치의 고유 커밋을 가져오는 함수"""
    
    # 1. 먼저 merge 여부 확인
    is_merged = check_if_merged(repo, branch_name, base_branch)
    
    if is_merged:
        # 2. merge된 경우: reflog 사용하여 merge 이전 커밋 찾기
        commits = get_commits_before_merge_from_reflog(repo, branch_name)
    else:
        # 3. merge 안 된 경우: 일반적인 방법
        commits = repo.git.log(f"{base_branch}..{branch_name}")
    
    return commits
```

### 결론
- `git log main..feature`는 feature가 완전히 merge된 경우 빈 결과를 반환
- `git reflog`를 활용하면 브랜치의 과거 상태를 추적 가능
- `tac` 명령어로 출력 순서를 쉽게 뒤집을 수 있음
- 도구 개발 시 merge 상태를 고려한 유연한 접근 필요