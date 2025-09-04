# MCP Client (FastAPI + LangGraph) 개발 계획서

_최종 업데이트: 2025-09-04_

이 문서는 **Azure OpenAI + GitHub MCP Server**를 연결하는 **MCP Client(FastAPI + LangGraph)** 개발 지침입니다.  
**Git MCP**를 통해 LangGraph 공식 문서를 참조하여 베스트 프랙티스를 적용합니다.

---

## 1. 목표 및 아키텍처

### 🎯 **핵심 목표**
사용자가 REST API(`/chat`)로 자연어 요청을 보내면:
1. **MCP Server(GitHub)** 연결 → 사용 가능한 툴 목록 조회
2. **LangGraph ReAct Agent** → Azure OpenAI 모델로 툴 실행 계획 수립
3. **MCP Server** → 실제 툴 실행 및 결과 수집
4. **LangGraph 워크플로우** → 최종 응답 생성 및 반환

### 🏗️ **아키텍처 개요**
```
FastAPI → LangGraph Agent → MCP Server → GitHub
    ↓           ↓              ↓
  /chat → ReAct Workflow → Tools Execution
```

### 📋 **상세 시퀀스 플로우 (ASCII 아트)**

```
┌─────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User   │    │   MCP Client    │    │ LangGraph Agent │    │   MCP Server    │    │ Azure OpenAI    │
│         │    │   (FastAPI)     │    │                 │    │    (GitHub)     │    │     API        │
└────┬────┘    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
     │                   │                      │                      │                      │
     │ 1. POST /chat     │                      │                      │                      │
     │ {"query": "GitHub │                      │                      │                      │
     │  이슈 생성해줘"}  │                      │                      │                      │
     │ ──────────────────┼──────────────────────►│                      │                      │
     │                   │                      │                      │                      │
     │                   │ 2. MCP 도구 가져오기  │                      │                      │
     │                   │ (JSON-RPC 2.0)       │                      │                      │
     │                   │ {"jsonrpc": "2.0",   │                      │                      │
     │                   │  "method": "tools/   │                      │                      │
     │                   │  list", "id": 1}     │                      │                      │
     │                   │ ─────────────────────┼──────────────────────►│                      │
     │                   │                      │                      │                      │
     │                   │                      │                      │ 3. 도구 목록 반환    │
     │                   │                      │                      │ {"jsonrpc": "2.0",   │
     │                   │                      │                      │  "result": {"tools":  │
     │                   │                      │                      │   [...]}, "id": 1}   │
     │                   │                      │                      │ ◄─────────────────────┼
     │                   │                      │                      │                      │
     │                   │                      │ 4. LangGraph 에이전트 │                      │
     │                   │                      │ 생성 및 실행          │                      │
     │                   │                      │ agent.ainvoke({       │                      │
     │                   │                      │   "messages": [...]  │                      │
     │                   │                      │ })                   │                      │
     │                   │                      │ ─────────────────────┼──────────────────────►│
     │                   │                      │                      │                      │
     │                   │                      │                      │                      │ 5. Azure OpenAI
     │                   │                      │                      │                      │ API 호출
     │                   │                      │                      │                      │ HTTP POST
     │                   │                      │                      │                      │ /chat/completions
     │                   │                      │                      │                      │ {"messages": [...],
     │                   │                      │                      │                      │  "tools": [...],
     │                   │                      │                      │                      │  "model": "gpt-4o"}
     │                   │                      │                      │                      │ ◄─────────────────────┼
     │                   │                      │                      │                      │
     │                   │                      │                      │                      │ 6. LLM 도구 사용
     │                   │                      │                      │                      │ 결정 응답
     │                   │                      │                      │                      │ {"choices": [{"message":
     │                   │                      │                      │                      │  {"role": "assistant",
     │                   │                      │                      │                      │   "tool_calls": [...]}
     │                   │                      │                      │                      │ }]}
     │                   │                      │                      │                      │
     │                   │                      │ 7. 도구 실행 요청    │                      │
     │                   │                      │ {"jsonrpc": "2.0",   │                      │
     │                   │                      │  "method": "tools/   │                      │
     │                   │                      │  call", "params":    │                      │
     │                   │                      │  {"name": "create_   │                      │
     │                   │                      │   github_issue",     │                      │
     │                   │                      │   "arguments": {...} │                      │
     │                   │                      │ }, "id": 2}         │                      │
     │                   │                      │ ─────────────────────┼──────────────────────►│
     │                   │                      │                      │                      │
     │                   │                      │                      │ 8. 도구 실행 결과    │
     │                   │                      │                      │ {"jsonrpc": "2.0",   │
     │                   │                      │                      │  "result": {"content":│
     │                   │                      │                      │   "이슈 생성됨"},     │
     │                   │                      │                      │  "id": 2}            │
     │                   │                      │                      │ ◄─────────────────────┼
     │                   │                      │                      │                      │
     │                   │                      │                      │                      │ 9. 최종 응답 생성
     │                   │                      │                      │                      │ HTTP POST
     │                   │                      │                      │                      │ /chat/completions
     │                   │                      │                      │                      │ {"messages": [
     │                   │                      │                      │                      │   {"role": "user", ...},
     │                   │                      │                      │                      │   {"role": "assistant", ...},
     │                   │                      │                      │                      │   {"role": "tool", ...}
     │                   │                      │                      │                      │ ]}
     │                   │                      │                      │                      │ ◄─────────────────────┼
     │                   │                      │                      │                      │
     │                   │                      │                      │                      │ 10. 최종 응답
     │                   │                      │                      │                      │ {"choices": [{"message":
     │                   │                      │                      │                      │  {"role": "assistant",
     │                   │                      │                      │                      │   "content": "GitHub
     │                   │                      │                      │                      │    이슈가 생성되었습니다!"}
     │                   │                      │                      │                      │ }]}
     │                   │                      │                      │                      │
     │                   │                      │ 11. 최종 응답 반환   │                      │                      │
     │                   │                      │ {"messages": [...]}  │                      │                      │
     │                   │                      │ ◄────────────────────┼──────────────────────┼
     │                   │                      │                      │                      │
     │ 12. 최종 응답      │                      │                      │                      │                      │
     │ {"response": "Git │                      │                      │                      │                      │
     │  Hub 이슈가 생성  │                      │                      │                      │                      │
     │  되었습니다!",     │                      │                      │                      │                      │
     │  "status": "suc   │                      │                      │                      │                      │
     │  cess"}           │                      │                      │                      │                      │
     │ ◄─────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼
     │                   │                      │                      │                      │
```

