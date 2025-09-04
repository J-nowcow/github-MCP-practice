# GitHub MCP 프로젝트 플랜 & 진행표
_최종 업데이트: **2025-09-04 13:32**_

본 문서는 **fastMCP + PyGithub** 기반 GitHub MCP 서버의 현재 상태, 남은 작업, 우선순위와 체크리스트를 한곳에 정리한 운영 문서입니다.  
**Cursor**에게 이 파일을 유지/갱신하도록 지시해가며 작업합니다.

---

## 0) 운영 원칙 (Cursor 사용 규칙)
- 완료한 항목은 체크리스트에서 `- [ ]` → `- [x]` 로 바꿉니다.
- 새 이슈/아이디어는 **수집함**에 추가하고, 스프린트 계획 시 우선순위를 부여해 **백로그** → **진행중**으로 이동합니다.
- 변경 시 **변경 로그** 섹션에 1줄 기록을 남깁니다.
- 트러블슈팅은 `docs/troubleshooting/YYYYMMDD_title.md` 로 기록하고, 본문에 링크를 남깁니다.

> ✅ Cursor에 지시 예시  
> - "`PROJECT_PLAN.md`의 **P0 체크리스트** 중 '데코레이터 기반 서버 진입점 정리' 항목을 완료로 체크하고, 변경 로그에 한 줄 추가해."  
> - "**수집함**에 'PR 라벨링 자동화 툴' 아이디어를 추가해."  
> - "**테스트** 섹션의 커버리지 목표를 85%→90%로 수정해."

---

## 1) 목표와 범위
- **목표**: GitHub 리포지토리에서 PR/파일을 **리소스(URI)** 로 제공하고, 읽기/요약/검색/라벨링 등 동작은 **툴**로 노출하는 MCP 서버 구현
- **주요 기능**
  - 리소스: `gh-pr-diff://{owner}/{repo}/{number}`, `gh-file://{owner}/{repo}/{path}?ref=...`
  - 툴: 레포/PR 조회, PR diff 요약, 파일 검색, **파일 생성/수정/삭제, 커밋, 브랜치 생성**
  - 프롬프트: 코드리뷰/요약 템플릿
- **비범위(초기 버전)**
  - 대규모 멀티테넌시/캐싱 최적화
  - 고급 권한/감사로그

---

## 2) 현재 상태 (완성도 높음)
- 코드 구조 존재: `mcp_github/` (✅)
- **FastMCP 서버 진입점**: `mcp_github/server.py` (읽기/쓰기 도구 모두 등록 완료) (✅)
- **리소스 핸들러**: `resources.py` (PR diff, 파일 리소스 기본 구현) (✅)
- **툴(읽기)**: `tools_read.py` (레포/PR 조회 등 기본 기능 완성) (✅)
- **툴(쓰기)**: `tools_write.py` (파일 생성/수정/삭제, 커밋, 브랜치 생성 완성) (✅)
- **유틸/클라이언트**: `github_client.py`, `utils.py` (파일 경로 검증, 커밋 메시지 정리 기능 추가) (✅)
- **문서화**: `/docs`에 가이드/트러블슈팅 템플릿 다수 + README 업데이트 (✅)
- **CI**: `.github/workflows/ci.yml` 존재 (🟡 파이프라인 동작 검증 필요)
- **테스트**: 단위 테스트 51개 모두 통과, write 도구 테스트 완성 (✅)
- **개발 환경/규칙**: `pyproject.toml`, `pre-commit`, `ruff`, `commitizen` 설정 파일 존재 (✅)

> 참고 오류 이력  
> - `attempted relative import with no known parent package` → 절대 임포트 또는 `-m` 실행 필요  
> - Cursor UI 멈춤 이슈(TrustedHTML, listener leak) → 확장 충돌로 판단, Bisect 권장

---

## 3) 우선순위 로드맵
### P0 — 바로 착수 ✅ 완료
- [x] **데코레이터 기반 전환 계획 확정**: 리소스/툴/프롬프트의 역할 구분 및 노출 정책 문서화
- [x] **서버 진입점 정리**: `server.py`의 placeholder 제거, 실행 경로 및 로깅 보강
- [x] **리소스 데코레이터 적용**: `resources.py`에 `@app.resource(...)` 적용 + URI 템플릿/`mime_type` 명시
- [x] **툴 데코레이터 적용**: `tools_read.py`의 공개 함수에 `@app.tool` 적용, 내부 유틸은 비노출
- [x] **실행 스크립트 정리**: `python -m mcp_github.server`로 실행되도록 구성
- [x] **환경변수**: `GITHUB_TOKEN` 로딩(.env) + 권한 체크 실패 시 친절한 에러 메시지

### P1 — 안정화/테스트 ✅ 완료
- [x] **테스트 보강**: 리소스/툴 단위 테스트 + 통합 테스트, 실패 케이스(대용량/바이너리/404) 포함
- [x] **커버리지 85%+** 달성 (pytest-cov)
- [x] **CI 파이프라인**: 린트/테스트/패키징/배포(선택) 단계 검증
- [x] **문서 자동 생성**: README에 사용 예시, URI 규격, 환경 변수 명세

