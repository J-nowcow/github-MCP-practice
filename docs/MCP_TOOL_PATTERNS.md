# MCP 도구 구현 패턴 비교

이 문서는 MCP 서버에서 도구(Tools)를 구현하는 두 가지 방식을 비교합니다.

## 1. 명시적 Tool 클래스 방식

### 특징
- FastMCP의 `Tool` 클래스를 직접 사용
- 모든 설정이 명시적으로 보임
- input_schema를 세밀하게 제어 가능

### 코드 예시
```python
from fastmcp import FastMCP
from fastmcp.tools import Tool

server = FastMCP("mcp-github", "0.1.0")

server.add_tool(Tool(
    name="getRepo",
    description="Get repository information from GitHub",
    input_schema={
        "type": "object",
        "properties": {
            "owner": {"type": "string", "description": "Repository owner"},
            "repo": {"type": "string", "description": "Repository name"}
        },
        "required": ["owner", "repo"]
    },
    handler=get_repo
))
```

### 장점
- ✅ **명확성**: 모든 설정이 한 곳에 명시됨
- ✅ **유연성**: 스키마를 세밀하게 커스터마이징 가능
- ✅ **타입 안전성**: Pydantic 스키마와 연동
- ✅ **디버깅**: 문제 발생 시 원인 파악이 쉬움

### 단점
- ❌ **보일러플레이트**: 코드가 길어짐
- ❌ **중복**: 여러 도구 등록 시 반복적인 코드
- ❌ **가독성**: 함수 정의와 등록이 분리됨

## 2. 데코레이터 방식

### 특징
- `@tool` 데코레이터를 사용
- 함수 정의와 도구 등록이 한 곳에
- 자동으로 스키마 추론

### 코드 예시
```python
from fastmcp import FastMCP
from fastmcp.tools import tool

server = FastMCP("mcp-github", "0.1.0")

@tool("getRepo")
async def get_repo(owner: str, repo: str) -> Dict[str, Any]:
    """Get repository information from GitHub.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
    """
    # ... 함수 내용

# 자동으로 등록됨
```

### 장점
- ✅ **간결함**: 함수 위에 간단한 데코레이터만
- ✅ **가독성**: 함수 정의와 도구 등록이 한 곳에
- ✅ **DRY 원칙**: 중복 코드 최소화
- ✅ **Pythonic**: Python의 일반적인 패턴

### 단점
- ❌ **제한적**: 스키마 커스터마이징이 어려움
- ❌ **의존성**: 특정 프레임워크 필요
- ❌ **디버깅**: 문제 발생 시 원인 파악이 어려울 수 있음

## 3. 권장 사용법

### 명시적 방식 사용 시기
- 복잡한 input_schema가 필요한 경우
- 커스텀 검증 로직이 필요한 경우
- 타입 안전성이 중요한 경우
- 팀 프로젝트에서 명확성을 우선하는 경우

### 데코레이터 방식 사용 시기
- 간단한 도구 구현
- 빠른 프로토타이핑
- 코드 가독성을 우선하는 경우
- 표준적인 MCP 도구 구현

## 4. 현재 프로젝트 상태

**mcp-github-fastmcp**는 현재 **데코레이터 방식**을 사용합니다:

```python
@tool("getRepo")
async def get_repo(owner: str, repo: str) -> Dict[str, Any]:
    """Get repository information from GitHub."""
    # ...

@tool("listPullRequests") 
async def list_pull_requests(owner: str, repo: str, state: str = "open") -> Dict[str, Any]:
    """List pull requests for a repository."""
    # ...
```

### 장점
- 코드가 간결하고 읽기 쉬움
- 함수 정의와 도구 등록이 통합됨
- 유지보수가 용이함

### 제한사항
- 기본 스키마만 사용 (필요시 확장 가능)
- FastMCP 프레임워크에 의존적

## 5. 마이그레이션 가이드

### 명시적 방식에서 데코레이터 방식으로
1. `@tool` 데코레이터 추가
2. `server.add_tool()` 호출 제거
3. 함수 docstring에 타입 힌트 추가

### 데코레이터 방식에서 명시적 방식으로
1. `@tool` 데코레이터 제거
2. `Tool` 클래스로 명시적 등록
3. input_schema 정의

## 6. 결론

두 방식 모두 장단점이 있으며, 프로젝트의 요구사항에 따라 선택하면 됩니다.

**현재 프로젝트**에서는 **데코레이터 방식**을 선택하여:
- 코드 가독성 향상
- 유지보수성 개선
- 개발 속도 향상

을 달성했습니다.

