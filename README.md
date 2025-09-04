# MCP GitHub + MCP Client 프로젝트

이 프로젝트는 **GitHub MCP Server**와 **MCP Client (FastAPI + LangGraph)** 두 부분으로 구성되어 있습니다.

## 🏗️ 프로젝트 구조

```
├── mcp_github/          # GitHub MCP Server (fastMCP 기반)
└── mcp_client/          # MCP Client (FastAPI + LangGraph)
```

---

# 🚀 MCP GitHub Server

GitHub MCP server built with fastMCP.

## 설치

```bash
# 가상환경 활성화
source venv/bin/activate

# 개발 모드로 설치
pip install -e .
```

## 환경변수 설정

GitHub API를 사용하려면 Personal Access Token이 필요합니다:

1. [GitHub Settings > Tokens](https://github.com/settings/tokens)에서 새 토큰 생성
2. 필요한 권한: `repo`, `user`
3. 환경변수 설정:

```bash
# .env 파일 생성 (프로젝트 루트에)
echo "GITHUB_TOKEN=your_token_here" > .env

# 또는 직접 환경변수 설정
export GITHUB_TOKEN=your_token_here
```

## 실행

```bash
# 가상환경 활성화
source venv/bin/activate

# MCP 서버 실행
python -m mcp_github.server
```

## Cursor 설정

Cursor에서 MCP 서버를 연결하려면 다음 설정을 사용하세요:

```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["-m", "mcp_github.server"],
      "cwd": "/Users/hyunwoo/Desktop/클테코/20250904_githubMCP",
      "env": {
        "PYTHUB_TOKEN": "your_github_token_here",
        "PYTHONPATH": "/Users/hyunwoo/Desktop/클테코/20250904_githubMCP"
      }
    }
  }
}
```

## 사용 가능한 도구들

### 읽기 전용 도구들 (Read Tools)

#### health
서버 상태 확인
```json
{
  "status": "ok"
}
```

#### getRepo
GitHub 저장소 정보 조회
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice"
}
```

#### listPullRequests
Pull Request 목록 조회
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice",
  "state": "open"
}
```

#### getPRDiff
Pull Request의 diff 조회
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice",
  "number": 1
}
```

#### getFile
저장소의 파일 내용 조회
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice",
  "path": "README.md",
  "ref": "main"
}
```

### 쓰기 도구들 (Write Tools)

#### createOrUpdateFile
파일 생성 또는 수정
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice",
  "path": "new_file.txt",
  "content": "Hello, World!",
  "message": "Add new file",
  "branch": "main",
  "committer_name": "Your Name",
  "committer_email": "your.email@example.com"
}
```

#### deleteFile
파일 삭제
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice",
  "path": "file_to_delete.txt",
  "message": "Delete file",
  "branch": "main"
}
```

#### createBranch
새 브랜치 생성
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice",
  "new_branch": "feature-branch",
  "base_branch": "main"
}
```

#### createCommitWithMultipleFiles
여러 파일을 한 번에 커밋
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice",
  "files": [
    {
      "path": "file1.txt",
      "content": "Content 1",
      "operation": "create"
    },
    {
      "path": "file2.txt",
      "content": "Updated content",
      "operation": "update"
    }
  ],
  "message": "Multiple file changes",
  "branch": "main"
}
```

#### getRepositoryStatus
저장소 상태 및 최신 커밋 정보 조회
```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice",
  "ref": "main"
}
```

## 사용 예시

### 파일 생성 및 커밋

1. 새 파일 생성:
```json
{
  "tool": "createOrUpdateFile",
  "arguments": {
    "owner": "J-nowcow",
    "repo": "github-MCP-practice",
    "path": "docs/new_feature.md",
    "content": "# New Feature\n\nThis is a new feature documentation.",
    "message": "Add new feature documentation"
  }
}
```

2. 파일 수정:
```json
{
  "tool": "createOrUpdateFile",
  "arguments": {
    "owner": "J-nowcow",
    "repo": "github-MCP-practice",
    "path": "README.md",
    "content": "# Updated README\n\nUpdated content here.",
    "message": "Update README"
  }
}
```

3. 새 브랜치에서 작업:
```json
{
  "tool": "createBranch",
  "arguments": {
    "owner": "J-nowcow",
    "repo": "github-MCP-practice",
    "new_branch": "feature/new-ui",
    "base_branch": "main"
  }
}
```

---

# 🧠 MCP Client (FastAPI + LangGraph)

Azure OpenAI + GitHub MCP Server를 연결하는 **MCP Client(FastAPI + LangGraph)** 프로젝트입니다.

## 🎯 프로젝트 개요

