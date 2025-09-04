"""
MCP 클라이언트 설정
"""
from typing import Dict, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp_client.config import config


def build_mcp_client(cfg=None) -> MultiServerMCPClient:
    """
    MCP 클라이언트를 생성합니다
    
    Args:
        cfg: 설정 객체. None인 경우 기본 설정 사용
        
    Returns:
        MultiServerMCPClient 인스턴스
    """
    if cfg is None:
        cfg = config
    
    server_map = {
        "github": {
            "transport": cfg.MCP_TRANSPORT,
            "url": cfg.get_mcp_config()["github"]["url"],
            "headers": cfg.get_mcp_config()["github"]["headers"],
            "timeout": cfg.HTTP_TIMEOUT_SEC
        }
    }
    
    return MultiServerMCPClient(server_map)
