"""
Research Agent for the Agentic Workflow Engine.

This module provides the ResearchAgent class which specializes in analyzing topics
using AI research models. It supports both real AI and simulation modes.
"""
from typing import Dict, Any, TypeVar, cast
import asyncio
import json

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, Field

from ..config.ai_models_config import ai_config, AIProvider, get_enhanced_research_content, AIConfigError
from .base import Agent, Message, AgentError, ModelInitializationError

T = TypeVar('T')

class ResearchRequest(BaseModel):
    """Structure for research requests."""
    topic: str = Field(..., description="The topic to research")
    depth: int = Field(default=1, ge=1, le=3, description="Research depth (1-3)")

class ResearchResponse(BaseModel):
    """Structure for research responses."""
    title: str = Field(..., description="Analysis title")
    executive_summary: str = Field(..., description="2-3 sentence overview")
    key_points: list[str] = Field(..., min_items=3, description="Key insights")
    keywords: list[str] = Field(..., min_items=1, description="Relevant keywords")
    research_confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    methodology: str = Field(..., description="Analysis approach")

class ResearchAgentError(AgentError):
    """Research agent specific errors."""
    pass

class ResearchAgent(Agent):
    """Research specialist with AI integration.
    
    This agent analyzes topics using advanced AI models, with fallback to simulation
    mode when real AI is not available or encounters errors.
    
    Attributes:
        name: The agent's identifier
        description: Description of the agent's purpose
        model_config: Configuration for the research model
        openai_client: OpenAI API client instance
    """
    def __init__(self) -> None:
        """Initialize the research agent."""
        super().__init__("research_agent", "Analyzes topics using AI research models")
        self.model_config = ai_config.research_config
        self.openai_client: Optional[AsyncOpenAI] = None
        self.validate_model_config()
    
    def validate_model_config(self) -> None:
        """Validate research agent specific configuration.
        
        Raises:
            ModelInitializationError: If the configuration is invalid
        """
        super().validate_model_config()
        if not self.model_config["simulation_mode"]:
            required_fields = ["model", "max_completion_tokens", "temperature"]
            missing_fields = [field for field in required_fields if field not in self.model_config]
            if missing_fields:
                raise ModelInitializationError(
                    f"Missing required fields for research model configuration: {missing_fields}"
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
        """Process a research request.
        
        Args:
            message: Dictionary containing the research request parameters
            
        Returns:
            Dictionary containing the research results
            
        Raises:
            ResearchAgentError: If the research request fails
        """
        try:
            request = ResearchRequest(**message)
        except Exception as e:
            raise ResearchAgentError(f"Invalid research request: {e}")
        
        print(f"🔍 [ResearchAgent]: Analyzing '{request.topic}' using {self.get_model_info()}")
        
        # Try real AI first, fall back to simulation
        if not self.model_config.get("simulation_mode", True):
            try:
                self._init_openai_client()
                if self.openai_client:
                    result = await self._call_real_ai(request.topic)
                    print(f"✅ [ResearchAgent]: Research complete - {result['research_confidence']*100:.1f}% confidence")
                    return result
            except (AIConfigError, ModelInitializationError) as e:
                print(f"⚠️ Configuration error: {e}, falling back to simulation")
            except Exception as e:
                print(f"⚠️ OpenAI API error: {e}, falling back to simulation")
        
        # Use enhanced simulation
        await asyncio.sleep(0.5)  # Simulate processing time
        result = get_enhanced_research_content(request.topic)
        print(f"✅ [ResearchAgent]: Research complete - {result['research_confidence']*100:.1f}% confidence")
        return result
    
    async def _call_real_ai(self, topic: str) -> Dict[str, Any]:
        """Call real OpenAI API for research analysis.
        
        Args:
            topic: The topic to research
            
        Returns:
            Dictionary containing the research results
            
        Raises:
            ModelInitializationError: If OpenAI client is not initialized
            ResearchAgentError: If the API call fails
        """
        if not self.openai_client:
            raise ModelInitializationError("OpenAI client not initialized")
        
        try:
            prompt = self._create_research_prompt(topic)
            
            completion: ChatCompletion = await self.openai_client.chat.completions.create(
                model=self.model_config.get("model", "gpt-4-1106-preview"),
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a research analysis AI that returns data in JSON format. Always return valid JSON without any other text."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.model_config.get("max_completion_tokens", 1500),
                temperature=self.model_config.get("temperature", 0.3),
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse and validate JSON response
            try:
                result = json.loads(completion.choices[0].message.content)
                response = ResearchResponse(**result)
                return response.model_dump()
            except json.JSONDecodeError as e:
                raise ResearchAgentError(f"Failed to parse AI response as JSON: {e}")
            except Exception as e:
                raise ResearchAgentError(f"Invalid research response format: {e}")
            
        except Exception as e:
            raise ResearchAgentError(f"OpenAI API call failed: {e}")
    
    def _create_research_prompt(self, topic: str) -> str:
        """Create a research prompt for the AI model.
        
        Args:
            topic: The topic to research
            
        Returns:
            A formatted prompt string
        """
        return f"""Analyze the topic "{topic}" and provide comprehensive research insights.
        
        Return a JSON object with:
        - title: Comprehensive analysis title
        - executive_summary: 2-3 sentence overview
        - key_points: Array of 4-5 key insights
        - keywords: Array of relevant keywords
        - research_confidence: Confidence score (0.0-1.0)
        - methodology: Brief description of analysis approach
        
        Focus on technological, business, and strategic implications.
        
        IMPORTANT: Return ONLY the JSON object, no other text.""" 