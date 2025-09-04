"""
API 스키마 정의
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """채팅 요청 모델"""
    query: str = Field(..., description="사용자 질문", min_length=1)
    thread_id: Optional[str] = Field(None, description="스레드 ID (선택사항)")


class ToolCall(BaseModel):
    """MCP 툴 호출 정보"""
    name: str = Field(..., description="툴 이름")
    arguments: Dict[str, Any] = Field(..., description="툴 인자")
    result: Optional[Any] = Field(None, description="툴 실행 결과")


class ChatResponse(BaseModel):
    """채팅 응답 모델"""
    response: str = Field(..., description="AI 응답 텍스트")
    used_tools: List[ToolCall] = Field(default_factory=list, description="사용된 툴 목록")
    status: str = Field(..., description="응답 상태 (success/error)")
    trace: Optional[Dict[str, Any]] = Field(None, description="추적 정보")


class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str = Field(..., description="서비스 상태")
    details: Optional[Dict[str, Any]] = Field(None, description="상세 상태 정보")


class JsonRpcRequest(BaseModel):
    """JSON-RPC 요청 모델"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 버전")
    id: int = Field(..., description="요청 ID")
    method: str = Field(..., description="메서드 이름")
    params: Dict[str, Any] = Field(default_factory=dict, description="메서드 파라미터")


class JsonRpcResponse(BaseModel):
    """JSON-RPC 응답 모델"""
    jsonrpc: str = Field("2.0", description="JSON-RPC 버전")
    id: int = Field(..., description="요청 ID")
    result: Optional[Any] = Field(None, description="성공 응답")
    error: Optional[Dict[str, Any]] = Field(None, description="에러 정보")


class MCPTool(BaseModel):
    """MCP 툴 정보"""
    name: str = Field(..., description="툴 이름")
    description: str = Field(..., description="툴 설명")
    input_schema: Dict[str, Any] = Field(..., description="입력 스키마")


class MCPToolsListResponse(BaseModel):
    """MCP tools/list 응답"""
    tools: List[MCPTool] = Field(..., description="사용 가능한 툴 목록")


class OpenAITool(BaseModel):
    """OpenAI 툴 포맷"""
    type: str = Field("function", description="툴 타입")
    function: Dict[str, Any] = Field(..., description="함수 정보")
