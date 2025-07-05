"""
Image Agent for the Agentic Workflow Engine.

This module provides the ImageAgent class which specializes in generating
professional images using AI image models. It supports both real AI
and simulation modes.
"""
from typing import Dict, Any, TypeVar, Optional
import asyncio
import base64
import io
import json
from pathlib import Path

from openai import AsyncOpenAI
from pydantic import BaseModel, Field, validator
from PIL import Image as PILImage

from ..config.ai_models_config import ai_config, AIProvider, AIConfigError
from .base import Agent, Message, AgentError, ModelInitializationError

T = TypeVar('T')

class ImageRequest(BaseModel):
    """Structure for image generation requests."""
    prompt: str = Field(..., description="Image generation prompt")
    style: str = Field(default="professional", description="Visual style")
    size: str = Field(default="1024x1024", description="Image dimensions")
    quality: str = Field(default="standard", description="Image quality")
    
    @validator('prompt')
    def prompt_not_empty(cls, v: str) -> str:
        """Validate that prompt is not empty."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty")
        return v.strip()
    
    @validator('size')
    def validate_size(cls, v: str) -> str:
        """Validate image size."""
        valid_sizes = ["1024x1024", "1024x1792", "1792x1024"]
        if v not in valid_sizes:
            raise ValueError(f"Size must be one of: {valid_sizes}")
        return v
    
    @validator('quality')
    def validate_quality(cls, v: str) -> str:
        """Validate image quality."""
        valid_qualities = ["standard", "hd"]
        if v not in valid_qualities:
            raise ValueError(f"Quality must be one of: {valid_qualities}")
        return v

class ImageResponse(BaseModel):
    """Structure for image generation responses."""
    image_data: str = Field(..., description="Base64 encoded image data")
    prompt_used: str = Field(..., description="Final prompt used")
    style_used: str = Field(..., description="Visual style used")
    dimensions: str = Field(..., description="Image dimensions")

class ImageAgentError(AgentError):
    """Image agent specific errors."""
    pass

class ImageAgent(Agent):
    """Image generation specialist with AI integration.
    
    This agent creates professional images using advanced AI models,
    with fallback to simulation mode when real AI is not available
    or encounters errors.
    
    Attributes:
        name: The agent's identifier
        description: Description of the agent's purpose
        model_config: Configuration for the image model
        openai_client: OpenAI API client instance
    """
    def __init__(self) -> None:
        """Initialize the image agent."""
        super().__init__("image_agent", "Creates professional images using AI image models")
        self.model_config = ai_config.image_config
        self.openai_client: Optional[AsyncOpenAI] = None
        self.validate_model_config()
    
    def validate_model_config(self) -> None:
        """Validate image agent specific configuration.
        
        Raises:
            ModelInitializationError: If the configuration is invalid
        """
        super().validate_model_config()
        if not self.model_config["simulation_mode"]:
            required_fields = ["model"]
            missing_fields = [field for field in required_fields if field not in self.model_config]
            if missing_fields:
                raise ModelInitializationError(
                    f"Missing required fields for image model configuration: {missing_fields}"
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
        """Process an image generation request.
        
        Args:
            message: Dictionary containing the image request parameters
            
        Returns:
            Dictionary containing the generated image data
            
        Raises:
            ImageAgentError: If the image generation fails
        """
        try:
            request = ImageRequest(**message)
        except Exception as e:
            raise ImageAgentError(f"Invalid image request: {e}")
        
        print(f"🎨 [ImageAgent]: Generating image using {self.get_model_info()}")
        
        # Try real AI first, fall back to simulation
        if not self.model_config.get("simulation_mode", True):
            try:
                self._init_openai_client()
                if self.openai_client:
                    image_data = await self._call_real_ai(request)
                    result = ImageResponse(
                        image_data=image_data,
                        prompt_used=request.prompt,
                        style_used=request.style,
                        dimensions=request.size
                    )
                    print("✅ [ImageAgent]: Image generation complete")
                    return result.model_dump()
            except (AIConfigError, ModelInitializationError) as e:
                print(f"⚠️ Configuration error: {e}, falling back to simulation")
            except Exception as e:
                print(f"⚠️ OpenAI API error: {e}, falling back to simulation")
        
        # Use enhanced simulation
        await asyncio.sleep(0.5)  # Simulate processing time
        image_data = b"SIMULATED_IMAGE_DATA"  # Placeholder for simulation
        result = ImageResponse(
            image_data=image_data,
            prompt_used=request.prompt,
            style_used=request.style,
            dimensions=request.size
        )
        print("✅ [ImageAgent]: Image generation complete")
        return result.model_dump()
    
    async def _call_real_ai(self, request: ImageRequest) -> str:
        """Call real OpenAI API for image generation.
        
        Args:
            request: Validated image request
            
        Returns:
            Base64 encoded image data
            
        Raises:
            ModelInitializationError: If OpenAI client is not initialized
            ImageAgentError: If the API call fails
        """
        if not self.openai_client:
            raise ModelInitializationError("OpenAI client not initialized")
        
        try:
            prompt = self._enhance_prompt(request)
            
            response = await self.openai_client.images.generate(
                model=self.model_config.get("model", "dall-e-3"),
                prompt=prompt,
                size=request.size,
                quality=request.quality,
                n=1,
                response_format="b64_json"
            )
            
            if not response.data:
                raise ImageAgentError("No image data received from API")
            
            return response.data[0].b64_json
            
        except Exception as e:
            raise ImageAgentError(f"OpenAI API call failed: {e}")
    
    def _enhance_prompt(self, request: ImageRequest) -> str:
        """Enhance the image generation prompt.
        
        Args:
            request: Validated image request
            
        Returns:
            Enhanced prompt string
        """
        style_prompts = {
            "professional": "Create a professional, high-quality image suitable for business use.",
            "modern": "Create a modern, sleek image with contemporary design elements.",
            "artistic": "Create an artistic, creative image with unique visual elements.",
            "minimalist": "Create a clean, minimalist image with essential elements only."
        }
        
        style_prompt = style_prompts.get(request.style, style_prompts["professional"])
        
        return f"""{style_prompt}

{request.prompt}

Ensure the image is:
- High quality and well-composed
- Appropriate for professional use
- Clear and visually appealing
- Consistent with requested style ({request.style})""" 