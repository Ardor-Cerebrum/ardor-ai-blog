"""
Writer Agent for the Agentic Workflow Engine.

This module provides the WriterAgent class which specializes in creating
professional articles using AI writing models. It supports both real AI
and simulation modes.
"""
from typing import Dict, Any, TypeVar, Optional
import asyncio
import json

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, Field, validator

from ..config.ai_models_config import ai_config, AIProvider, get_enhanced_writing_content, AIConfigError
from .base import Agent, Message, AgentError, ModelInitializationError

T = TypeVar('T')

class WriterRequest(BaseModel):
    """Structure for writer requests."""
    title: str = Field(..., description="Article title")
    executive_summary: str = Field(..., description="Brief overview")
    key_points: list[str] = Field(..., min_items=1, description="Key points to cover")
    keywords: list[str] = Field(default_factory=list, description="Relevant keywords")
    tone: str = Field(default="professional", description="Writing tone")
    
    @validator('title')
    def title_not_empty(cls, v: str) -> str:
        """Validate that title is not empty."""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @validator('executive_summary')
    def summary_not_empty(cls, v: str) -> str:
        """Validate that summary is not empty."""
        if not v.strip():
            raise ValueError("Executive summary cannot be empty")
        return v.strip()

class WriterResponse(BaseModel):
    """Structure for writer responses."""
    article_text: str = Field(..., description="Generated article HTML")
    keywords: list[str] = Field(..., description="Used keywords")
    word_count: int = Field(..., ge=100, description="Article word count")
    writing_style: str = Field(..., description="Used writing style")

class WriterAgentError(AgentError):
    """Writer agent specific errors."""
    pass

class WriterAgent(Agent):
    """Content creation specialist with AI integration.
    
    This agent creates professional articles using advanced AI models,
    with fallback to simulation mode when real AI is not available
    or encounters errors.
    
    Attributes:
        name: The agent's identifier
        description: Description of the agent's purpose
        model_config: Configuration for the writing model
        openai_client: OpenAI API client instance
    """
    def __init__(self) -> None:
        """Initialize the writer agent."""
        super().__init__("writer_agent", "Creates professional articles using AI writing models")
        self.model_config = ai_config.writing_config
        self.openai_client: Optional[AsyncOpenAI] = None
        self.validate_model_config()
    
    def validate_model_config(self) -> None:
        """Validate writer agent specific configuration.
        
        Raises:
            ModelInitializationError: If the configuration is invalid
        """
        super().validate_model_config()
        if not self.model_config["simulation_mode"]:
            required_fields = ["model", "max_completion_tokens", "temperature"]
            missing_fields = [field for field in required_fields if field not in self.model_config]
            if missing_fields:
                raise ModelInitializationError(
                    f"Missing required fields for writer model configuration: {missing_fields}"
                )
    
    def _init_openai_client(self) -> None:
        """Initialize OpenAI client if needed.
        
        Raises:
            ModelInitializationError: If client initialization fails
        """
        if not self.openai_client and ai_config.has_valid_api_key(AIProvider.OPENAI):
            try:
                self.openai_client = AsyncOpenAI(api_key=ai_config.api_keys.get("openai"))
            except Exception as e:
                raise ModelInitializationError(f"Failed to initialize OpenAI client: {e}")
    
    async def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a writing request.
        
        Args:
            message: Dictionary containing the writing request parameters
            
        Returns:
            Dictionary containing the generated article
            
        Raises:
            WriterAgentError: If the writing request fails
        """
        try:
            request = WriterRequest(**message)
        except Exception as e:
            raise WriterAgentError(f"Invalid writing request: {e}")
        
        print(f"✍️ [WriterAgent]: Creating article using {self.get_model_info()}")
        
        # Try real AI first, fall back to simulation
        if not self.model_config.get("simulation_mode", True):
            try:
                self._init_openai_client()
                if self.openai_client:
                    article_html = await self._call_real_ai(request)
                    result = WriterResponse(
                        article_text=article_html,
                        keywords=request.keywords,
                        word_count=len(article_html.split()),
                        writing_style=request.tone
                    )
                    print(f"✅ [WriterAgent]: Article complete ({result.word_count} words)")
                    return result.model_dump()
            except (AIConfigError, ModelInitializationError) as e:
                print(f"⚠️ Configuration error: {e}, falling back to simulation")
            except Exception as e:
                print(f"⚠️ OpenAI API error: {e}, falling back to simulation")
        
        # Use enhanced simulation
        await asyncio.sleep(0.7)  # Simulate processing time
        article_html = get_enhanced_writing_content(request.model_dump())
        result = WriterResponse(
            article_text=article_html,
            keywords=request.keywords,
            word_count=len(article_html.split()),
            writing_style=request.tone
        )
        print(f"✅ [WriterAgent]: Article complete ({result.word_count} words)")
        return result.model_dump()
    
    async def _call_real_ai(self, request: WriterRequest) -> str:
        """Call real OpenAI API for content generation.
        
        Args:
            request: Validated writing request
            
        Returns:
            Generated article HTML
            
        Raises:
            ModelInitializationError: If OpenAI client is not initialized
            WriterAgentError: If the API call fails
        """
        if not self.openai_client:
            raise ModelInitializationError("OpenAI client not initialized")
        
        try:
            prompt = self._create_writing_prompt(request)
            
            completion: ChatCompletion = await self.openai_client.chat.completions.create(
                model=self.model_config.get("model", "gpt-4-1106-preview"),
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.model_config.get("max_completion_tokens", 2000),
                temperature=self.model_config.get("temperature", 0.7)
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            raise WriterAgentError(f"OpenAI API call failed: {e}")
    
    def _create_writing_prompt(self, request: WriterRequest) -> str:
        """Create a writing prompt for the AI model.
        
        Args:
            request: Validated writing request
            
        Returns:
            A formatted prompt string
        """
        return f"""Create a professional article based on this research brief:
        
        Title: {request.title}
        Executive Summary: {request.executive_summary}
        Key Points: {json.dumps(request.key_points)}
        Writing Style: {request.tone}
        
        Create a well-structured HTML article with:
        - Professional introduction
        - Detailed sections covering key points
        - Strategic recommendations
        - Compelling conclusion
        
        Target length: 400-600 words. Use {request.tone} writing style.""" 