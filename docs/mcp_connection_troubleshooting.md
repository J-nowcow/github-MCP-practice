# MCP 연결 실패 트러블슈팅 가이드

## 🚨 문제 개요

**문제명**: FastAPI 앱에서 MCP 서버 연결 실패 및 ExceptionGroup 에러

**발생 시점**: FastAPI 앱 시작 시 MCP 클라이언트 초기화 과정
**에러 메시지**: 
```
MCP 서버 연결 실패: connecting_failed: ExceptionGroup
unhandled errors in a TaskGroup (1 sub-exception)
```

## 🔍 원인 분석

**근본 원인**: 
1. **포트 충돌**: 기존 uvicorn 프로세스가 포트 8081을 점유
2. **MCP 설정 구조**: `MultiServerMCPClient` 설정이 공식 문서와 일치하지 않음
3. **프로세스 관리**: 백그라운드 프로세스 정리 부족

**관련 코드**: 
- `mcp_client/main.py`: FastAPI 앱 수명주기 관리
- `mcp_client/config.py`: MCP 서버 설정 구성
- `langchain_mcp_adapters.client.MultiServerMCPClient`: MCP 클라이언트

## ✅ 해결 방법

**해결 단계**:

### 1단계: 기존 프로세스 정리
```bash
# 모든 uvicorn 프로세스 종료
pkill -f uvicorn

# 포트 사용 확인
lsof -i :8081
lsof -i :3000
```

### 2단계: MCP 설정 구조 수정
**config.py 수정**:
```python
def get_mcp_config(self) -> Dict[str, Any]:
    base_url = f"http://{self.MCP_SERVER_HOST}:{self.MCP_SERVER_PORT}{self.MCP_SERVER_PATH}"
    if not base_url.endswith("/"):
        base_url += "/"
        
    return {
        "github": {
            "transport": self.MCP_TRANSPORT,  # "streamable_http" 고정
            "url": base_url,
            "headers": {
                "Accept": "text/event-stream, application/json",
                "Content-Type": "application/json",
                "MCP-Protocol-Version": "2025-03-26"
            }
        }
    }
```

**main.py 수정**:
```python
# MultiServerMCPClient 직접 생성 (컨텍스트 매니저 불필요)
app.state.mcp_client = MultiServerMCPClient(cfg.get_mcp_config())

# 공식 문서에 따라 직접 도구 로딩
tools = await app.state.mcp_client.get_tools()
```

### 3단계: FastAPI 앱 재시작
```bash
# 가상환경 활성화
source venv/bin/activate

# FastAPI 앱 실행
python -m uvicorn mcp_client.main:app --host 0.0.0.0 --port 8081
```

## 🧪 검증 방법

**테스트 명령어**:

### 헬스체크 테스트
```bash
curl http://localhost:8081/health
```

**예상 결과**: 
```json
{
  "status": "ok",
  "details": {
    "mcp_client": {
      "status": "connected",
      "tool_count": 10,
      "client_type": "MultiServerMCPClient"
    },
    "workflow": "ready",
    "tools_available": 10
  }
}
```

### 채팅 엔드포인트 테스트
```bash
curl -X POST http://localhost:8081/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "안녕하세요!", "thread_id": "test-123"}'
```

**예상 결과**: 정상적인 AI 응답과 함께 `status: "success"`

## 📚 참고 자료

### 공식 문서
- **langchain-mcp-adapters**: [GitHub Repository](https://github.com/langchain-ai/langchain-mcp-adapters)
- **FastMCP**: [공식 문서](https://gofastmcp.com)
- **LangGraph**: [공식 문서](https://langchain-ai.github.io/langgraph/)

### 핵심 설정 가이드
```python
# ✅ 올바른 MultiServerMCPClient 사용법
client = MultiServerMCPClient({
    "github": {
        "transport": "streamable_http",
        "url": "http://127.0.0.1:3000/mcp/",
        "headers": {
            "Accept": "text/event-stream, application/json",
            "Content-Type": "application/json",
            "MCP-Protocol-Version": "2025-03-26"
        }
    }
})

# 도구 로딩 (컨텍스트 매니저 불필요)
tools = await client.get_tools()
```

## 🔄 예방 방법

**앱 시작 전 체크리스트**:
1. **포트 충돌 확인**: `lsof -i :8081` 및 `lsof -i :3000`
2. **기존 프로세스 정리**: `pkill -f uvicorn` 필요시 실행
3. **MCP 서버 상태 확인**: GitHub MCP 서버가 포트 3000에서 실행 중인지 확인
4. **설정 검증**: `config.py`의 MCP 설정이 공식 문서와 일치하는지 확인

**개발 환경 관리**:
- **가상환경 사용**: `venv` 활성화 후 실행
- **프로세스 모니터링**: `ps aux | grep uvicorn`으로 상태 확인
- **로그 모니터링**: FastAPI 앱과 MCP 서버 로그 동시 확인

## 🎯 문제 해결 요약

### **시도했던 해결 방법들**
1. ❌ **FastAPI 수명주기 수정**: `startup_event` → `lifespan` 전환
2. ❌ **MCP 클라이언트 래퍼 제거**: `MCPClientManager` → `MultiServerMCPClient` 직접 사용
3. ❌ **Import 에러 수정**: 상대 import → 절대 import 변경
4. ❌ **MCP 서버 실행**: FastMCP 기반 GitHub MCP 서버 실행
5. ✅ **포트 충돌 해결**: 기존 프로세스 정리 및 재시작

### **최종 성공 요인**
1. **프로세스 정리**: `pkill -f uvicorn`로 포트 충돌 해결
2. **설정 구조 정확성**: 공식 문서에 맞는 MCP 설정 구조
3. **순서적 실행**: MCP 서버 → FastAPI 앱 순서로 실행

---

**작성일**: 2025-09-04
**작성자**: AI Assistant
**버전**: 0.1.0
**관련 이슈**: MCP 연결 실패 및 ExceptionGroup 에러