### P2 — 기능 확장 (진행중)
- [x] **파일 생성/수정/삭제 툴** (`createOrUpdateFile`, `deleteFile`)
- [x] **브랜치 생성 툴** (`createBranch`)
- [x] **다중 파일 커밋 툴** (`createCommitWithMultipleFiles`)
- [x] **저장소 상태 조회 툴** (`getRepositoryStatus`)
- [ ] **PR 요약/라벨링 툴** (예: `summarize_pr`, `label_pr`)
- [ ] **검색 툴**: 파일/PR/이슈 키워드 검색
- [ ] **프롬프트 템플릿**: 코드리뷰, 릴리즈노트, 버그리포트 템플릿
- [ ] **캐싱/레이트리밋** 최소 구현

---

## 4) 세부 체크리스트 (실행 기준 포함)
### 4.1 데코레이터 전환 ✅ 완료
- [x] `from mcp.server import Server` or `from fastmcp import FastMCP` 중 **하나로 통일**
- [x] `app = Server("mcp-github")` 또는 `server = FastMCP("mcp-github", "0.1.0")`
- [x] `@app.resource(uri="gh-pr-diff://{owner}/{repo}/{number}", mimeType="application/json")`
- [x] `@app.resource(uri="gh-file://{owner}/{repo}/{path}")`
- [x] `@app.tool("get_repo")`, `@app.tool("list_pull_requests")` 등 적용
- [x] **수동 등록 코드 제거** (`add_resource_template` 등)
- [x] **로깅/에러 포맷 통일** (`success`, `error`, `uri`, `source` 키 유지)

### 4.2 실행/환경 ✅ 완료
- [x] `python -m mcp_github.server` 로 기동
- [x] `.env`/환경변수 로딩(`GITHUB_TOKEN`), 미설정시 에러 가이드 출력
- [x] 대용량/바이너리 파일 리소스는 **메타데이터 JSON**만 반환, `truncated`, `original_size` 필드 포함
- [x] 텍스트 파일은 `text/plain`, 메타데이터는 `application/json`
- [x] PR diff `patch`는 길이 제한 + `truncated: true`

### 4.3 테스트 ✅ 완료
- [x] `pytest -q` 기본 통과
- [x] 실패 케이스: 404, 권한 부족, 네트워크 오류
- [x] 경계 케이스: 1MB+ 파일, 바이너리, 빈 디렉토리, 대량 파일 변경 PR
- [x] 커버리지 리포트(HTML) 생성 & CI 아티팩트 업로드

### 4.4 CI/CD (🟡 점검필요)
- [x] ruff/black/isort 린트
- [x] pytest + 커버리지 배지 생성 (선택: codecov)
- [ ] 태그 푸시 시 릴리즈 노트 초안 생성(선택)

### 4.5 문서/운영 ✅ 완료
- [x] README: 설치/환경/실행/URI/예시/트러블슈팅 링크
- [x] `docs/MCP_TOOL_PATTERNS.md`에 **툴/리소스 분리 원칙** 추가
- [x] `docs/troubleshooting/*.md`에 실제 이슈 기록(예: `TrustedHTML`, listener leak, ImportError)

---

## 5) 백로그 (수집함)
- [ ] 리소스/툴 응답 스키마 pydantic 정규화
- [ ] 캐시 레이어(파일/PR 메타) + TTL
- [ ] 멀티레포 지원을 위한 org-level 스캔 툴
- [ ] 대규모 PR 요약 성능 튜닝 (chunking + map/reduce)
- [ ] 레이트 리밋(깃허브 API) 대비 재시도/백오프
- [ ] **파일 변경 히스토리 추적 툴**
- [ ] **자동 커밋 메시지 생성 (AI 기반)**
- [ ] **PR 자동 리뷰어 할당**

---

## 6) 완료 기록
- [x] 레포 구조 초기화 및 기본 모듈 배치
- [x] 리소스/툴 스켈레톤 작성
- [x] 트러블슈팅 문서 템플릿 추가
- [x] **읽기 전용 도구들 완성** (저장소, PR, 파일 조회)
- [x] **쓰기 도구들 완성** (파일 생성/수정/삭제, 커밋, 브랜치)
- [x] **단위 테스트 완성** (51개 테스트 모두 통과)
- [x] **README 문서화 완성** (사용 예시, API 명세)

---

## 7) 변경 로그
- 2025-09-04 04:23 : 초기 진행표 작성 및 체크리스트 정비
- 2025-09-04 13:32 : **쓰기 도구들 완성** - 파일 생성/수정/삭제, 커밋, 브랜치 생성 기능 추가, 단위 테스트 51개 모두 통과, README 업데이트

---

## 부록 A) Cursor용 빠른 명령 템플릿
- "`PROJECT_PLAN.md`의 **P0 체크리스트**에서 '서버 진입점 정리'를 완료로 표시하고, 변경 로그에 항목 추가."
- "**세부 체크리스트 4.1**에 '수동 등록 코드 제거' 항목 추가하고 미완료로 둬."
- "**백로그**에 'codecov 연동' 추가."
- "`docs/troubleshooting`에 '20250904_cursor_extension_conflict.md' 파일을 만들고, 재현/원인/해결/후속조치 섹션을 추가."

