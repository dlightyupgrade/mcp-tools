#!/usr/bin/env python3
"""
Configuration settings for MCP Tools Server
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for centralized settings"""
    
    # Server configuration
    DEFAULT_PORT = int(os.getenv("MCP_SERVER_PORT", "8002"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # Tool configuration
    TOOL_TIMEOUT = int(os.getenv("TOOL_TIMEOUT", "300"))  # 5 minutes
    RATE_LIMIT = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    
    # Tool script paths
    PR_VIOLATIONS_SCRIPT = os.getenv("PR_VIOLATIONS_SCRIPT", "pr-violations-claude")
    CODE_REVIEW_SCRIPT = os.getenv("CODE_REVIEW_SCRIPT", "code-review-claude")
    
    # Default cloud ID for JIRA operations
    JIRA_CLOUD_ID = "credify.atlassian.net"
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """Get all configuration values as dictionary"""
        return {
            "port": cls.DEFAULT_PORT,
            "log_level": cls.LOG_LEVEL,
            "tool_timeout": cls.TOOL_TIMEOUT,
            "rate_limit": cls.RATE_LIMIT,
            "pr_violations_script": cls.PR_VIOLATIONS_SCRIPT,
            "code_review_script": cls.CODE_REVIEW_SCRIPT,
            "jira_cloud_id": cls.JIRA_CLOUD_ID
        }