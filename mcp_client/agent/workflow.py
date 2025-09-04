"""
MCP Agent 워크플로우
LangGraph를 사용하여 ReAct 에이전트를 구성하고 MCP 도구를 통합합니다.
"""
import logging
from typing import Dict, Any, List, Optional

from langgraph.prebuilt import create_react_agent
from langchain_openai import AzureChatOpenAI
from langchain.tools import BaseTool
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

from mcp_client.config import config

logger = logging.getLogger(__name__)


class MCPAgentWorkflow:
    """
    MCP 도구를 사용하는 LangGraph ReAct 에이전트 워크플로우
    
    Azure OpenAI 모델과 MCP 도구를 통합하여 사용자 요청을 처리합니다.
    """
    
    def __init__(
        self, 
        mcp_client: MultiServerMCPClient,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None
    ):
        """
        MCPAgentWorkflow 초기화
        
        Args:
            mcp_client: MultiServerMCPClient 인스턴스
            model_name: Azure OpenAI 모델 이름 (기본값: config에서 가져옴)
            temperature: 모델 온도 (기본값: config에서 가져옴)
        """
        self.mcp_client = mcp_client
        self.model_name = model_name or config.AZURE_OPENAI_DEPLOYMENT
        self.temperature = temperature or config.OPENAI_TEMPERATURE
        
        # Azure OpenAI 모델 초기화
        self.model = self._create_model()
        
        # 워크플로우 구성
        self.graph = None  # 초기화 시점에는 None, 실행 시점에 생성
        
        logger.info(
            "MCPAgentWorkflow 초기화됨",
            model=self.model_name,
            temperature=self.temperature
        )
    
    def _create_model(self) -> AzureChatOpenAI:
        """Azure OpenAI 모델 생성"""
        return AzureChatOpenAI(
            azure_deployment=self.model_name,
            azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
            api_key=config.AZURE_OPENAI_API_KEY,
            api_version=config.AZURE_OPENAI_API_VERSION,
            temperature=self.temperature,
            max_tokens=4000
        )
    
    def _build_workflow(self, tools: List[BaseTool]):
        """도구 목록으로 워크플로우 구성"""
        try:
            logger.info(f"{len(tools)}개의 도구로 워크플로우 구성 중...")
            # create_react_agent가 자체적으로 StateGraph를 반환
            graph = create_react_agent(model=self.model, tools=tools)
            logger.info("LangGraph 워크플로우 구성 완료")
            return graph
        except Exception as e:
            logger.error(f"워크플로우 구성 실패: {e}")
            raise
    
    def _modify_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        상태 수정 함수
        
        LangGraph의 상태를 ReAct 에이전트에 맞게 조정합니다.
        
        Args:
            state: 현재 상태
            
        Returns:
            수정된 상태
        """
        # 메시지가 없는 경우 빈 리스트로 초기화
        if "messages" not in state:
            state["messages"] = []
        
        # next 필드가 없는 경우 "agent"로 설정
        if "next" not in state:
            state["next"] = "agent"
        
        return state
    
    async def invoke(self, query: str, thread_id: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        try:
            logger.info("워크플로우 실행 시작", query=query, thread_id=thread_id)
            
            # 실행 시점에 실제 도구 목록 가져오기
            tools = await self.mcp_client.get_tools()
            logger.info(f"실행 시점에 {len(tools)}개의 도구를 가져왔습니다")
            
            # 워크플로우 구성
            self.graph = self._build_workflow(tools)
            
            messages = [HumanMessage(content=query)]
            result = await self.graph.ainvoke({"messages": messages}, config={"configurable": {"thread_id": thread_id}} if thread_id else {})
            response = self._process_result(result)
            logger.info("워크플로우 실행 완료", response_length=len(response.get("messages", [])))
            return response
        except Exception as e:
            logger.error(f"워크플로우 실행 실패: {e}", query=query)
            raise
    
    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        워크플로우 실행 결과 처리
        
        Args:
            result: 원시 실행 결과
            
        Returns:
            처리된 결과
        """
        try:
            messages = result.get("messages", [])
            
            # 사용된 도구 정보 추출
            used_tools = self._extract_used_tools(messages)
            
            # 최종 응답 추출
            final_response = self._extract_final_response(messages)
            
            return {
                "response": final_response,
                "used_tools": used_tools,
                "messages": messages,
                "status": "success"
            }
            
        except Exception as e:
            logger.error("결과 처리 실패", error=str(e))
            return {
                "response": "결과 처리 중 오류가 발생했습니다",
                "error": str(e),
                "status": "error"
            }
    
    def _extract_used_tools(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """
        메시지에서 사용된 도구 정보 추출
        
        Args:
            messages: 메시지 리스트
            
        Returns:
            사용된 도구 정보 리스트
        """
        used_tools = []
        
        for i, message in enumerate(messages):
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    # 다음 메시지에서 도구 실행 결과 찾기
                    if i + 1 < len(messages) and hasattr(messages[i + 1], 'tool_call_id'):
                        tool_result = messages[i + 1].content
                        
                        used_tools.append({
                            "name": tool_call.get("name", "unknown"),
                            "arguments": tool_call.get("args", {}),
                            "result": tool_result
                        })
        
        return used_tools
    
    def _extract_final_response(self, messages: List[BaseMessage]) -> str:
        """
        최종 응답 메시지 추출
        
        Args:
            messages: 메시지 리스트
            
        Returns:
            최종 응답 텍스트
        """
        # 마지막 AI 메시지 찾기
        for message in reversed(messages):
            if isinstance(message, AIMessage) and message.content:
                return message.content
        
        return "응답을 생성할 수 없습니다"
    
    async def health_check(self) -> Dict[str, Any]:
        """워크플로우 상태 확인"""
        try:
            # MultiServerMCPClient에서 직접 도구 가져오기
            tools = await self.mcp_client.get_tools()
            tools_count = len(tools)
            
            return {
                "workflow": "ready" if self.graph else "not_initialized", 
                "model": self.model_name, 
                "mcp_client": {
                    "status": "connected",
                    "tool_count": tools_count,
                    "client_type": "MultiServerMCPClient"
                }, 
                "tools_available": tools_count
            }
        except Exception as e:
            return {"workflow": "error", "error": str(e)}
    
    def get_workflow_info(self) -> Dict[str, Any]:
        """워크플로우 정보 반환"""
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "nodes": list(self.graph.nodes.keys()) if hasattr(self.graph, 'nodes') else [],
            "checkpointer": "MemorySaver"
        }
