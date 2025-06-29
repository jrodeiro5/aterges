"""
Base Agent Class for Aterges Platform
Abstract base class for all data agents
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all Aterges data agents
    """
    
    def __init__(self, agent_name: str, agent_description: str):
        """Initialize the base agent"""
        self.agent_name = agent_name
        self.agent_description = agent_description
        self.is_initialized = False
        self.last_error = None
        
        # Initialize the agent
        try:
            self._initialize()
            self.is_initialized = True
            logger.info(f"{self.agent_name} initialized successfully")
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Failed to initialize {self.agent_name}: {e}")
    
    @abstractmethod
    def _initialize(self):
        """Initialize agent-specific resources (credentials, clients, etc.)"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the agent
        Returns status information
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent"""
        return {
            "name": self.agent_name,
            "description": self.agent_description,
            "initialized": self.is_initialized,
            "last_error": self.last_error
        }
    
    def _handle_error(self, operation: str, error: Exception) -> Dict[str, Any]:
        """Standard error handling for agent operations"""
        error_msg = f"{self.agent_name} error in {operation}: {str(error)}"
        logger.error(error_msg)
        self.last_error = error_msg
        
        return {
            "error": True,
            "message": error_msg,
            "operation": operation,
            "agent": self.agent_name
        }
    
    def _format_success_response(self, data: Any, operation: str = None) -> Dict[str, Any]:
        """Standard success response format"""
        return {
            "success": True,
            "data": data,
            "agent": self.agent_name,
            "operation": operation
        }
