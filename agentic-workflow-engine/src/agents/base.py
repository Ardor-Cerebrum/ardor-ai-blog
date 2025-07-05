"""
Base Agent class for the Agentic Workflow Engine.

This module provides the foundational classes for all agents in the system.
Each agent inherits from the base Agent class and implements its specific logic.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Optional, Dict, TypeVar, Generic

from ..config.ai_models_config import AIConfigError

T = TypeVar('T')  # Generic type for message content

class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class ModelInitializationError(AgentError):
    """Raised when AI model initialization fails."""
    pass

class Message(Generic[T]):
    """Enhanced Message structure with AI model metadata.
    
    Attributes:
        content: The actual message content of type T
        media_type: The MIME type of the content
        timestamp: When the message was created
        model_used: The AI model used to generate the content
    """
    def __init__(
        self, 
        content: T, 
        media_type: str = "application/json", 
        model_used: Optional[str] = None
    ) -> None:
        self.content: T = content
        self.media_type: str = media_type
        self.timestamp: datetime = datetime.now()
        self.model_used: Optional[str] = model_used

    def __str__(self) -> str:
        """Return a string representation of the message."""
        return f"Message(content={self.content}, model={self.model_used})"

class Agent:
    """Enhanced Base Agent class with AI model integration.
    
    This class provides the foundation for all specialized agents in the system.
    Each agent has a name, description, and model configuration.
    
    Attributes:
        name: The agent's identifier
        description: A human-readable description of the agent's purpose
        model_config: Configuration for the AI model used by this agent
    """
    def __init__(self, name: str, description: str) -> None:
        """Initialize a new agent.
        
        Args:
            name: The agent's identifier
            description: A human-readable description of the agent's purpose
        """
        self.name: str = name
        self.description: str = description
        self.model_config: Dict[str, Any] = {"simulation_mode": True}
    
    def get_model_info(self) -> str:
        """Get current model info for display.
        
        Returns:
            A formatted string describing the current model configuration
        """
        if self.model_config.get("simulation_mode", True):
            return "🎭 Simulation Mode"
        
        model = self.model_config.get('model', 'gpt-4-1106-preview')
        if 'o4-mini' in model:
            return f"🤖 {model}"
        else:
            return f"🤖 {model} @ {self.model_config.get('temperature', 0.5)} temp"
    
    def validate_model_config(self) -> None:
        """Validate the agent's model configuration.
        
        Raises:
            ModelInitializationError: If the configuration is invalid
        """
        if not isinstance(self.model_config, dict):
            raise ModelInitializationError(
                f"Invalid model configuration for {self.name}: must be a dictionary"
            )
        
        required_fields = ["simulation_mode"]
        missing_fields = [field for field in required_fields if field not in self.model_config]
        if missing_fields:
            raise ModelInitializationError(
                f"Missing required fields in model configuration for {self.name}: {missing_fields}"
            )
    
    async def process(self, message: Message[T]) -> Message[T]:
        """Process a message (to be implemented by subclasses).
        
        Args:
            message: The input message to process
            
        Returns:
            The processed message
            
        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement process()") 