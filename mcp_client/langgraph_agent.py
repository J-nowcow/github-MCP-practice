"""
LangGraph 에이전트 구성
"""
from langgraph.prebuilt import create_react_agent
from langchain.schema.language_model import BaseLanguageModel
from langchain.tools import BaseTool


def build_agent(llm: BaseLanguageModel, tools: list[BaseTool]):
    """
    LangGraph ReAct 에이전트를 생성합니다
    
    Args:
        llm: 언어 모델
        tools: 사용할 도구 목록
        
    Returns:
        LangGraph 워크플로우
    """
    return create_react_agent(llm, tools)
