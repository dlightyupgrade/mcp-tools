#!/usr/bin/env python3
"""
MCP Tools Registry

Dynamic tool loader that registers all available tools with the FastMCP server.
"""

import logging
from typing import List, Dict, Any

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_all_tools(mcp: FastMCP) -> Dict[str, Any]:
    """
    Register all available tools with the FastMCP server.
    
    This function dynamically imports and registers all tool modules,
    providing a centralized way to manage tool registration.
    
    Args:
        mcp: FastMCP server instance
        
    Returns:
        Dictionary with registration results and tool information
    """
    registered_tools = []
    registration_errors = []
    
    # List of tool modules to register
    tool_modules = [
        ("pr_violations", "register_pr_violations_tool"),
        ("code_review", "register_code_review_tool"), 
        ("tech_design_review", "register_tech_design_review_tool"),
        ("jira_transition", "register_jira_transition_tool"),
        ("jira_transitions", "register_jira_transitions_tool"),
        ("system", "register_system_tools")
    ]
    
    logger.info("Starting tool registration process...")
    
    for module_name, register_function_name in tool_modules:
        try:
            # Dynamic import of tool module
            module = __import__(f"tools.{module_name}", fromlist=[register_function_name])
            
            # Get the registration function
            register_function = getattr(module, register_function_name)
            
            # Call the registration function
            register_function(mcp)
            
            registered_tools.append({
                "module": module_name,
                "register_function": register_function_name,
                "status": "success"
            })
            
            logger.info(f"Successfully registered tools from module: {module_name}")
            
        except ImportError as e:
            error_info = {
                "module": module_name,
                "register_function": register_function_name,
                "status": "import_error",
                "error": str(e)
            }
            registration_errors.append(error_info)
            logger.error(f"Failed to import module {module_name}: {e}")
            
        except AttributeError as e:
            error_info = {
                "module": module_name,
                "register_function": register_function_name,
                "status": "function_not_found",
                "error": str(e)
            }
            registration_errors.append(error_info)
            logger.error(f"Function {register_function_name} not found in module {module_name}: {e}")
            
        except Exception as e:
            error_info = {
                "module": module_name,
                "register_function": register_function_name,
                "status": "registration_error",
                "error": str(e)
            }
            registration_errors.append(error_info)
            logger.error(f"Error registering tools from module {module_name}: {e}")
    
    # Summary
    total_modules = len(tool_modules)
    successful_registrations = len(registered_tools)
    failed_registrations = len(registration_errors)
    
    logger.info(f"Tool registration complete: {successful_registrations}/{total_modules} modules successful")
    
    if registration_errors:
        logger.warning(f"Registration errors occurred in {failed_registrations} modules")
        for error in registration_errors:
            logger.warning(f"  - {error['module']}: {error['status']} - {error['error']}")
    
    return {
        "total_modules": total_modules,
        "successful_registrations": successful_registrations,
        "failed_registrations": failed_registrations,
        "registered_tools": registered_tools,
        "registration_errors": registration_errors,
        "available_tools": get_tool_list(),
        "status": "completed" if failed_registrations == 0 else "completed_with_errors"
    }


def get_tool_list() -> List[str]:
    """
    Get list of available tool names.
    
    Returns:
        List of tool names that should be available after registration
    """
    return [
        "pr_violations",
        "code_review", 
        "tech_design_review",
        "jira_transition",
        "get_jira_transitions",
        "echo",
        "get_system_info"
    ]


def get_tool_descriptions() -> Dict[str, str]:
    """
    Get descriptions of all available tools.
    
    Returns:
        Dictionary mapping tool names to their descriptions
    """
    return {
        "pr_violations": "Analyze PR violations, open review threads, CI failures, and merge conflicts",
        "code_review": "Perform comprehensive code quality review of pull requests",
        "tech_design_review": "Comprehensive technical design document review with architecture, security, and implementation analysis",
        "jira_transition": "Automatically perform JIRA ticket transitions using Atlassian MCP",
        "get_jira_transitions": "Calculate transition paths between JIRA statuses with preset shortcuts",
        "echo": "Echo text back to verify MCP connectivity",
        "get_system_info": "Get comprehensive system information and server diagnostics"
    }