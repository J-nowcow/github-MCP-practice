# 코드 품질 관리 가이드

## 🎯 개요

**코드 품질을 유지하고 향상시키기 위한 도구와 모범 사례 가이드입니다.**

## 🛠️ 핵심 도구

### 1. Linting (코드 검사)
- **Ruff**: Python 코드 검사 및 포맷팅
- **ESLint**: JavaScript/TypeScript 코드 검사
- **Pylint**: Python 코드 품질 분석

### 2. Formatting (코드 포맷팅)
- **Black**: Python 코드 포맷터
- **Prettier**: JavaScript/TypeScript 포맷터
- **isort**: Python import 정렬

### 3. Type Checking (타입 검사)
- **MyPy**: Python 타입 검사
- **TypeScript**: JavaScript 타입 검사
- **Pyright**: Python 타입 검사 (VS Code)

## 📋 코드 품질 체크리스트

### 가독성
- [ ] 함수와 변수명이 명확한가?
- [ ] 함수가 너무 길지 않은가? (20줄 이하 권장)
- [ ] 적절한 주석이 있는가?
- [ ] 코드 구조가 논리적인가?

### 성능
- [ ] 불필요한 반복문이 있는가?
- [ ] 메모리 사용량이 적절한가?
- [ ] 알고리즘 복잡도가 적절한가?

### 보안
- [ ] 입력값 검증이 있는가?
- [ ] SQL 인젝션 방지가 되어 있는가?
- [ ] 민감한 정보가 노출되지 않는가?

### 테스트
- [ ] 테스트 커버리지가 충분한가?
- [ ] 엣지 케이스가 테스트되었는가?
- [ ] 테스트가 독립적인가?

## 🔧 도구 설정 예시

### Ruff 설정
```toml
# pyproject.toml
[tool.ruff]
target-version = "py311"
line-length = 88
select = ["E", "W", "F", "I", "B", "C4"]
ignore = ["E501", "B008"]
```

### Pre-commit 설정
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
```

## 📚 모범 사례

### 1. 함수 설계
```python
# ❌ 나쁜 예시
def process_data(data, config, options, user_prefs, flags):
    # 너무 많은 매개변수
    pass

# ✅ 좋은 예시
def process_data(data: Data, config: Config) -> ProcessedData:
    """데이터를 처리하여 결과를 반환합니다."""
    return _apply_config(data, config)

def _apply_config(data: Data, config: Config) -> ProcessedData:
    """설정을 적용하여 데이터를 처리합니다."""
    pass
```

### 2. 에러 처리
```python
# ❌ 나쁜 예시
def divide(a, b):
    return a / b  # ZeroDivisionError 발생 가능

# ✅ 좋은 예시
def divide(a: float, b: float) -> float:
    """두 숫자를 나눕니다."""
    if b == 0:
        raise ValueError("0으로 나눌 수 없습니다.")
    return a / b
```

### 3. 테스트 작성
```python
# ❌ 나쁜 예시
def test_divide():
    assert divide(10, 2) == 5  # 기본 케이스만

# ✅ 좋은 예시
def test_divide_success():
    assert divide(10, 2) == 5
    assert divide(0, 5) == 0
    assert divide(-10, 2) == -5

def test_divide_by_zero():
    with pytest.raises(ValueError, match="0으로 나눌 수 없습니다"):
        divide(10, 0)
```

## 🚨 일반적인 문제

### 1. 순환 임포트
```python
# ❌ 문제가 있는 코드
# module_a.py
from .module_b import function_b

# module_b.py
from .module_a import function_a

# ✅ 해결 방법
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .module_a import function_a
```

### 2. 긴 함수
```python
# ❌ 문제가 있는 코드
def process_user_data(user_data):
    # 50줄 이상의 복잡한 로직
    pass

# ✅ 해결 방법
def process_user_data(user_data: UserData) -> ProcessedUserData:
    """사용자 데이터를 처리합니다."""
    validated_data = validate_user_data(user_data)
    enriched_data = enrich_user_data(validated_data)
    return ProcessedUserData(enriched_data)

def validate_user_data(user_data: UserData) -> ValidatedUserData:
    """사용자 데이터를 검증합니다."""
    pass

def enrich_user_data(user_data: ValidatedUserData) -> EnrichedUserData:
    """사용자 데이터를 보강합니다."""
    pass
```

## 🔄 지속적 개선

### 1. 정기적인 코드 리뷰
- 주간 코드 품질 검토
- 팀 코드 스타일 가이드 업데이트
- 새로운 도구 도입 검토

### 2. 메트릭 모니터링
- 코드 복잡도 측정
- 테스트 커버리지 추적
- 기술 부채 관리

### 3. 교육 및 훈련
- 코드 품질 워크샵
- 도구 사용법 교육
- 모범 사례 공유

---

**작성일**: 2024-09-04
**버전**: 1.0.0
**용도**: 코드 품질 관리 및 모범 사례 참고
