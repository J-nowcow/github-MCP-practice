# MCP 클라이언트 맥락 관리 시스템

## 📋 목차
1. [개요](#개요)
2. [Thread ID 시스템](#thread-id-시스템)
3. [맥락 유지 메커니즘](#맥락-유지-메커니즘)
4. [세션 관리](#세션-관리)
5. [실제 구현 예시](#실제-구현-예시)
6. [맥락 관리의 장단점](#맥락-관리의-장단점)
7. [고급 기능](#고급-기능)

## 🎯 개요

MCP(Model Context Protocol) 클라이언트는 사용자와의 대화에서 **맥락을 유지**하고 **연속성 있는 작업**을 수행할 수 있도록 설계되었습니다. 이는 단순한 명령어 실행이 아닌, **지능형 어시스턴트**로서의 역할을 가능하게 합니다.

## 🔑 Thread ID 시스템

### Thread ID란?
- **정의**: 대화의 맥락을 구분하는 고유 식별자
- **형식**: `{interface_type}_{timestamp}_{random}`
- **예시**: `web_interface_1756967195034`, `chat_interface_1756967195034`

### Thread ID 생성 방식
```javascript
// 웹 인터페이스에서의 생성
let currentThreadId = 'web_interface_' + Date.now();

// 채팅 인터페이스에서의 생성  
let currentThreadId = 'chat_interface_' + Date.now();
```

### Thread ID의 역할
1. **대화 구분**: 서로 다른 인터페이스나 세션의 대화를 분리
2. **맥락 유지**: 같은 thread_id 내에서 이전 대화 내용을 기억
3. **세션 관리**: 사용자별, 인터페이스별로 독립적인 대화 환경 제공

## 🧠 맥락 유지 메커니즘

### 1. LangGraph 워크플로우
```python
# mcp_client/agent/workflow.py
class MCPAgentWorkflow:
    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.memory = {}  # 메모리 저장소
        
    async def invoke(self, query: str, thread_id: str):
        # thread_id를 기반으로 이전 대화 내용 조회
        previous_context = self.get_context(thread_id)
        
        # 현재 쿼리와 이전 맥락을 결합하여 처리
        enhanced_query = self.enhance_with_context(query, previous_context)
        
        # MCP 도구 실행 및 결과 저장
        result = await self.execute_tools(enhanced_query)
        
        # 맥락 업데이트
        self.update_context(thread_id, query, result)
        
        return result
```

### 2. 맥락 정보 구조
```python
context_structure = {
    "thread_id": "chat_interface_1756967195034",
    "conversation_history": [
        {
            "timestamp": "2025-09-04T06:20:00Z",
            "user_query": "Git 상태 확인해줘",
            "ai_response": "현재 Git 상태는...",
            "used_tools": ["getGitStatus"],
            "tool_results": {...}
        },
        {
            "timestamp": "2025-09-04T06:20:30Z", 
            "user_query": "그럼 스테이징해줘",
            "ai_response": "변경사항을 스테이징했습니다...",
            "used_tools": ["stageAllChanges"],
            "tool_results": {...}
        }
    ],
    "current_state": {
        "git_status": "staged",
        "staged_files": ["mcp_chat_interface.html"],
        "last_commit": "abc123..."
    },
    "user_preferences": {
        "language": "ko",
        "interface_type": "chat"
    }
}
```

## 🔄 세션 관리

### 1. 세션 생명주기
```
세션 시작 → Thread ID 생성 → 맥락 초기화 → 대화 진행 → 맥락 업데이트 → 세션 종료
```

### 2. 세션 타입별 관리
```python
# 세션 타입별 다른 맥락 관리 전략
session_managers = {
    "web_interface": WebInterfaceSessionManager(),
    "chat_interface": ChatInterfaceSessionManager(),
    "api_client": APIClientSessionManager()
}

class WebInterfaceSessionManager:
    def __init__(self):
        self.sessions = {}
        self.session_timeout = 3600  # 1시간
        
    def create_session(self, thread_id):
        self.sessions[thread_id] = {
            "created_at": time.time(),
            "last_activity": time.time(),
            "context": {},
            "interface_type": "web"
        }
        
    def cleanup_expired_sessions(self):
        current_time = time.time()
        expired_sessions = [
            tid for tid, session in self.sessions.items()
            if current_time - session["last_activity"] > self.session_timeout
        ]
        
        for tid in expired_sessions:
            del self.sessions[tid]
```

### 3. 메모리 관리
```python
class ContextMemory:
    def __init__(self, max_memory_size=1000):
        self.memory = {}
        self.max_size = max_memory_size
        self.access_order = []
        
    def add_context(self, thread_id, context_data):
        if len(self.memory) >= self.max_size:
            # LRU 방식으로 오래된 맥락 제거
            oldest_thread = self.access_order.pop(0)
            del self.memory[oldest_thread]
            
        self.memory[thread_id] = context_data
        self.access_order.append(thread_id)
        
    def get_context(self, thread_id):
        if thread_id in self.memory:
            # 접근 순서 업데이트 (LRU)
            self.access_order.remove(thread_id)
            self.access_order.append(thread_id)
            return self.memory[thread_id]
        return None
```

## 💻 실제 구현 예시

### 1. 웹 인터페이스에서의 맥락 관리
```javascript
// mcp_web_interface.html
let currentThreadId = 'web_interface_' + Date.now();

async function callMCP(query) {
    const response = await fetch(`${MCP_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            query: query,
            thread_id: currentThreadId  // 맥락 유지를 위한 thread_id
        })
    });
    
    return response.json();
}
```

### 2. 채팅 인터페이스에서의 맥락 관리
```javascript
// mcp_chat_interface.html
let currentThreadId = 'chat_interface_' + Date.now();

// 연속 대화 예시
async function runFullWorkflow() {
    const message = document.getElementById('workflowMessage').value.trim();
    
    try {
        // 같은 thread_id로 연속 작업 수행
        await callMCP('Check current Git repository status');
        await callMCP('Stage all changes in the repository');
        await callMCP(`Create a commit with message: ${message}`);
        await callMCP('Push to remote repository');
        
        // AI는 이전 대화 내용을 기억하고 있어서
        // "그럼" 같은 대명사도 이해할 수 있음
    } catch (error) {
        console.error('워크플로우 실행 오류:', error);
    }
}
```

### 3. MCP 클라이언트에서의 맥락 처리
```python
# mcp_client/main.py
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # thread_id를 기반으로 워크플로우 실행
    result = await workflow.invoke(
        query=request.query,
        thread_id=request.thread_id  # 맥락 유지의 핵심
    )
    
    return ChatResponse(
        response=result.get("response", "응답을 생성할 수 없습니다"),
        used_tools=result.get("used_tools", []),
        status=result.get("status", "error"),
        trace={
            "tool_names": [tool.get("name", "unknown") for tool in result.get("used_tools", [])],
            "model_rounds": len(result.get("messages", [])),
            "thread_id": request.thread_id  # 응답에도 thread_id 포함
        }
    )
```

## 📊 맥락 관리의 장단점

### ✅ 장점
1. **연속성**: 이전 대화 내용을 기억하여 자연스러운 대화 가능
2. **효율성**: 반복적인 정보 입력 불필요
3. **사용자 경험**: 개인화된 응답과 추천 가능
4. **작업 연속성**: 복잡한 워크플로우를 단계별로 진행 가능

### ❌ 단점
1. **메모리 사용량**: 세션이 많아질수록 메모리 소모 증가
2. **보안 위험**: 민감한 정보가 맥락에 저장될 수 있음
3. **복잡성**: 맥락 관리 로직이 복잡해짐
4. **디버깅 어려움**: 맥락 관련 버그 추적이 어려움

## 🚀 고급 기능

### 1. 맥락 압축 및 요약
```python
class ContextCompressor:
    def compress_context(self, context, max_tokens=1000):
        if self.count_tokens(context) <= max_tokens:
            return context
            
        # 중요한 정보만 추출하여 압축
        compressed = {
            "current_state": context["current_state"],
            "recent_actions": context["conversation_history"][-3:],
            "summary": self.generate_summary(context["conversation_history"])
        }
        
        return compressed
        
    def generate_summary(self, conversation_history):
        # AI 모델을 사용하여 대화 내용 요약
        summary_prompt = f"다음 대화 내용을 간단히 요약해주세요: {conversation_history}"
        return self.ai_model.generate(summary_prompt)
```

### 2. 맥락 동기화
```python
class ContextSynchronizer:
    def sync_across_interfaces(self, user_id, thread_id):
        # 웹 인터페이스와 채팅 인터페이스 간 맥락 동기화
        web_context = self.get_web_context(user_id)
        chat_context = self.get_chat_context(thread_id)
        
        # 공통 정보 병합
        merged_context = self.merge_contexts(web_context, chat_context)
        
        # 모든 인터페이스에 동기화
        self.update_all_interfaces(user_id, merged_context)
```

### 3. 맥락 백업 및 복구
```python
class ContextBackup:
    def backup_context(self, thread_id):
        context = self.get_context(thread_id)
        backup_data = {
            "thread_id": thread_id,
            "timestamp": time.time(),
            "context": context,
            "checksum": self.calculate_checksum(context)
        }
        
        # 데이터베이스나 파일에 백업
        self.save_backup(backup_data)
        
    def restore_context(self, thread_id, backup_timestamp):
        backup = self.load_backup(thread_id, backup_timestamp)
        if backup and self.verify_checksum(backup):
            self.restore_context(thread_id, backup["context"])
            return True
        return False
```

## 🔍 디버깅 및 모니터링

### 1. 맥락 로깅
```python
import logging

class ContextLogger:
    def __init__(self):
        self.logger = logging.getLogger('context_manager')
        
    def log_context_change(self, thread_id, action, details):
        self.logger.info(f"Thread {thread_id}: {action} - {details}")
        
    def log_context_error(self, thread_id, error, stack_trace):
        self.logger.error(f"Thread {thread_id}: Error - {error}\n{stack_trace}")
```

### 2. 맥락 상태 모니터링
```python
class ContextMonitor:
    def get_context_stats(self):
        return {
            "total_sessions": len(self.memory),
            "active_sessions": len([s for s in self.memory.values() if s["active"]]),
            "memory_usage": self.calculate_memory_usage(),
            "oldest_session": min(self.memory.values(), key=lambda x: x["created_at"]),
            "newest_session": max(self.memory.values(), key=lambda x: x["created_at"])
        }
```

## 📝 결론

MCP 클라이언트의 맥락 관리 시스템은 **thread_id**를 핵심으로 하여 사용자와의 자연스러운 대화를 가능하게 합니다. 

### 핵심 포인트:
1. **Thread ID**: 대화 맥락을 구분하는 고유 식별자
2. **맥락 저장**: 대화 히스토리, 현재 상태, 사용자 선호도 등 저장
3. **세션 관리**: 인터페이스별, 사용자별 독립적인 세션 관리
4. **메모리 최적화**: LRU 방식으로 메모리 사용량 제어
5. **확장성**: 맥락 압축, 동기화, 백업 등 고급 기능 지원

이러한 시스템을 통해 MCP 클라이언트는 단순한 명령어 실행기가 아닌, **지능형 Git 어시스턴트**로서의 역할을 수행할 수 있습니다.
