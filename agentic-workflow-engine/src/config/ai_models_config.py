#!/usr/bin/env python3
"""
AI Models Configuration for the Agentic Workflow Engine
"""
from enum import Enum
import os
from typing import Dict, Any, Optional

class AIConfigError(Exception):
    """Base exception for AI configuration errors"""
    pass

class InvalidAPIKeyError(AIConfigError):
    """Raised when an API key is invalid or missing"""
    pass

class UnsupportedModelError(AIConfigError):
    """Raised when an unsupported model is specified"""
    pass

class AIProvider(Enum):
    """Supported AI providers"""
    SIMULATION = "simulation"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"

class AIConfig:
    """Central configuration for AI models"""
    # Supported models by provider
    SUPPORTED_MODELS = {
        "openai": {
            "chat": ["gpt-4-1106-preview", "gpt-4", "gpt-3.5-turbo"],
            "image": ["dall-e-3", "dall-e-2"]
        }
    }
    
    def __init__(self):
        self.provider = AIProvider.SIMULATION
        self.api_keys = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "anthropic": os.getenv("ANTHROPIC_API_KEY"),
            "google": os.getenv("GOOGLE_AI_API_KEY")
        }
        
        # Default configurations
        self.research_config = {
            "model": "gpt-4-1106-preview",
            "max_completion_tokens": 1500,
            "temperature": 0.3,
            "simulation_mode": True
        }
        
        self.writing_config = {
            "model": "gpt-4-1106-preview",
            "max_completion_tokens": 2000,
            "temperature": 0.7,
            "simulation_mode": True
        }
        
        self.image_config = {
            "model": "dall-e-3",
            "size": "1024x1024",
            "quality": "standard",
            "simulation_mode": True
        }
        
        # Validate initial configurations
        self._validate_configs()
    
    def _validate_configs(self) -> None:
        """Validate all model configurations"""
        self._validate_model_config("research", self.research_config)
        self._validate_model_config("writing", self.writing_config)
        self._validate_model_config("image", self.image_config)
    
    def _validate_model_config(self, agent_type: str, config: Dict[str, Any]) -> None:
        """Validate a specific model configuration"""
        if not config.get("simulation_mode"):
            model = config.get("model")
            if not model:
                raise UnsupportedModelError(f"No model specified for {agent_type} configuration")
            
            # Check if model is supported
            model_type = "image" if agent_type == "image" else "chat"
            if model not in self.SUPPORTED_MODELS["openai"][model_type]:
                raise UnsupportedModelError(
                    f"Unsupported model '{model}' for {agent_type}. "
                    f"Supported models: {self.SUPPORTED_MODELS['openai'][model_type]}"
                )
    
    def enable_real_ai(self, provider: AIProvider) -> None:
        """Enable real AI for a specific provider"""
        if not self.has_valid_api_key(provider):
            raise InvalidAPIKeyError(f"No valid API key found for {provider.value}")
        
        self.provider = provider
        self.research_config["simulation_mode"] = False
        self.writing_config["simulation_mode"] = False
        self.image_config["simulation_mode"] = False
        
        # Validate configurations after enabling real AI
        self._validate_configs()
    
    def has_valid_api_key(self, provider: AIProvider) -> bool:
        """Check if we have a valid API key for a provider"""
        key = self.api_keys.get(provider.value)
        if not key:
            return False
        
        # Basic validation
        if len(key) < 20:
            return False
            
        # Provider-specific validation
        if provider == AIProvider.OPENAI and not key.startswith(("sk-", "org-")):
            return False
        elif provider == AIProvider.ANTHROPIC and not key.startswith("sk-ant-"):
            return False
        
        return True

# Global configuration instance
ai_config = AIConfig()

def get_enhanced_research_content(topic: str) -> Dict[str, Any]:
    """Generate enhanced simulated research content"""
    return {
        "title": f"Strategic Analysis: {topic}",
        "executive_summary": f"Comprehensive analysis of {topic} reveals significant opportunities for innovation and market growth. Key technological advances and changing user behaviors are creating new possibilities for disruption and value creation.",
        "key_points": [
            f"Market adoption of {topic} technologies accelerating 45% faster than predicted",
            "Regulatory environment increasingly supportive with new frameworks",
            "Supply chain optimization creating 30-35% cost reduction opportunities",
            "Consumer trust metrics showing 82% positive sentiment",
            "Investment surge with $3.8B in new funding across sector"
        ],
        "keywords": [
            topic.lower(),
            "innovation",
            "market growth",
            "technology",
            "digital transformation",
            "strategic analysis"
        ],
        "research_confidence": 0.926,
        "methodology": "Multi-source analysis with AI-powered synthesis"
    }