**핵심 특징:**
- **모듈화된 아키텍처**: 각 컴포넌트가 명확한 역할을 담당
- **JSON-RPC 2.0**: MCP Client와 MCP Server 간 통신
- **OpenAI Chat Format**: LangGraph Agent와 Azure OpenAI API 간 통신
- **LangGraph 오케스트레이션**: LLM의 도구 사용 결정을 기반으로 한 멀티스텝 워크플로우

---

## 2. 기술 스택 (LangGraph 베스트 프랙티스)

### 🐍 **핵심 의존성**
- Python 3.11+
- **LangGraph 0.2.0+** (워크플로우 오케스트레이션)
- **langchain-mcp-adapters** (MCP 통합)
- **langchain-openai** (Azure OpenAI 통합)

### 🚀 **웹 프레임워크**
- FastAPI, uvicorn
- httpx (비동기 HTTP 클라이언트)

### 📊 **데이터 관리**
- pydantic v2 (스키마 검증)
- python-dotenv (환경변수)

### 🛠️ **유틸리티**
- tenacity (재시도 로직)
- structlog (구조적 로깅)

---

## 3. 환경 변수

```env
# MCP Server
MCP_SERVER_URL=http://localhost:3000

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://oai-az01-sbox-poc-145.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview
OPENAI_TEMPERATURE=0.1

# HTTP
HTTP_TIMEOUT_SEC=30
```

---

## 4. 폴더 구조 (LangGraph 최적화)

```
mcp_client/
├── __init__.py
├── main.py                 # FastAPI 엔트리포인트
├── config.py              # 환경변수 설정
├── schemas.py             # Pydantic 모델 (LangGraph 호환)
├── mcp_client.py          # MCP 서버 연결 (langchain-mcp-adapters)
├── agent/
│   ├── __init__.py
│   ├── workflow.py        # LangGraph 워크플로우 정의
│   ├── nodes.py           # 커스텀 노드들
│   └── state.py           # 상태 관리
└── utils/
    ├── __init__.py
    └── logging.py         # 구조적 로깅

tests/
├── test_agent_flow.py     # LangGraph 워크플로우 테스트
├── test_mcp_integration.py # MCP 통합 테스트
└── conftest.py            # 테스트 설정
```

---

## 5. LangGraph 워크플로우 설계

### 🔄 **ReAct 패턴 구현**
```python
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

# 1. MCP 클라이언트 생성
async with MultiServerMCPClient({
    "github": {"url": "http://localhost:3000", "transport": "sse"}
}) as client:
    # 2. ReAct 에이전트 생성
    agent = create_react_agent(
        model="azure-openai:gpt-4o",
        tools=client.get_tools()
    )
```

