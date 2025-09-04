# Python 프로젝트 구조 가이드

## 🎯 개요

**Python 프로젝트를 체계적으로 구성하고 관리하기 위한 표준 구조 및 모범 사례 가이드입니다.**

## 🏗️ 표준 프로젝트 구조

### 기본 구조 (소규모 프로젝트)
```
project-name/
├── .cursor/                          # Cursor IDE 설정 및 가이드
├── .github/                          # GitHub Actions CI/CD
├── .venv/                            # Python 가상환경
├── docs/                             # 프로젝트 문서
├── src/                              # 소스 코드 (선택사항)
├── project_name/                     # 메인 패키지
│   ├── __init__.py                  # 패키지 초기화
│   ├── main.py                      # 메인 실행 파일
│   ├── core/                        # 핵심 기능
│   │   ├── __init__.py
│   │   └── business_logic.py
│   ├── utils/                        # 유틸리티
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── config/                       # 설정 관리
│       ├── __init__.py
│       └── settings.py
├── tests/                            # 테스트 코드
│   ├── __init__.py
│   ├── test_core.py
│   └── test_utils.py
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

### 확장 구조 (대규모 프로젝트)
```
project-name/
├── .cursor/                          # Cursor IDE 설정
├── .github/                          # GitHub Actions
├── .venv/                            # 가상환경
├── docs/                             # 문서
│   ├── api/                         # API 문서
│   ├── guides/                      # 사용자 가이드
│   └── development/                 # 개발자 문서
├── src/                             # 소스 코드
│   └── project_name/
│       ├── __init__.py
│       ├── main.py
│       ├── api/                     # API 레이어
│       ├── core/                    # 비즈니스 로직
│       ├── data/                    # 데이터 액세스
│       ├── domain/                  # 도메인 모델
│       ├── infrastructure/          # 인프라 코드
│       └── shared/                  # 공유 유틸리티
├── tests/                            # 테스트
│   ├── unit/                        # 단위 테스트
│   ├── integration/                 # 통합 테스트
│   ├── e2e/                         # E2E 테스트
│   └── fixtures/                    # 테스트 데이터
├── scripts/                          # 스크립트
├── config/                           # 설정 파일
├── migrations/                       # 데이터베이스 마이그레이션
├── docker/                           # Docker 설정
├── kubernetes/                       # Kubernetes 설정
└── [기본 파일들...]
```

## 📦 패키지 구조 원칙

### 1. 계층 분리 (Layered Architecture)
```python
# presentation/api/controllers.py
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service
    
    def create_user(self, user_data: dict):
        return self.user_service.create_user(user_data)

# core/services.py
class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def create_user(self, user_data: dict):
        # 비즈니스 로직
        pass

# data/repositories.py
class UserRepository:
    def save(self, user: User):
        # 데이터 저장 로직
        pass
```

### 2. 의존성 주입
```python
# config/container.py
from dependency_injector import containers, providers
from core.services import UserService
from data.repositories import UserRepository

class Container(containers.DeclarativeContainer):
    user_repository = providers.Singleton(UserRepository)
    user_service = providers.Factory(UserService, user_repository=user_repository)
```

### 3. 설정 관리
```python
# config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 사용
settings = Settings()
```

## 🧪 테스트 구조

### 테스트 계층 구조
```python
# tests/unit/test_user_service.py
import pytest
from unittest.mock import Mock
from core.services import UserService

class TestUserService:
    def test_create_user_success(self):
        # Arrange
        mock_repo = Mock()
        service = UserService(mock_repo)
        user_data = {"name": "John", "email": "john@example.com"}
        
        # Act
        result = service.create_user(user_data)
        
        # Assert
        assert result.name == "John"
        mock_repo.save.assert_called_once()

# tests/integration/test_user_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user_endpoint():
    response = client.post("/users", json={"name": "John", "email": "john@example.com"})
    assert response.status_code == 201
    assert response.json()["name"] == "John"
```

### 테스트 데이터 관리
```python
# tests/fixtures/users.py
import pytest
from core.models import User

@pytest.fixture
def sample_user():
    return User(
        id=1,
        name="John Doe",
        email="john@example.com"
    )

@pytest.fixture
def user_list():
    return [
        User(id=1, name="John", email="john@example.com"),
        User(id=2, name="Jane", email="jane@example.com")
    ]
```

## 🔧 개발 도구 설정

### 1. Pre-commit 설정
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
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

### 2. Ruff 설정
```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
]
ignore = [
    "E501",  # line too long
    "B008",  # do not perform function calls in argument defaults
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### 3. MyPy 설정
```toml
# pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

[[tool.mypy.overrides]]
module = [
    "tests.*",
    "scripts.*"
]
disallow_untyped_defs = false
```

## 📚 문서화

### 1. README 구조
```markdown
# Project Name

## 🎯 개요
프로젝트에 대한 간단한 설명

## 🚀 빠른 시작
설치 및 실행 방법

## 📖 사용법
주요 기능 사용법

## 🧪 테스트
테스트 실행 방법

## 🤝 기여하기
기여 가이드

## 📄 라이선스
라이선스 정보
```

### 2. API 문서
```python
# core/models.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    """사용자 모델"""
    
    id: Optional[int] = Field(None, description="사용자 ID")
    name: str = Field(..., description="사용자 이름", min_length=1, max_length=100)
    email: str = Field(..., description="이메일 주소", regex=r"^[^@]+@[^@]+\.[^@]+$")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        }
```

## 🔄 개발 워크플로우

### 1. 기능 개발
```bash
# 1. 기능 브랜치 생성
git checkout -b feature/new-feature

# 2. 코드 작성 및 테스트
# ...

# 3. 커밋 (Conventional Commits)
git commit -m "feat: add user authentication system"

# 4. 푸시 및 PR 생성
git push origin feature/new-feature
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
make test-cov
```

### 3. 릴리스 준비
```bash
# 버전 업데이트
cz bump

# 태그 생성
git push --tags

# 배포
make deploy
```

## 🚨 일반적인 문제와 해결

### 1. 순환 임포트
```python
# ❌ 문제가 있는 코드
# user_service.py
from .user_repository import UserRepository

# user_repository.py
from .user_service import UserService

# ✅ 해결 방법
# 인터페이스 분리 또는 지연 임포트 사용
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user_service import UserService
```

### 2. 패키지 임포트 문제
```python
# ❌ 문제가 있는 코드
from .models import User  # 상대 임포트

# ✅ 해결 방법
from project_name.models import User  # 절대 임포트
```

### 3. 테스트 격리
```python
# ❌ 문제가 있는 코드
class TestUserService:
    def test_create_user(self):
        # 전역 상태에 의존
        global_user_count = 0
        # ...

# ✅ 해결 방법
class TestUserService:
    def setup_method(self):
        # 각 테스트 전에 상태 초기화
        self.user_repository = Mock()
        self.service = UserService(self.user_repository)
    
    def test_create_user(self):
        # 격리된 테스트
        # ...
```

## 📖 참고 자료

- [Python 패키징 가이드](https://packaging.python.org/)
- [Python 프로젝트 구조 모범 사례](https://docs.python-guide.org/writing/structure/)
- [FastAPI 프로젝트 구조](https://fastapi.tiangolo.com/tutorial/best-practices/)
- [Python 테스트 가이드](https://docs.pytest.org/en/stable/)
- [Python 타입 힌트](https://docs.python.org/3/library/typing.html)

---

**작성일**: 2024-09-04
**버전**: 1.0.0
**용도**: Python 프로젝트 구조 및 모범 사례 참고
