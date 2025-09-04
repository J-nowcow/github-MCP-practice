# mcp-github-fastmcp

GitHub MCP server built with fastMCP.

## 설치

```bash
# 가상환경 활성화
source .venv/bin/activate

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
      "cwd": "/Users/hyunwoo/Desktop/클테코/20250904_githubMCP",
      "env": {
        "PYTHUB_TOKEN": "your_github_token_here",
        "PYTHONPATH": "/Users/hyunwoo/Desktop/클테코/20250904_githubMCP"
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

### getRepo 툴 호출

GitHub 저장소 정보를 가져오는 예시:

```json
{
  "owner": "J-nowcow",
  "repo": "github-MCP-practice"
}
```

응답 예시:
```json
{
  "summary": "Repository: J-nowcow/github-MCP-practice\nDescription: GitHub MCP server built with fastMCP\nLanguage: Python\nStars: 0\nForks: 0\n...",
  "data": "{\n  \"id\": 123456789,\n  \"name\": \"github-MCP-practice\",\n  \"full_name\": \"J-nowcow/github-MCP-practice\",\n  ...\n}",
  "success": true
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


