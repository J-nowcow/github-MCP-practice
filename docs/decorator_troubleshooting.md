# FastMCP 데코레이터 트러블슈팅 가이드

## 🚨 문제 개요

**문제명**: `@mcp.tool` 데코레이터 사용 시 NameError 발생

**발생 시점**: FastMCP 서버에서 도구 등록 시
**에러 메시지**: 
```
NameError: name 'mcp' is not defined
TypeError: 'module' object is not callable
```

## 🔍 원인 분석

**근본 원인**: 
1. `tools_read.py`에서 별도의 FastMCP 인스턴스를 만들려고 시도
2. `@mcp.tool` 데코레이터 사용 시 `mcp` 변수가 정의되지 않음
3. FastMCP 버전별 메서드 차이 (`serve_stdio` vs `run`)

**관련 코드**: `mcp_github/tools_read.py`와 `mcp_github/server.py`

## ✅ 해결 방법

**해결 단계**:
1. `tools_read.py`에서 `@mcp.tool` 데코레이터 제거
2. `server.py`에서 `@server.tool` 데코레이터 사용
3. `server.run()` 메서드 사용 (FastMCP 2.7+)

**코드 예시**:
```python
# ❌ 잘못된 방법
# tools_read.py
mcp = FastMCP("github-tools")

@mcp.tool
def my_function():
    pass

# server.py
server.serve_stdio()  # FastMCP 1.x 방식

# ✅ 올바른 방법
# tools_read.py - 데코레이터 없이 일반 함수
async def my_function():
    pass

# server.py
@server.tool
def my_function():
    return my_function()  # tools_read.py의 함수 호출

server.run()  # FastMCP 2.7+ 방식
```

## 🧪 검증 방법

**테스트 명령어**:
```bash
python -m mcp_github.server  # 서버 실행
python tests/test_tools.py    # 도구 테스트
```

**예상 결과**: 서버가 정상 시작되고, 모든 도구가 등록되어 테스트 성공

## 📚 참고 자료

- [FastMCP 공식 문서](https://gofastmcp.com)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [MCP 도구 등록 가이드](https://gofastmcp.com/docs/tools)

## 🔄 예방 방법

**앞으로 주의사항**:
- `tools_read.py`에는 데코레이터를 사용하지 말고 일반 함수로 구현
- `server.py`에서만 `@server.tool` 데코레이터 사용
- FastMCP 버전에 맞는 메서드 사용 (`server.run()`)
- 단일 FastMCP 인스턴스로 관리

---

**작성일**: 2024-09-04
**작성자**: J-nowcow
**버전**: 0.1.0
