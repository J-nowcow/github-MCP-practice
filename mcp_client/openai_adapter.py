"""
Azure OpenAI 모델 어댑터
"""
from langchain_openai import AzureChatOpenAI
from mcp_client.config import config


def build_llm(cfg=None) -> AzureChatOpenAI:
    """
    Azure OpenAI 모델을 생성합니다
    
    Args:
        cfg: 설정 객체. None인 경우 기본 설정 사용
        
    Returns:
        AzureChatOpenAI 인스턴스
    """
    if cfg is None:
        cfg = config
    
    return AzureChatOpenAI(
        azure_deployment=cfg.AZURE_OPENAI_DEPLOYMENT,
        azure_endpoint=cfg.AZURE_OPENAI_ENDPOINT,
        api_key=cfg.AZURE_OPENAI_API_KEY,
        api_version=cfg.AZURE_OPENAI_API_VERSION,
        temperature=cfg.OPENAI_TEMPERATURE,
        max_tokens=4000
    )
