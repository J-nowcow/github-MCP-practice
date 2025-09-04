# MCP 서버 개발 가이드

## 🎯 개요

**Model Context Protocol (MCP)** 서버를 Python과 FastMCP로 개발하기 위한 종합 가이드입니다.

## 🏗️ 프로젝트 구조

### 기본 구조
```
project-name/
├── .cursor/                          # Cursor IDE 설정 및 가이드
├── .github/                          # GitHub Actions CI/CD
├── .venv/                            # Python 가상환경
├── docs/                             # 프로젝트 문서
├── mcp_project/                      # 메인 패키지
│   ├── __init__.py                  # 패키지 초기화
│   ├── server.py                    # MCP 서버 메인
│   ├── tools_read.py                # 읽기 전용 도구들
│   ├── tools_write.py               # 쓰기 도구들 (선택사항)
│   ├── utils.py                     # 유틸리티 함수들
│   └── client.py                    # 외부 API 클라이언트
├── tests/                            # 테스트 코드
├── .env                              # 환경 변수 (gitignore에 포함)
├── .env.example                      # 환경 변수 예시
├── .gitignore                        # Git 무시 파일
├── .pre-commit-config.yaml           # pre-commit 설정
├── .cz.toml                          # Commitizen 설정
├── Makefile                          # 프로젝트 관리 명령어
├── pyproject.toml                    # 프로젝트 설정 및 의존성
├── README.md                         # 프로젝트 설명
└── requirements.txt                  # 의존성 목록 (선택사항)
```

## 🚀 빠른 시작

### 1. 프로젝트 생성
```bash
# 프로젝트 디렉토리 생성
mkdir my-mcp-project
cd my-mcp-project

# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 기본 의존성 설치
pip install fastmcp python-dotenv rich pydantic
```

### 2. 기본 파일 생성
```bash
# 패키지 디렉토리 생성
mkdir mcp_project
touch mcp_project/__init__.py
touch mcp_project/server.py
touch mcp_project/tools.py
touch .env
touch .gitignore
touch pyproject.toml
```

### 3. 최소 MCP 서버 구현
```python
# mcp_project/server.py
from fastmcp import FastMCP

def main():
    server = FastMCP("my-mcp-server", "0.1.0")
    
    @server.tool
    def health() -> dict[str, str]:
        """Health check tool."""
        return {"status": "ok"}
    
    server.run()

if __name__ == "__main__":
    main()
```

## 🛠️ 핵심 개념

### FastMCP 아키텍처
```python
# ✅ 올바른 구조
# server.py - 도구 등록 및 서버 실행
server = FastMCP("server-name", "version")

@server.tool
def my_tool():
    return actual_implementation()

# tools.py - 실제 구현 (데코레이터 없음)
def actual_implementation():
    # 비즈니스 로직
    pass
```

### 도구 등록 패턴
```python
# ❌ 잘못된 방법
# tools.py에서 FastMCP 인스턴스 생성
mcp = FastMCP("tools")
@mcp.tool  # NameError 발생!
def my_tool():
    pass

# ✅ 올바른 방법
# server.py에서만 데코레이터 사용
@server.tool
def my_tool():
    return actual_implementation()  # tools.py의 함수 호출
```

## 📦 의존성 관리

### 필수 의존성
```toml
# pyproject.toml
[project]
dependencies = [
    "fastmcp>=2.7.0",
    "python-dotenv>=1.0.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
    "pre-commit>=3.0.0",
    "commitizen>=3.0.0"
]
```

### 가상환경 관리
```bash
# 의존성 설치
pip install -e ".[dev]"

# 개발 의존성만 설치
pip install -e ".[dev]"

# 프로덕션 의존성만 설치
pip install -e .
```

## 🧪 테스트 전략

### 테스트 구조
```python
# tests/test_tools.py
import subprocess
import time
from fastmcp import Client

async def test_mcp_tools():
    # 서버를 백그라운드에서 실행
    server_process = subprocess.Popen(
        ["python", "-m", "mcp_project.server"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(2)  # 서버 시작 대기
    
    try:
        async with Client("mcp_project/server.py") as client:
            # 도구 테스트
            result = await client.call_tool("health", {})
            assert result.data["status"] == "ok"
    finally:
        server_process.terminate()
        server_process.wait()
```

### 테스트 실행
```bash
# 전체 테스트
python -m pytest tests/

# 특정 테스트
python tests/test_tools.py

# 커버리지 포함
python -m pytest --cov=mcp_project tests/
```

## 🔧 개발 도구

### pre-commit 설정
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
  
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.0.0
    hooks:
      - id: commitizen
```

### Commitizen 설정
```toml
# .cz.toml
[tool.commitizen]
name = "cz_conventional_commits"
version = "0.1.0"
tag_format = "v$version"
```

### Makefile
```makefile
# Makefile
.PHONY: install test lint format clean

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v

lint:
	ruff check .
	mypy .

format:
	ruff format .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```

## 🚨 일반적인 문제와 해결

### ImportError: attempted relative import
```python
# ❌ 문제가 있는 코드
from .tools import my_function

# ✅ 해결 방법
from mcp_project.tools import my_function
```

### NameError: name 'mcp' is not defined
```python
# ❌ 문제가 있는 코드
@mcp.tool
def my_tool():
    pass

# ✅ 해결 방법
@server.tool
def my_tool():
    return actual_implementation()
```

### AttributeError: 'FastMCP' object has no attribute 'serve_stdio'
```python
# ❌ FastMCP 1.x 방식
server.serve_stdio()

# ✅ FastMCP 2.7+ 방식
server.run()
```

## 📚 참고 자료

- [FastMCP 공식 문서](https://gofastmcp.com)
- [MCP 프로토콜 스펙](https://modelcontextprotocol.io/)
- [Python 패키징 가이드](https://packaging.python.org/)
- [pre-commit 문서](https://pre-commit.com/)
- [Commitizen 문서](https://commitizen-tools.github.io/commitizen/)

## 🔄 개발 워크플로우

### 1. 새 기능 개발
```bash
# 기능 브랜치 생성
git checkout -b feature/new-tool

# 코드 작성 및 테스트
# ...

# 커밋
git add .
git commit -m "feat: add new tool for data processing"

# 푸시 및 PR 생성
git push origin feature/new-tool
```

### 2. 코드 품질 관리
```bash
# pre-commit 실행
pre-commit run --all-files

# 린팅 및 포맷팅
make lint
make format

# 테스트 실행
make test
```

### 3. 릴리스 준비
```bash
# 버전 업데이트
cz bump

# 태그 생성
git push --tags

# 배포
# (배포 스크립트에 따라 다름)
```

---

**작성일**: 2024-09-04
**버전**: 1.0.0
**용도**: 다른 MCP 프로젝트에서 참고용
