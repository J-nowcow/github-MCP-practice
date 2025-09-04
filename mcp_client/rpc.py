"""
MCP Server JSON-RPC 클라이언트
"""
import json
import logging
from typing import Any, Dict, List, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import config
from .schemas import JsonRpcRequest, JsonRpcResponse, MCPTool

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP Server JSON-RPC 클라이언트"""
    
    def __init__(self, server_url: Optional[str] = None):
        self.server_url = server_url or config.MCP_SERVER_URL
        self.timeout = config.HTTP_TIMEOUT_SEC
        self._request_id = 0
    
    def _get_next_id(self) -> int:
        """다음 요청 ID 생성"""
        self._request_id += 1
        return self._request_id
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> JsonRpcResponse:
        """JSON-RPC 요청 실행"""
        request_id = self._get_next_id()
        request_data = JsonRpcRequest(
            id=request_id,
            method=method,
            params=params or {}
        )
        
        logger.debug(f"MCP Server 요청: {method} (ID: {request_id})")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                self.server_url,
                json=request_data.model_dump(),
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            response_data = response.json()
            rpc_response = JsonRpcResponse(**response_data)
            
            if rpc_response.error:
                logger.error(f"MCP Server 에러: {rpc_response.error}")
                raise Exception(f"MCP Server 에러: {rpc_response.error}")
            
            logger.debug(f"MCP Server 응답: {method} (ID: {request_id})")
            return rpc_response
    
    async def list_tools(self) -> List[MCPTool]:
        """사용 가능한 툴 목록 조회"""
        try:
            response = await self._make_request("tools/list")
            tools_data = response.result.get("tools", [])
            return [MCPTool(**tool) for tool in tools_data]
        except Exception as e:
            logger.error(f"툴 목록 조회 실패: {e}")
            raise
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """툴 실행"""
        try:
            params = {"name": name, "arguments": arguments}
            response = await self._make_request("tools/call", params)
            return response.result
        except Exception as e:
            logger.error(f"툴 실행 실패 {name}: {e}")
            raise
    
    async def health_check(self) -> bool:
        """MCP Server 연결 상태 확인"""
        try:
            await self._make_request("tools/list")
            return True
        except Exception as e:
            logger.error(f"MCP Server 연결 실패: {e}")
            return False
