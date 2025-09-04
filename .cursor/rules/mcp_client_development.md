# MCP Client 개발 규칙

## 🎯 목적

이 규칙은 **MCP Client (FastAPI + LangGraph)** 개발 시 반드시 따라야 할 가이드라인입니다. 
모든 개발 작업은 `.cursor/MCP_CLIENT_PLAN.md` 문서를 기반으로 진행됩니다.

## 📚 핵심 참조 문서

### **MCP_CLIENT_PLAN.md** ⭐ **필수 참조**
- **위치**: `.cursor/MCP_CLIENT_PLAN.md`
- **용도**: 모든 개발 작업의 기준 문서
- **업데이트**: 개발 진행에 따라 지속적으로 업데이트

## 🚀 개발 시작 원칙

### 1. **계획 문서 우선**
- 모든 작업 시작 전 `MCP_CLIENT_PLAN.md` 검토 필수
- 현재 진행 단계와 다음 작업 항목 확인
- 체크리스트 기반으로 작업 진행

### 2. **LangGraph 베스트 프랙티스 준수**
- LangGraph 공식 문서 기반 구현
- `langchain-mcp-adapters` 사용 (직접 JSON-RPC 구현 금지)
- `create_react_agent` + 커스텀 노드 조합 활용

### 3. **Git MCP 활용**
- LangGraph 공식 문서 참조 시 Git MCP 적극 활용
- `@resource` 명령어로 문서 직접 참조

## 📋 현재 개발 단계 (2025-09-04)

### ✅ **1단계: 기본 구조 (완료)**
- [x] 프로젝트 구조 설정 (`mcp_client/` 폴더 생성)
- [x] 기본 모듈 구현 (`config.py`, `schemas.py`)
- [x] 의존성 관리 (`requirements.txt`, `pyproject.toml`)
- [x] LangGraph 관련 패키지 추가

### 🔄 **2단계: LangGraph 통합 (진행 중)**
- [x] **langchain-mcp-adapters** 의존성 추가
- [ ] **MCPClientManager** 구현 (`mcp_client/mcp_client.py`)
- [ ] **MCPAgentWorkflow** 구현 (`mcp_client/agent/workflow.py`)
- [ ] **ReAct 에이전트** 설정

## 🛠️ 구현 가이드라인

### **MCPClientManager 구현**
```python
# 파일: mcp_client/mcp_client.py
from langchain_mcp_adapters.client import MultiServerMCPClient

class MCPClientManager:
    def __init__(self, config):
        self.config = config
        self.client = None
    
    async def __aenter__(self):
        # MultiServerMCPClient 초기화
        pass
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # 리소스 정리
        pass
```

### **MCPAgentWorkflow 구현**
```python
# 파일: mcp_client/agent/workflow.py
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

class MCPAgentWorkflow:
    def __init__(self, mcp_client, model):
        # ReAct 에이전트 생성
        pass
    
    def _build_workflow(self):
        # StateGraph 구성
        pass
```

## 🔍 코드 품질 기준

### **1. LangGraph 패턴 준수**
- `StateGraph` 사용하여 워크플로우 구성
- `MessagesState` 또는 커스텀 상태 관리
- 노드와 엣지의 명확한 분리

### **2. MCP 통합 표준**
- `langchain-mcp-adapters` 라이브러리 사용
- JSON-RPC 직접 구현 금지
- 툴 변환 자동화 활용

### **3. 에러 처리**
- 각 노드별 예외 처리
- 재시도 로직 (`tenacity` 활용)
- 사용자 친화적 에러 메시지

## 📝 개발 워크플로우

### **1. 작업 시작**
```bash
# 1. MCP_CLIENT_PLAN.md 검토
# 2. 현재 단계 확인
# 3. 다음 작업 항목 파악
# 4. 구현 시작
```

### **2. 구현 과정**
```bash
# 1. 코드 작성
# 2. 테스트 실행
# 3. 체크리스트 업데이트
# 4. MCP_CLIENT_PLAN.md 업데이트
```

### **3. 완료 확인**
```bash
# 1. 기능 테스트
# 2. 체크리스트 항목 체크
# 3. 다음 단계 준비
```

## 🚫 금지사항

### **1. LangGraph 무시**
- 직접 StateGraph 구현하지 않고 다른 방식 사용
- `create_react_agent` 대신 커스텀 에이전트 구현

### **2. MCP 통합 우회**
- `langchain-mcp-adapters` 대신 직접 JSON-RPC 구현
- MCP 툴을 수동으로 LangChain 툴로 변환

### **3. 계획 문서 무시**
- MCP_CLIENT_PLAN.md 없이 임의로 개발 진행
- 체크리스트 업데이트 누락

## 🔄 문서 업데이트 규칙

### **개발 진행 시**
- 각 단계 완료 시 체크리스트 업데이트
- 구현 과정에서 발견한 문제점 문서화
- 코드 예시 및 참고사항 추가

### **완료 후**
- 전체 체크리스트 검토
- 다음 개발 단계 계획 수립
- 변경 로그 작성

## 💡 개발 팁

### **1. LangGraph 디버깅**
- `graph.get_graph().draw_mermaid_png()` 활용
- 노드별 상태 변화 로깅
- 체크포인팅으로 상태 복구

### **2. MCP 통합 테스트**
- MCP 서버 연결 상태 확인
- 툴 목록 조회 테스트
- 툴 실행 결과 검증

### **3. 성능 최적화**
- 불필요한 LLM 호출 최소화
- MCP 서버 연결 재사용
- 메모리 사용량 모니터링

## 📖 추가 참조 자료

### **LangGraph 공식 문서**
- [LangGraph 기본 개념](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [ReAct 에이전트 구현](https://langchain-ai.github.io/langgraph/how-tos/react-agent-from-scratch/)
- [MCP 통합 가이드](https://langchain-ai.github.io/langgraph/agents/mcp/)

### **Git MCP 활용**
- LangGraph 공식 문서를 Git MCP로 직접 참조
- `@resource` 명령어로 실시간 문서 확인

---

**작성일**: 2025-09-04  
**버전**: 1.0.0  
**목적**: MCP Client 개발의 일관성과 품질 보장