이 프로젝트는 사용자가 REST API(`/chat`)로 자연어 요청을 보내면:
1. **MCP Server(GitHub)** 연결 → 사용 가능한 툴 목록 조회
2. **LangGraph ReAct Agent** → Azure OpenAI 모델로 툴 실행 계획 수립
3. **MCP Server** → 실제 툴 실행 및 결과 수집
4. **LangGraph 워크플로우** → 최종 응답 생성 및 반환

## 🏗️ 아키텍처

```
FastAPI → LangGraph Agent → MCP Server → GitHub
    ↓           ↓              ↓
  /chat → ReAct Workflow → Tools Execution
```

## 🚀 빠른 시작

### 1. 가상 환경 설정

```bash
# 가상 환경 생성
python -m venv venv

# 가상 환경 활성화
source venv/bin/activate  # macOS/Linux
# 또는
venv\Scripts\activate     # Windows
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 프로젝트 루트에 생성하고 다음 내용을 추가하세요:

```env
# MCP Server
MCP_SERVER_URL=http://localhost:3000

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview
OPENAI_TEMPERATURE=0.1

# HTTP
HTTP_TIMEOUT_SEC=30
```

### 4. 서버 실행

```bash
# 개발 모드로 실행
uvicorn mcp_client.main:app --reload --port 8081
```

## 📡 API 엔드포인트

### POST /chat
사용자 질문을 처리하고 MCP 도구를 사용하여 응답을 생성합니다.

**요청:**
```json
{
  "query": "GitHub 이슈 생성해줘",
  "thread_id": "optional_thread_id"
}
```

**응답:**
```json
{
  "response": "GitHub 이슈가 생성되었습니다",
  "used_tools": [
    {
      "name": "create_github_issue",
      "arguments": {"title": "...", "body": "..."},
      "result": {"url": "..."}
    }
  ],
  "status": "success",
  "trace": {
    "tool_names": ["create_github_issue"],
    "model_rounds": 2,
    "thread_id": "thread_123"
  }
}
```

### GET /health
서비스 상태를 확인합니다.

**응답:**
```json
{
  "status": "ok",
  "details": {
    "mcp_client": {"status": "connected", "tool_count": 5},
    "workflow": "ready",
    "tools_available": 5
  }
}
```

### GET /workflow/info
워크플로우 정보를 조회합니다.

**응답:**
```json
{
  "status": "success",
  "workflow_info": {
    "model": "gpt-4o",
    "temperature": 0.1,
    "nodes": ["agent"],
    "checkpointer": "MemorySaver"
  }
}
```

## 🛠️ 핵심 컴포넌트

### MCPClientManager (`mcp_client/mcp_client.py`)
- `langchain-mcp-adapters`의 `MultiServerMCPClient` 래퍼 클래스
- 비동기 컨텍스트 매니저 구현
- 에러 처리 및 재시도 로직

### MCPAgentWorkflow (`mcp_client/agent/workflow.py`)
- LangGraph의 `StateGraph`를 사용한 ReAct 에이전트 구성
- Azure OpenAI 모델과 MCP 도구 통합
- 워크플로우 실행 및 결과 처리

## 🔧 개발

### 프로젝트 구조
```
mcp_client/
├── __init__.py
├── main.py                 # FastAPI 엔트리포인트
├── config.py              # 환경변수 설정
├── schemas.py             # Pydantic 모델
├── mcp_client.py          # MCP 서버 연결 관리
└── agent/
    ├── __init__.py
    └── workflow.py        # LangGraph 워크플로우
```

### 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 테스트
pytest tests/ -v

# 커버리지
pytest --cov=mcp_client
```

### 코드 품질

```bash
# 린팅
ruff check .

# 포맷팅
ruff format .

# 타입 체크
mypy mcp_client/
```

## 📚 기술 스택

- **Python 3.11+**
- **FastAPI** - 웹 프레임워크
- **LangGraph** - 워크플로우 오케스트레이션
- **langchain-mcp-adapters** - MCP 통합
- **langchain-openai** - Azure OpenAI 통합
- **Pydantic** - 데이터 검증
- **Uvicorn** - ASGI 서버

## 🔍 문제 해결

### 일반적인 문제들

1. **MCP 서버 연결 실패**
   - MCP 서버가 실행 중인지 확인
   - `MCP_SERVER_URL` 환경변수 확인

2. **Azure OpenAI 인증 실패**
   - API 키와 엔드포인트 확인
   - 배포 이름과 API 버전 확인

3. **Import 오류**
   - 가상 환경이 활성화되었는지 확인
   - `pip install -r requirements.txt` 실행

### 로그 확인

서버 실행 시 상세한 로그를 확인할 수 있습니다:

```bash
uvicorn mcp_client.main:app --reload --port 8081 --log-level debug
```

---

## 🤝 기여

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면:
1. GitHub Issues에 문제를 등록
2. 프로젝트 문서 확인
3. 개발팀에 문의

---

**개발팀**: MCP GitHub + MCP Client Team  
**최종 업데이트**: 2025-09-04  
**버전**: 0.1.0