def get_enhanced_writing_content(brief: Dict[str, Any]) -> str:
    """Generate enhanced simulated article content"""
    title = brief["title"]
    summary = brief["executive_summary"]
    points = brief["key_points"]
    
    article = f"""
    <h1>{title}</h1>
    
    <div class="executive-summary">
        <p>{summary}</p>
    </div>
    
    <h2>Key Strategic Insights</h2>
    <div class="key-insights">
        <ul>
            {"".join(f"<li>{point}</li>" for point in points)}
        </ul>
    </div>
    
    <h2>Detailed Analysis</h2>
    <p>Our comprehensive analysis reveals a rapidly evolving landscape with significant implications for industry leaders and innovators alike. The convergence of technological advancement and market demand is creating unprecedented opportunities for organizations that can effectively navigate this transformation.</p>
    
    <h2>Market Dynamics</h2>
    <p>The market is experiencing accelerated growth, driven by several key factors:</p>
    <ul>
        <li>Technological Innovation: Rapid advancement in core technologies</li>
        <li>Market Demand: Growing user sophistication and expectations</li>
        <li>Regulatory Support: Favorable policy frameworks emerging globally</li>
        <li>Investment Climate: Strong venture capital and corporate interest</li>
    </ul>
    
    <h2>Strategic Recommendations</h2>
    <p>Organizations should consider the following strategic initiatives:</p>
    <ol>
        <li>Invest in technological capabilities and infrastructure</li>
        <li>Build strategic partnerships across the ecosystem</li>
        <li>Focus on user experience and trust-building</li>
        <li>Develop clear regulatory compliance frameworks</li>
    </ol>
    
    <h2>Conclusion</h2>
    <p>The evolution of this space presents both challenges and opportunities. Organizations that can effectively leverage these insights while maintaining agility and innovation focus will be best positioned for success in this dynamic environment.</p>
    """
    
    return article

def setup_openai():
    """Setup OpenAI integration"""
    try:
        from openai import AsyncOpenAI
        api_key = ai_config.api_keys["openai"]
        if not api_key:
            print("❌ OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
            return False
        # OpenAI client is initialized in enhanced_demo.py
        print("✅ OpenAI integration configured")
        return True
    except ImportError:
        print("❌ OpenAI library not installed. Run: uv add openai")
        return False

def setup_anthropic():
    """Setup Anthropic (Claude) integration"""
    try:
        import anthropic
        api_key = ai_config.api_keys["anthropic"]
        if not api_key:
            print("❌ Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
            return False
        print("✅ Anthropic integration configured")
        return True
    except ImportError:
        print("❌ Anthropic library not installed. Run: uv add anthropic")
        return False

def setup_google():
    """Setup Google AI (Gemini) integration"""
    try:
        import google.generativeai as genai
        api_key = ai_config.api_keys["google"]
        if not api_key:
            print("❌ Google AI API key not found. Set GOOGLE_AI_API_KEY environment variable.")
            return False
        genai.configure(api_key=api_key)
        print("✅ Google AI integration configured")
        return True
    except ImportError:
        print("❌ Google AI library not installed. Run: uv add google-generativeai")
        return False

# Enhanced content generation for simulation mode
RESEARCH_TEMPLATES = [
    {
        "topics": ["AI", "Machine Learning", "Technology", "Automation"],
        "key_points": [
            "Advanced neural architectures enable unprecedented pattern recognition capabilities",
            "Distributed computing frameworks support massive scale AI model training",
            "Edge computing brings AI inference closer to data sources for reduced latency",
            "Federated learning preserves privacy while enabling collaborative model improvement"
        ]
    },
    {
        "topics": ["Business", "Enterprise", "Strategy", "Innovation"],
        "key_points": [
            "Digital transformation drives competitive advantage through AI-powered insights",
            "Automated decision-making systems reduce operational costs by 40-60%",
            "Customer experience personalization increases engagement metrics significantly",
            "Predictive analytics enable proactive business strategy adjustments"
        ]
    },
    {
        "topics": ["Development", "Software", "Engineering", "Architecture"],
        "key_points": [
            "Microservice architectures provide scalable, maintainable system design",
            "DevOps practices accelerate deployment cycles while maintaining reliability",
            "API-first design enables seamless integration across diverse platforms",
            "Cloud-native solutions offer elastic scalability and cost optimization"
        ]
    }
] 