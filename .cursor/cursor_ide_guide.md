# Cursor IDE MCP 개발 가이드

## 🎯 개요

**Cursor IDE**에서 **Model Context Protocol (MCP)** 서버를 효율적으로 개발하기 위한 설정 및 사용법 가이드입니다.

## ⚙️ Cursor IDE 설정

### 1. MCP 서버 등록

**Cursor 설정에서 MCP 서버를 등록하여 AI 어시스턴트가 코드베이스를 이해할 수 있도록 합니다.**

#### 방법 1: 설정 파일 직접 편집
```json
// ~/.cursor/settings.json 또는 프로젝트별 .vscode/settings.json
{
  "mcp.servers": {
    "github-mcp": {
      "command": "python",
      "args": ["-m", "mcp_github.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

#### 방법 2: Cursor UI에서 설정
1. `Cmd/Ctrl + Shift + P` → "MCP: Add Server" 검색
2. 서버 정보 입력:
   - **Name**: `github-mcp`
   - **Command**: `python`
   - **Arguments**: `["-m", "mcp_github.server"]`
   - **Working Directory**: `${workspaceFolder}`

### 2. 환경 변수 설정

**GitHub API 토큰 등 민감한 정보를 안전하게 관리합니다.**

```json
// .vscode/settings.json
{
  "terminal.integrated.env.osx": {
    "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
  },
  "terminal.integrated.env.linux": {
    "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
  },
  "terminal.integrated.env.windows": {
    "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
  }
}
```

### 3. Python 인터프리터 설정

**가상환경을 사용하여 프로젝트별 의존성을 격리합니다.**

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.linting.enabled": true,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "ruff"
}
```

## 🚀 개발 워크플로우

### 1. 프로젝트 시작

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd <project-name>

# 2. 가상환경 생성 및 활성화
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. 의존성 설치
pip install -e ".[dev]"

# 4. Cursor IDE에서 프로젝트 열기
cursor .
```

### 2. AI 어시스턴트 활용

#### 코드 생성 및 수정
```
@cursor: GitHub API를 사용해서 레포지토리 정보를 가져오는 함수를 만들어줘
```

#### 코드 리뷰 및 개선
```
@cursor: 이 함수의 성능을 개선하고 에러 처리를 추가해줘
```

#### 테스트 코드 생성
```
@cursor: 이 함수에 대한 테스트 코드를 작성해줘
```

#### 문서화
```
@cursor: 이 함수에 대한 docstring을 작성해줘
```

### 3. MCP 도구 테스트

**Cursor IDE의 터미널에서 MCP 도구를 직접 테스트합니다.**

```bash
# 서버 실행
python -m mcp_github.server

# 새 터미널에서 테스트
python tests/test_tools.py
```

## 🔧 유용한 Cursor 확장 프로그램

### 필수 확장 프로그램
- **Python** - Python 언어 지원
- **Pylance** - Python 언어 서버
- **Python Test Explorer** - 테스트 실행 및 디버깅
- **GitLens** - Git 히스토리 및 변경사항 추적
- **Prettier** - 코드 포맷팅
- **Error Lens** - 인라인 에러 표시

### MCP 관련 확장 프로그램
- **MCP Client** - MCP 서버와의 통신
- **GitHub Copilot** - AI 코드 완성
- **Tabnine** - AI 코드 제안

## 📝 코드 품질 관리

### 1. Pre-commit 훅 설정

```bash
# pre-commit 설치 및 설정
pip install pre-commit
pre-commit install

# 모든 파일에 대해 실행
pre-commit run --all-files
```

### 2. 린팅 및 포맷팅

```bash
# Ruff로 린팅
ruff check .

# Ruff로 포맷팅
ruff format .

# MyPy로 타입 체크
mypy .
```

### 3. 테스트 실행

```bash
# 전체 테스트
pytest

# 커버리지 포함
pytest --cov=mcp_github

# 특정 테스트만
pytest tests/test_tools.py::test_health
```

## 🚨 문제 해결

### MCP 서버 연결 실패
```bash
# 1. 서버 상태 확인
python -m mcp_github.server

# 2. 포트 충돌 확인
lsof -i :<port>

# 3. 로그 확인
tail -f /var/log/mcp-server.log
```

### Python 가상환경 문제
```bash
# 1. 가상환경 재생성
rm -rf .venv
python -m venv .venv
source .venv/bin/activate

# 2. 의존성 재설치
pip install -r requirements.txt
# 또는
pip install -e ".[dev]"
```

### Cursor IDE 성능 문제
```json
// .vscode/settings.json
{
  "python.analysis.autoImportCompletions": false,
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.autoSearchPaths": false
}
```

## 💡 생산성 향상 팁

### 1. 키보드 단축키
- `Cmd/Ctrl + Shift + P`: 명령 팔레트
- `Cmd/Ctrl + Shift + E`: 탐색기
- `Cmd/Ctrl + Shift + G`: 소스 제어
- `Cmd/Ctrl + Shift + X`: 확장 프로그램
- `Cmd/Ctrl + Shift + F`: 검색

### 2. AI 어시스턴트 명령어
```
@cursor: 이 코드를 리팩토링해줘
@cursor: 이 함수에 대한 테스트를 작성해줘
@cursor: 이 에러를 해결해줘
@cursor: 이 기능을 구현해줘
@cursor: 코드를 최적화해줘
```

### 3. 디버깅 팁
```python
# 디버깅을 위한 로깅 추가
import logging
logging.basicConfig(level=logging.DEBUG)

# 특정 함수에 대한 로깅
logger = logging.getLogger(__name__)
logger.debug(f"Function called with args: {args}")
```

## 📚 추가 자료

- [Cursor IDE 공식 문서](https://cursor.sh/docs)
- [VS Code Python 확장 프로그램](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python 개발 환경 설정](https://docs.python.org/3/tutorial/)
- [MCP 프로토콜 스펙](https://modelcontextprotocol.io/)

---

**작성일**: 2024-09-04
**버전**: 1.0.0
**용도**: Cursor IDE에서 MCP 프로젝트 개발 시 참고
