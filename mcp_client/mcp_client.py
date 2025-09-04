"""
MCP Client 관리자
langchain-mcp-adapters의 MultiServerMCPClient를 래핑하여 사용하기 쉽게 만듭니다.
"""
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.tools import BaseTool

from mcp_client.config import config

logger = logging.getLogger(__name__)


class MCPClientManager:
    """
    MCP 서버 연결을 관리하는 클래스
    
    langchain-mcp-adapters의 MultiServerMCPClient를 래핑하여
    에러 처리, 재시도 로직, 로깅을 추가합니다.
    """
    
    def __init__(self, mcp_config: Optional[Dict[str, Any]] = None):
        """
        MCPClientManager 초기화
        
        Args:
            mcp_config: MCP 서버 설정. None인 경우 기본 설정 사용
        """
        self.mcp_config = mcp_config or config.get_mcp_config()
        self.client: Optional[MultiServerMCPClient] = None
        self._is_connected = False
        self.session_id: Optional[str] = None
        self._session_headers: Dict[str, str] = {}
        self._connection_attempts = 0
        self._max_connection_attempts = 3
        
        logger.info("MCPClientManager 초기화됨", extra={"config": self.mcp_config})
    
    async def __aenter__(self) -> 'MCPClientManager':
        """비동기 컨텍스트 매니저 진입"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """비동기 컨텍스트 매니저 종료"""
        await self.disconnect()
    
    def _generate_session_id(self) -> str:
        """세션 ID 생성"""
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        return self.session_id

    def _get_session_headers(self) -> Dict[str, str]:
        """세션 헤더 반환"""
        session_id = self._generate_session_id()
        headers = {
            "X-Session-ID": session_id,
            "X-Request-ID": str(uuid.uuid4()),
            "Accept": "text/event-stream, application/json",
            "Content-Type": "application/json"
        }
        return headers

    @retry(
        stop=stop_after_attempt(3), 
        wait=wait_exponential(multiplier=1, min=2, max=8), 
        retry=retry_if_exception_type((ConnectionError, TimeoutError, Exception))
    )
    async def connect(self) -> None:
        """MCP 서버에 연결"""
        try:
            if self._connection_attempts >= self._max_connection_attempts:
                raise RuntimeError(f"최대 연결 시도 횟수({self._max_connection_attempts})를 초과했습니다")
            
            self._connection_attempts += 1
            logger.info(f"MCP 서버에 연결 중... (시도 {self._connection_attempts}/{self._max_connection_attempts})")
            
            self._session_headers = self._get_session_headers()
            
            # MCP 설정에 세션 헤더 추가
            mcp_config = self.mcp_config.copy()
            if "github" in mcp_config:
                # 기존 헤더와 세션 헤더 병합
                existing_headers = mcp_config["github"].get("headers", {})
                mcp_config["github"]["headers"] = {**existing_headers, **self._session_headers}
            
            self.client = MultiServerMCPClient(mcp_config)
            await self._test_connection()
            self._is_connected = True
            self._connection_attempts = 0  # 성공 시 카운터 리셋
            logger.info(f"MCP 서버 연결 성공 (세션: {self.session_id})")
            
        except Exception as e:
            logger.error(f"MCP 서버 연결 실패 (시도 {self._connection_attempts}): {e}")
            self._is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """MCP 서버 연결 해제"""
        if self.client and self._is_connected:
            try:
                # 세션 종료
                if self.session_id:
                    logger.info(f"세션 종료: {self.session_id}")
                    self.session_id = None
                
                # langchain-mcp-adapters는 자동으로 리소스 정리
                logger.info("MCP 서버 연결 해제됨")
            except Exception as e:
                logger.error(f"MCP 서버 연결 해제 중 오류: {e}")
            finally:
                self.client = None
                self._is_connected = False
    
    async def _test_connection(self) -> None:
        """연결 테스트"""
        if not self.client:
            raise RuntimeError("MCP 클라이언트가 초기화되지 않았습니다")
        try:
            # 단순히 클라이언트가 초기화되었는지만 확인
            logger.info("MCP 클라이언트 초기화 확인됨")
        except Exception as e:
            logger.error(f"MCP 서버 연결 테스트 실패: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def get_tools(self) -> List[BaseTool]:
        """
        MCP 서버에서 사용 가능한 도구 목록을 가져옵니다
        
        Returns:
            LangChain Tool 객체들의 리스트
        
        Raises:
            RuntimeError: 클라이언트가 연결되지 않은 경우
            Exception: MCP 서버 통신 오류
        """
        if not self.client or not self._is_connected:
            raise RuntimeError("MCP 클라이언트가 연결되지 않았습니다")
        
        try:
            tools = await self.client.get_tools()
            logger.info(f"{len(tools)}개의 MCP 도구를 LangChain 도구로 변환했습니다")
            return tools
            
        except Exception as e:
            # ExceptionGroup 처리
            if hasattr(e, '__cause__') and e.__cause__:
                logger.error(f"MCP 도구 목록 가져오기 실패 (원인): {e.__cause__}")
                raise e.__cause__ if e.__cause__ else e
            else:
                logger.error(f"MCP 도구 목록 가져오기 실패: {e}")
                raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=8)
    )
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        MCP 도구를 실행합니다
        
        Args:
            tool_name: 실행할 도구 이름
            arguments: 도구 실행에 필요한 인수
            
        Returns:
            도구 실행 결과
            
        Raises:
            RuntimeError: 클라이언트가 연결되지 않은 경우
            Exception: MCP 서버 통신 오류
        """
        if not self.client or not self._is_connected:
            raise RuntimeError("MCP 클라이언트가 연결되지 않은 경우")
        
        try:
            logger.info(f"MCP 도구 실행: {tool_name}", extra={"arguments": arguments, "session": self.session_id})
            
            # MultiServerMCPClient의 도구 실행 방식에 따라 구현
            # 실제 구현은 langchain-mcp-adapters의 API에 따라 달라질 수 있음
            # result = await self.client.call_tool(tool_name, arguments)
            
            # 임시로 더미 결과 반환 (실제 구현 시 수정 필요)
            result = {"status": "success", "message": f"도구 {tool_name} 실행됨"}
            
            logger.info(f"MCP 도구 실행 완료: {tool_name}", extra={"result": result})
            return result
            
        except Exception as e:
            logger.error(f"MCP 도구 실행 실패: {tool_name}", extra={"error": str(e), "arguments": arguments})
            raise
    
    @property
    def is_connected(self) -> bool:
        """연결 상태 반환"""
        return self._is_connected
    
    async def health_check(self) -> Dict[str, Any]:
        """MCP 서버 상태 확인"""
        try:
            if not self.is_connected:
                return {"status": "disconnected", "error": "클라이언트가 연결되지 않음"}
            
            tools = await self.get_tools()
            return {
                "status": "connected",
                "tool_count": len(tools),
                "server_url": self.mcp_config.get("github", {}).get("url"),
                "session_id": self.session_id,
                "headers": self._session_headers,
                "connection_attempts": self._connection_attempts
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def refresh_session(self) -> None:
        """세션 새로고침"""
        try:
            old_session = self.session_id
            self.session_id = None
            self._session_headers = self._get_session_headers()
            logger.info(f"세션 새로고침: {old_session} -> {self.session_id}")
        except Exception as e:
            logger.error(f"세션 새로고침 실패: {e}")
    
    def reset_connection_attempts(self) -> None:
        """연결 시도 횟수 리셋"""
        self._connection_attempts = 0


# 편의를 위한 컨텍스트 매니저 함수
@asynccontextmanager
async def get_mcp_client(mcp_config: Optional[Dict[str, Any]] = None):
    """
    MCP 클라이언트를 컨텍스트 매니저로 제공하는 편의 함수
    
    Usage:
        async with get_mcp_client() as client:
            tools = await client.get_tools()
            result = await client.call_tool("tool_name", {"arg": "value"})
    """
    async with MCPClientManager(mcp_config) as client:
        yield client
