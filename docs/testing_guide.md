# GitHub MCP 도구 테스트 가이드

## 🧪 테스트 개요

**목적**: GitHub MCP 서버의 모든 도구가 정상 작동하는지 확인
**테스트 방식**: FastMCP 클라이언트를 사용한 통합 테스트
**테스트 대상**: 5개 도구 (health, getRepo, listPullRequests, getPRDiff, getFile)

## 🚀 테스트 실행 방법

### 1. 기본 테스트 실행

```bash
# 가상환경 활성화
source .venv/bin/activate

# 테스트 실행
python tests/test_tools.py
```

### 2. 개별 도구 테스트

```bash
# 서버만 실행 (백그라운드)
python -m mcp_github.server &

# Python 인터프리터에서 개별 테스트
python
```

```python
from fastmcp import Client
import asyncio

async def test_single_tool():
    async with Client("mcp_github/server.py") as client:
        # health 도구만 테스트
        result = await client.call_tool("health", {})
        print(f"Health check: {result.data}")

# 실행
asyncio.run(test_single_tool())
```

## ✅ 정상 실행 예시

### 테스트 시작
```
🧪 GitHub MCP 도구 테스트 시작...
🚀 MCP 서버 시작 중...
```

### FastMCP 서버 시작
```
╭────────────────────────────────────────────────────────────────────────────╮
│                                                                            │
│        _ __ ___  _____           __  __  _____________    ____    ____     │
│       _ __ ___ .'____/___ ______/ /_/  |/  / ____/ __ \  |___ \  / __ \    │
│      _ __ ___ / /_  / __ `/ ___/ __/ /|_/ / /   / /_/ /  ___/ / / / / /    │
│     _ __ ___ / __/ / /_/ (__  ) /_/ /  / / /___/ ____/  /  __/_/ /_/ /     │
│    _ __ ___ /_/    \____/____/\__/_/  /_/\____/_/      /_____(*)____/      │
│                                                                            │
│                                                                            │
│                                FastMCP  2.0                                │
│                                                                            │
│                                                                            │
│                 🖥️  Server name:     mcp-github                             │
│                 📦 Transport:       STDIO                                  │
│                                                                            │
│                 🏎️  FastMCP version: 2.12.2                                 │
│                 🤝 MCP SDK version: 1.13.1                                 │
│                                                                            │
│                 📚 Docs:            https://gofastmcp.com                  │
│                 🚀 Deploy:          https://fastmcp.cloud                  │
│                                                                            │
╰────────────────────────────────────────────────────────────────────────────╯

[09/04/25 11:12:25] INFO     Starting MCP server 'mcp-github' with transport 'stdio'
```

### 도구 목록 확인
```
1️⃣ 도구 목록 확인:
   📋 등록된 도구 수: 5
   🛠️  도구 목록: ['health', 'getRepo', 'listPullRequests', 'getPRDiff', 'getFile']
```

### 각 도구 테스트 결과
```
2️⃣ health 도구 테스트:
   ✅ health 성공: {'status': 'ok'}

3️⃣ getRepo 도구 테스트:
   ✅ getRepo 성공
   📝 요약: Repository: J-nowcow/github-MCP-practice
Description: GitHub MCP server built with fastMCP
Language:...

4️⃣ listPullRequests 도구 테스트:
   ✅ listPullRequests 성공
   📊 PR 개수: 1개

5️⃣ getPRDiff 도구 테스트:
   ✅ getPRDiff 성공
   📁 변경된 파일: 1개

6️⃣ getFile 도구 테스트:
   ✅ getFile 성공
   📄 파일 크기: 2142 bytes
```

### 테스트 완료
```
🛑 MCP 서버 종료 중...
🎯 모든 도구 테스트 완료!
```

## 🔧 테스트 코드 구조

### 주요 구성 요소

1. **서버 프로세스 관리**: `subprocess.Popen`으로 백그라운드 실행
2. **FastMCP 클라이언트**: `Client("mcp_github/server.py")`로 연결
3. **도구 호출**: `await client.call_tool("도구명", 매개변수)`
4. **결과 검증**: 각 도구의 응답 데이터 확인
5. **정리**: 서버 프로세스 종료

### 테스트 도구별 매개변수

```python
# health
await client.call_tool("health", {})

# getRepo
await client.call_tool("getRepo", {
    "owner": "J-nowcow",
    "repo": "github-MCP-practice"
})

# listPullRequests
await client.call_tool("listPullRequests", {
    "owner": "J-nowcow",
    "repo": "github-MCP-practice",
    "state": "open"
})

# getPRDiff
await client.call_tool("getPRDiff", {
    "owner": "J-nowcow",
    "repo": "github-MCP-practice",
    "number": 1
})

# getFile
await client.call_tool("getFile", {
    "owner": "J-nowcow",
    "repo": "github-MCP-practice",
    "path": "README.md",
    "ref": "HEAD"
})
```

## 🚨 문제 해결

### 일반적인 문제들

1. **ImportError**: `server.py`의 임포트 문제 → 절대 임포트 사용
2. **Connection closed**: 서버가 크래시 → 서버 로그 확인
3. **Timeout**: GitHub API 응답 지연 → 네트워크 상태 확인

### 디버깅 방법

```bash
# 서버 로그 확인
python -m mcp_github.server

# 개별 도구 테스트
python -c "
import asyncio
from mcp_github.tools_read import get_repo
result = asyncio.run(get_repo('J-nowcow', 'github-MCP-practice'))
print(result)
"
```

## 📚 참고 자료

- [FastMCP 클라이언트 문서](https://gofastmcp.com/docs/client)
- [MCP 프로토콜 스펙](https://modelcontextprotocol.io/)
- [GitHub API 문서](https://docs.github.com/en/rest)

---

**작성일**: 2024-09-04
**작성자**: J-nowcow
**버전**: 0.1.0
