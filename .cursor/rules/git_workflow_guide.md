# Git 워크플로우 가이드

## 🎯 개요

**Git을 사용한 협업 개발을 위한 워크플로우 및 모범 사례 가이드입니다.**

## 🌿 브랜치 전략

### 1. Git Flow (전통적인 방식)
```
main (production)
├── develop (integration)
│   ├── feature/user-auth
│   ├── feature/payment
│   └── hotfix/critical-bug
├── release/v1.2.0
└── hotfix/security-patch
```

**브랜치 역할:**
- **main**: 프로덕션 코드 (안정적)
- **develop**: 개발 통합 브랜치
- **feature/***: 새로운 기능 개발
- **release/***: 릴리스 준비
- **hotfix/***: 긴급 수정

### 2. GitHub Flow (간단한 방식)
```
main
├── feature/user-auth
├── feature/payment
└── hotfix/critical-bug
```

**브랜치 역할:**
- **main**: 항상 배포 가능한 상태
- **feature/***: 기능 개발
- **hotfix/***: 긴급 수정

### 3. Trunk-Based Development (현대적인 방식)
```
main (trunk)
├── feature/user-auth
├── feature/payment
└── hotfix/critical-bug
```

**브랜치 역할:**
- **main**: 메인 브랜치 (trunk)
- **feature/***: 단기 기능 브랜치 (1-2일)
- **hotfix/***: 긴급 수정

## 📝 커밋 메시지 규칙

### Conventional Commits
```bash
# 형식: <type>[optional scope]: <description>

# 기능 추가
git commit -m "feat: add user authentication system"
git commit -m "feat(auth): implement JWT token validation"

# 버그 수정
git commit -m "fix: resolve login page crash"
git commit -m "fix(api): handle null response from external service"

# 문서 업데이트
git commit -m "docs: update API documentation"
git commit -m "docs(readme): add installation instructions"

# 스타일 변경
git commit -m "style: format code according to style guide"
git commit -m "style(ui): improve button hover effects"

# 리팩토링
git commit -m "refactor: simplify user validation logic"
git commit -m "refactor(database): optimize query performance"

# 테스트
git commit -m "test: add unit tests for user service"
git commit -m "test(integration): add API endpoint tests"

# 빌드/배포
git commit -m "build: update dependencies to latest versions"
git commit -m "ci: add automated testing pipeline"
```

### 커밋 타입 설명
- **feat**: 새로운 기능
- **fix**: 버그 수정
- **docs**: 문서 변경
- **style**: 코드 스타일 변경 (기능에 영향 없음)
- **refactor**: 코드 리팩토링
- **test**: 테스트 추가/수정
- **chore**: 빌드 프로세스, 도구 변경
- **perf**: 성능 개선
- **ci**: CI/CD 설정 변경

## 🔄 워크플로우 단계

### 1. 기능 개발 워크플로우

```bash
# 1. 최신 main 브랜치 가져오기
git checkout main
git pull origin main

# 2. 기능 브랜치 생성
git checkout -b feature/user-authentication

# 3. 개발 작업
# ... 코드 작성 ...

# 4. 변경사항 스테이징
git add .

# 5. 커밋
git commit -m "feat: implement user login functionality"

# 6. 원격 저장소에 푸시
git push origin feature/user-authentication

# 7. Pull Request 생성 (GitHub/GitLab)
# 8. 코드 리뷰 및 수정
# 9. main 브랜치로 병합
```

### 2. 핫픽스 워크플로우

```bash
# 1. main 브랜치에서 핫픽스 브랜치 생성
git checkout main
git checkout -b hotfix/critical-security-issue

# 2. 긴급 수정
# ... 수정 작업 ...

# 3. 커밋
git commit -m "fix: resolve critical security vulnerability"

# 4. 푸시 및 PR 생성
git push origin hotfix/critical-security-issue

# 5. 빠른 리뷰 및 병합
# 6. main과 develop 모두에 병합
```

### 3. 릴리스 워크플로우

```bash
# 1. develop에서 릴리스 브랜치 생성
git checkout develop
git checkout -b release/v1.2.0

# 2. 버전 번호 업데이트
# ... 버전 정보 수정 ...

# 3. 커밋
git commit -m "chore: bump version to 1.2.0"

# 4. main과 develop에 병합
git checkout main
git merge release/v1.2.0
git tag v1.2.0

git checkout develop
git merge release/v1.2.0

# 5. 릴리스 브랜치 삭제
git branch -d release/v1.2.0
```

## 🚨 충돌 해결

### 1. Merge 충돌 해결
```bash
# 1. 충돌 발생 시
git merge feature/user-auth
# CONFLICT (content): Merge conflict in src/auth.py

# 2. 충돌 파일 확인
git status

# 3. 충돌 해결
# 파일 편집하여 충돌 마커 제거
<<<<<<< HEAD
def login():
    return "old login"
=======
def login():
    return "new login with 2FA"
>>>>>>> feature/user-auth

# 4. 해결된 파일 스테이징
git add src/auth.py

# 5. 병합 완료
git commit -m "merge: resolve conflicts in auth.py"
```

### 2. Rebase 충돌 해결
```bash
# 1. Rebase 시작
git rebase main

# 2. 충돌 발생 시
# CONFLICT (content): Merge conflict in src/auth.py

# 3. 충돌 해결 후
git add src/auth.py
git rebase --continue

# 4. 모든 충돌 해결 후
git push origin feature/user-auth --force-with-lease
```

## 🔧 고급 Git 기능

### 1. Interactive Rebase
```bash
# 커밋 히스토리 정리
git rebase -i HEAD~3

# 편집기에서:
# pick   abc1234 feat: add user authentication
# squash def5678 feat: add password validation
# squash ghi9012 feat: add email verification
```

### 2. Cherry-pick
```bash
# 특정 커밋만 가져오기
git cherry-pick abc1234

# 여러 커밋 가져오기
git cherry-pick abc1234 def5678 ghi9012
```

### 3. Stash 활용
```bash
# 작업 중인 변경사항 임시 저장
git stash push -m "WIP: user authentication"

# 다른 브랜치로 이동
git checkout main

# 작업 완료 후 stash 적용
git checkout feature/user-auth
git stash pop
```

## 📋 Pull Request 가이드

### 1. PR 템플릿
```markdown
## 🎯 변경 사항
이 PR에서 구현한 기능이나 수정 사항을 설명하세요.

## 🔍 변경 이유
왜 이 변경이 필요한지 설명하세요.

## 🧪 테스트
어떤 테스트를 수행했는지 설명하세요.

## 📸 스크린샷 (UI 변경 시)
변경 전후 스크린샷을 첨부하세요.

## ✅ 체크리스트
- [ ] 코드가 프로젝트 스타일 가이드를 따릅니다
- [ ] 자체 코드 리뷰를 수행했습니다
- [ ] 코드에 주석을 추가했습니다 (특히 이해하기 어려운 부분)
- [ ] 문서를 업데이트했습니다
- [ ] 변경사항이 기존 기능을 깨뜨리지 않습니다
- [ ] 새로운 테스트를 추가했거나 기존 테스트를 수정했습니다
```

### 2. 리뷰 가이드
```markdown
## 🎯 리뷰 포인트
- 코드 품질 및 가독성
- 성능 및 보안
- 테스트 커버리지
- 문서화 품질

## 💬 리뷰 코멘트 예시
- "이 함수는 너무 길어서 가독성이 떨어집니다. 작은 함수들로 분리해보세요."
- "에러 처리가 누락되어 있습니다. 예외 상황을 고려해주세요."
- "이 부분에 대한 테스트가 필요합니다."
```

## 🚨 일반적인 문제와 해결

### 1. 실수로 잘못된 브랜치에 커밋
```bash
# 1. 현재 커밋을 다른 브랜치로 이동
git stash
git checkout correct-branch
git stash pop

# 2. 잘못된 브랜치에서 커밋 제거
git checkout wrong-branch
git reset --hard HEAD~1
```

### 2. 커밋 메시지 수정
```bash
# 마지막 커밋 메시지 수정
git commit --amend -m "feat: add user authentication system"

# 이전 커밋 메시지 수정
git rebase -i HEAD~3
# 편집기에서 'reword'로 변경
```

### 3. 파일 삭제 취소
```bash
# 삭제된 파일 복구
git checkout HEAD -- deleted-file.py

# 특정 커밋에서 파일 복구
git checkout abc1234 -- deleted-file.py
```

## 🔄 자동화 도구

### 1. Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
  
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.0.0
    hooks:
      - id: commitizen
```

### 2. GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          pip install -r requirements.txt
          pytest
```

## 📚 참고 자료

- [Git 공식 문서](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)

---

**작성일**: 2024-09-04
**버전**: 1.0.0
**용도**: Git 워크플로우 및 협업 모범 사례 참고
