# ImportError 트러블슈팅 가이드

## 🚨 문제 개요

**문제명**: 상대 임포트 실패로 인한 서버 크래시

**발생 시점**: FastMCP 클라이언트로 테스트 실행 시
**에러 메시지**: 
```
ImportError: attempted relative import with no known parent package
RuntimeError: Client failed to connect: Connection closed
```

## 🔍 원인 분석

**근본 원인**: `server.py`에서 상대 임포트(`from .tools_read import ...`)를 사용했지만, FastMCP 클라이언트가 파일을 직접 실행할 때 패키지 컨텍스트가 없어서 실패

**관련 코드**: `mcp_github/server.py`의 임포트 구문

## ✅ 해결 방법

**해결 단계**:
1. 상대 임포트를 절대 임포트로 변경
2. `__init__.py` 파일 존재 확인
3. 테스트 코드에서 올바른 클라이언트 연결 방식 사용

**코드 예시**:
```python
# ❌ 잘못된 방법
from .tools_read import get_repo, list_pull_requests, get_pr_diff, get_file

# ✅ 올바른 방법
from mcp_github.tools_read import get_repo, list_pull_requests, get_pr_diff, get_file
```

## 🧪 검증 방법

**테스트 명령어**:
```bash
python tests/test_tools.py
```

**예상 결과**: 모든 도구 테스트가 성공적으로 실행되고, FastMCP 클라이언트가 정상 연결됨

## 📚 참고 자료

- [FastMCP 공식 문서](https://gofastmcp.com)
- [Python 패키지 임포트 가이드](https://docs.python.org/3/reference/import.html)

## 🔄 예방 방법

**앞으로 주의사항**:
- MCP 서버 개발 시 상대 임포트보다 절대 임포트 사용
- `__init__.py` 파일이 모든 패키지 디렉토리에 존재하는지 확인
- FastMCP 클라이언트 테스트 시 서버를 별도 프로세스로 실행

---

**작성일**: 2024-09-04
**작성자**: J-nowcow
**버전**: 0.1.0
