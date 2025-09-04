# .cursor/rules 디렉토리 가이드

## 🎯 목적

이 디렉토리는 **어떤 주제의 프로젝트에서도 사용할 수 있는 범용적인 개발 가이드들**을 포함합니다.

## 📚 포함된 범용 가이드

### 1. [Python 프로젝트 구조 가이드](./python_project_structure.md)
**Python 프로젝트의 표준적인 구조와 모범 사례**

**주요 내용:**
- 표준 프로젝트 구조 (소규모/대규모)
- 패키지 구조 원칙 (계층 분리, 의존성 주입, 설정 관리)
- 테스트 구조 및 데이터 관리
- 개발 도구 설정 (pre-commit, ruff, mypy)
- 문서화 가이드
- 개발 워크플로우
- 일반적인 문제와 해결 방법

**사용 시기:** Python 프로젝트를 시작할 때, 프로젝트 구조를 개선하고 싶을 때

### 2. [Git 워크플로우 가이드](./git_workflow_guide.md)
**Git을 사용한 협업 개발 워크플로우 및 모범 사례**

**주요 내용:**
- 브랜치 전략 (Git Flow, GitHub Flow, Trunk-Based Development)
- 커밋 메시지 규칙 (Conventional Commits)
- 워크플로우 단계별 가이드
- 충돌 해결 방법
- 고급 Git 기능 (Interactive Rebase, Cherry-pick, Stash)
- Pull Request 가이드 및 템플릿
- 일반적인 문제와 해결 방법
- 자동화 도구 설정

**사용 시기:** Git 협업 워크플로우를 설정할 때, 팀 개발 프로세스를 개선하고 싶을 때

### 3. [코드 품질 관리 가이드](./code_quality_guide.md)
**코드 품질을 유지하고 향상시키기 위한 도구와 모범 사례**

**주요 내용:**
- 핵심 도구 (Linting, Formatting, Type Checking)
- 코드 품질 체크리스트 (가독성, 성능, 보안, 테스트)
- 도구 설정 예시
- 모범 사례 (함수 설계, 에러 처리, 테스트 작성)
- 일반적인 문제와 해결 방법
- 지속적 개선 방법

**사용 시기:** 코드 품질을 향상시키고 싶을 때, 개발 도구를 설정할 때

### 4. [PROJECT_PLAN.md 기반 작업 규칙](./project_plan_based_work.md) ⭐ **NEW**
**프로젝트 계획 문서를 기반으로 모든 작업을 체계적으로 진행하는 규칙**

**주요 내용:**
- PROJECT_PLAN.md 기반 작업 시작 원칙
- 우선순위별 작업 관리 (P0, P1, P2)
- 체크리스트 및 백로그 관리 방법
- Cursor 사용 지시 예시
- 문서화 및 변경 로그 관리 규칙

**사용 시기:** 모든 작업을 시작할 때, 프로젝트 진행 상황을 체계적으로 관리하고 싶을 때

### 5. [MCP Client 개발 규칙](./mcp_client_development.md) ⭐ **SPECIFIC**
**MCP Client (FastAPI + LangGraph) 개발을 위한 전용 규칙**

**주요 내용:**
- MCP_CLIENT_PLAN.md 기반 개발 진행
- LangGraph 베스트 프랙티스 준수
- `langchain-mcp-adapters` 사용 가이드
- MCP 통합 표준 및 구현 가이드라인
- 개발 워크플로우 및 품질 기준

**사용 시기:** MCP Client 개발 시, LangGraph 통합 작업 시

## 🚀 활용 방법

### 새 프로젝트 시작
1. **Python 프로젝트**: [Python 프로젝트 구조 가이드](./python_project_structure.md) 참조
2. **Git 설정**: [Git 워크플로우 가이드](./git_workflow_guide.md) 참조
3. **품질 관리**: [코드 품질 관리 가이드](./code_quality_guide.md) 참조
4. **작업 관리**: [PROJECT_PLAN.md 기반 작업 규칙](./project_plan_based_work.md) 참조
5. **MCP Client 개발**: [MCP Client 개발 규칙](./mcp_client_development.md) 참조

### 기존 프로젝트 개선
1. **구조 개선**: [Python 프로젝트 구조 가이드](./python_project_structure.md)의 모범 사례 적용
2. **워크플로우 개선**: [Git 워크플로우 가이드](./git_workflow_guide.md)의 브랜치 전략 적용
3. **품질 향상**: [코드 품질 관리 가이드](./code_quality_guide.md)의 도구 및 체크리스트 적용
4. **작업 체계화**: [PROJECT_PLAN.md 기반 작업 규칙](./project_plan_based_work.md)의 체계적 작업 관리 방법 적용

### 팀 개발 표준화
1. **코딩 표준**: 가이드의 모범 사례를 팀 표준으로 채택
2. **워크플로우**: Git 워크플로우를 팀 규칙으로 설정
3. **품질 관리**: 코드 품질 체크리스트를 PR 리뷰 기준으로 활용

## 🔄 가이드 확장

### 새로운 가이드 추가
- **프론트엔드 개발**: React/Vue.js 프로젝트 구조 및 모범 사례
- **데이터베이스**: 데이터베이스 설계 및 마이그레이션 가이드
- **DevOps**: CI/CD, Docker, Kubernetes 설정 가이드
- **보안**: 보안 모범 사례 및 취약점 방지 가이드

### 가이드 개선
- 프로젝트별 경험과 모범 사례 추가
- 커뮤니티 피드백 반영
- 새로운 기술 트렌드 반영

## 💡 사용 팁

### 1. 프로젝트별 맞춤화
- 가이드의 내용을 프로젝트 특성에 맞게 수정
- 팀의 기술 스택과 선호도 반영
- 프로젝트 규모에 맞는 구조 선택

### 2. 점진적 적용
- 모든 가이드를 한 번에 적용하지 말고 단계적으로 적용
- 팀원들의 학습 곡선 고려
- 피드백을 받아가며 개선

### 3. 지속적 학습
- 정기적으로 가이드 내용 검토 및 업데이트
- 새로운 도구나 방법론 도입 시 가이드에 반영
- 팀 내 지식 공유 세션 활용

## 📖 추가 자료

### 공식 문서
- [Python 공식 문서](https://docs.python.org/)
- [Git 공식 문서](https://git-scm.com/doc)
- [Conventional Commits](https://www.conventionalcommits.org/)

### 커뮤니티
- [Python 한국 사용자 그룹](https://www.facebook.com/groups/pythonkorea/)
- [GitHub 커뮤니티](https://github.com/community)
- [개발자 커뮤니티](https://okky.kr/)

---

**작성일**: 2024-09-04
**버전**: 1.0.0
**목적**: 범용적인 개발 가이드 제공으로 개발 생산성 향상