### 🏗️ **워크플로우 구조**
```
START → [MCP Tools Discovery] → [ReAct Agent] → [Tool Execution] → [Response Generation] → END
                ↓                      ↓              ↓                    ↓
         tools/list 호출        툴 선택 및 계획    tools/call 실행     최종 응답 생성
```

### 📊 **상태 관리**
```python
from langgraph.graph import MessagesState

# 표준 메시지 상태 사용
state = MessagesState(
    messages=[],      # 대화 히스토리
    next="agent"     # 다음 실행할 노드
)
```

---

## 6. MCP 통합 (공식 문서 기반)

### 🔌 **MCP 클라이언트 설정**
```python
# langchain-mcp-adapters 사용
from langchain_mcp_adapters.client import MultiServerMCPClient

mcp_config = {
    "github": {
        "url": "http://localhost:3000",
        "transport": "sse",  # Server-Sent Events
        "headers": {
            "Authorization": "Bearer your_token"
        }
    }
}

async with MultiServerMCPClient(mcp_config) as client:
    tools = client.get_tools()
    # tools는 LangChain Tool 객체들의 리스트
```

### 🛠️ **툴 변환 자동화**
- **MCP → LangChain**: `langchain-mcp-adapters`가 자동 처리
- **스키마 변환**: `input_schema` → `parameters` 자동 매핑
- **타입 안전성**: Pydantic 기반 검증

---

## 7. API 스펙

### POST /chat
```json
{
  "query": "GitHub 이슈 생성해줘",
  "thread_id": "optional_thread_id"
}
```

### Response
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
```json
{
  "status": "ok",
  "mcp_server": "connected",
  "langgraph": "ready"
}
```

---

## 8. 핵심 구현 모듈

### 🧠 **Agent Workflow (`agent/workflow.py`)**
```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

class MCPAgentWorkflow:
    def __init__(self, mcp_client, model):
        self.mcp_client = mcp_client
        self.agent = create_react_agent(model, mcp_client.get_tools())
        self.graph = self._build_workflow()
    
    def _build_workflow(self):
        workflow = StateGraph(MessagesState)
        
        # 노드 추가
        workflow.add_node("agent", self.agent)
        
        # 엣지 연결
        workflow.add_edge("agent", END)
        
        return workflow.compile()
```

### 🔌 **MCP Client (`mcp_client.py`)**
```python
from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPClientManager:
    def __init__(self, config):
        self.config = config
        self.client = None
    
    async def __aenter__(self):
        self.client = MultiServerMCPClient(self.config)
        await self.client.__aenter__()
        return self.client
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
```

### 🚀 **FastAPI Integration (`main.py`)**
```python
from fastapi import FastAPI
from .agent.workflow import MCPAgentWorkflow

app = FastAPI(title="MCP Client + LangGraph")

@app.post("/chat")
async def chat(request: ChatRequest):
    async with MCPClientManager(config.mcp_config) as mcp_client:
        workflow = MCPAgentWorkflow(mcp_client, config.openai_model)
        
        # LangGraph 워크플로우 실행
        result = await workflow.ainvoke({
            "messages": [{"role": "user", "content": request.query}]
        })
        
        return ChatResponse(
            response=result["messages"][-1]["content"],
            used_tools=extract_used_tools(result),
            status="success"
        )
```

---

## 9. 에러 처리 및 복구

### 🛡️ **LangGraph 레벨 에러 처리**
```python
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

# 체크포인팅으로 상태 복구
checkpointer = MemorySaver()
workflow = StateGraph(MessagesState, checkpointer=checkpointer)

# 에러 처리 노드
@workflow.add_node("error_handler")
def handle_errors(state):
    # 에러 상황 처리 및 복구
    return {"messages": state["messages"], "error": "handled"}
```

### 🔄 **재시도 로직**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def mcp_tool_call(tool_name, arguments):
    # MCP 툴 호출 재시도
    pass
