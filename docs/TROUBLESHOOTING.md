# FastMCP 트러블슈팅 가이드

## 🚨 주요 문제와 해결 방법

### 1. `@mcp.tool` 데코레이터 오류

**문제:**
```python
@mcp.tool
def my_function():
    pass
# NameError: name 'mcp' is not defined
```

**원인:**
- `tools_read.py`에서 별도의 FastMCP 인스턴스를 만들려고 시도
- `mcp = FastMCP("github-tools")`로 인스턴스 생성 후 `@mcp.tool` 사용

**해결 방법:**
```python
# ❌ 잘못된 방법
# tools_read.py
mcp = FastMCP("github-tools")

@mcp.tool
def my_function():
    pass

# ✅ 올바른 방법
# server.py
server = FastMCP("mcp-github", "0.1.0")

@server.tool
def my_function():
    pass
```

### 2. FastMCP 버전별 메서드 차이

**문제:**
```python
# FastMCP 1.x
server.serve_stdio()

# FastMCP 2.x  
server.run()  # 기본값: STDIO
```

**해결 방법:**
```python
# FastMCP 2.7+ 권장 방식
server.run()  # 자동으로 적절한 전송 방식 선택
```

### 3. 도구 등록 방식

**권장 방식:**
```python
# server.py에서 직접 데코레이터 사용
@server.tool
def getRepo(owner: str, repo: str) -> dict[str, Any]:
    """Get repository information from GitHub."""
    return get_repo(owner, repo)  # tools_read.py의 함수 호출
```

**장점:**
- 단일 FastMCP 인스턴스로 관리
- 명확한 도구 등록 구조
- 에러 발생 시 추적 용이

## 🔧 빠른 수정 체크리스트

- [ ] `tools_read.py`에서 `@mcp.tool` 데코레이터 제거
- [ ] `server.py`에서 `@server.tool` 데코레이터 사용
- [ ] `server.run()` 메서드 사용
- [ ] 가상환경 활성화 확인

## 📚 참고 자료

- [FastMCP 공식 문서](https://gofastmcp.com)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
