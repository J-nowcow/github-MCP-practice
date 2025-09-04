# mcp-github-fastmcp

GitHub MCP server built with fastMCP.

## 설치

```bash
# 가상환경 활성화
source .venv/bin/activate

# 개발 모드로 설치
pip install -e .
```

## 실행

```bash
# 가상환경 활성화
source .venv/bin/activate

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
      "cwd": "/path/to/your/project",
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

## 사용 예시

### health 툴 호출

MCP 클라이언트에서 health 툴을 호출하면 다음과 같은 응답을 받습니다:

```json
{
  "status": "ok"
}
```

## 개발

### 의존성 설치

```bash
# 개발 의존성 설치
pip install -e ".[dev]"
```

### 코드 포맷팅

```bash
# ruff로 코드 포맷팅
ruff format .

# ruff로 린팅
ruff check .
```

### 테스트

```bash
# 테스트 실행
pytest

# 커버리지와 함께 테스트
pytest --cov=mcp_github
```