```

---

## 10. 개발 체크리스트

### ✅ **1단계: 기본 구조 (완료)**
- [x] 프로젝트 구조 설정 (`mcp_client/` 폴더 생성)
- [x] 기본 모듈 구현 (`config.py`, `schemas.py`)
- [x] 의존성 관리 (`requirements.txt`, `pyproject.toml`)
- [x] LangGraph 관련 패키지 추가 (`langgraph`, `langchain-mcp-adapters`)

### 🔄 **2단계: LangGraph 통합 (완료)**
- [x] **langchain-mcp-adapters** 의존성 추가
- [x] **MCPClientManager** 구현 (`mcp_client/mcp_client.py`)
  - [x] `MultiServerMCPClient` 래퍼 클래스
  - [x] 비동기 컨텍스트 매니저 구현
  - [x] 에러 처리 및 재시도 로직
- [x] **MCPAgentWorkflow** 구현 (`mcp_client/agent/workflow.py`)
  - [x] `AgentState` 정의
  - [x] `StateGraph` 구성 (노드, 엣지)
  - [x] `create_react_agent` 통합
- [x] **ReAct 에이전트** 설정
  - [x] Azure OpenAI 모델 연결
  - [x] MCP 툴을 LangChain 툴로 변환
  - [x] 워크플로우 컴파일

### 🔄 **3단계: 워크플로우 최적화**
- [ ] **상태 관리** (`MessagesState` 또는 커스텀 상태)
- [ ] **노드 구성** (에이전트, 툴 실행, 에러 처리)
- [ ] **에러 처리** 노드 및 복구 로직
- [ ] **체크포인팅** 설정 (메모리 관리)

### 🔄 **4단계: FastAPI 통합 및 테스트**
- [ ] **main.py 업데이트** (LangGraph 에이전트 통합)
- [ ] **API 엔드포인트** (`/chat`, `/health`)
- [ ] **에러 핸들링** 및 로깅
- [ ] **단위 테스트** 작성

### 🔄 **5단계: 고급 기능 (향후 고려)**
- [ ] **스트리밍** 응답
- [ ] **메모리 관리** (대화 히스토리)
- [ ] **스레드 관리** (멀티 사용자)
- [ ] **로깅 및 모니터링** 강화

### 🔄 **6단계: 배포 (향후 고려)**
- [ ] **Docker** 컨테이너화
- [ ] **환경별 설정** 관리
- [ ] **성능 테스트** 및 최적화

---

## 11. 실행 방법

### 🚀 **개발 환경 설정**
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일 편집

# 서버 실행
uvicorn mcp_client.main:app --reload --port 8081
```

### 🧪 **테스트 실행**
```bash
# 전체 테스트
pytest

# 특정 테스트
pytest tests/test_agent_flow.py -v

# 커버리지
pytest --cov=mcp_client
```

### 📡 **API 테스트**
```bash
# 헬스체크
curl http://localhost:8081/health

# 채팅 요청
curl -X POST http://localhost:8081/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"GitHub 이슈 생성해줘"}'
```

---

## 12. Git MCP 활용 가이드

### 📚 **참조 문서**
- **MCP 통합**: `docs/docs/agents/mcp.md`
- **ReAct 에이전트**: `docs/docs/how-tos/react-agent-from-scratch.ipynb`
- **상태 관리**: `docs/docs/concepts/low_level.md`
- **사전 구축 에이전트**: `docs/docs/prebuilt/`

### 🔍 **개발 시 활용 방법**
1. **LangGraph API 사용법** → 공식 문서 직접 참조
2. **워크플로우 설계** → 베스트 프랙티스 예제 참조
3. **에러 처리** → 트러블슈팅 가이드 활용
4. **성능 최적화** → 배포 및 스케일링 가이드 참조

---

## 13. 성능 최적화

### ⚡ **LangGraph 최적화**
- **노드 병렬화**: 독립적인 노드들의 병렬 실행
- **메모리 관리**: 대화 히스토리 자동 정리
- **스트리밍**: 실시간 응답 처리

### 🔧 **MCP 최적화**
- **연결 풀링**: MCP 서버 연결 재사용
- **배치 처리**: 여러 툴 호출을 한 번에 처리
- **캐싱**: 툴 목록 및 스키마 캐싱

---

## 14. 모니터링 및 로깅

### 📊 **LangGraph 모니터링**
```python
import structlog

# 구조적 로깅 설정
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()
```

### 📈 **메트릭 수집**
- 워크플로우 실행 시간
- 툴 호출 성공률
- 에러 발생 빈도
- 사용자 요청 처리량

---

## 15. 배포 및 운영 (향후 고려사항)

### 🚀 **현재: 로컬 개발 환경**
- **개발 서버**: `uvicorn mcp_client.main:app --reload --port 8081`
- **환경변수**: `.env` 파일로 관리
- **의존성**: `pip install -r requirements.txt`

### 🔧 **향후 고려사항 (배포 시)**
- **Docker**: 컨테이너화된 배포
- **환경별 설정**: 개발/스테이징/프로덕션
- **모니터링**: 로깅 및 메트릭 수집
- **확장성**: 수평적 확장 지원
