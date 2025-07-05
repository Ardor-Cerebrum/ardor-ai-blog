#!/usr/bin/env python3
"""
Enhanced Agentic Workflow Engine with Real AI Model Integration
"""
import asyncio
import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional

from openai import AsyncOpenAI

# Import our AI configuration system
from src.config.ai_models_config import (
    ai_config, AIProvider, 
    get_enhanced_research_content, 
    get_enhanced_writing_content
)

# Initialize OpenAI client globally
openai_client = None

def init_openai_client():
    """Initialize the OpenAI client with the current API key"""
    global openai_client
    openai_client = AsyncOpenAI(api_key=ai_config.api_keys.get("openai"))

class Message:
    """Enhanced Message structure with AI model metadata"""
    def __init__(self, content: Any, media_type: str = "application/json", model_used: Optional[str] = None):
        self.content = content
        self.media_type = media_type
        self.timestamp = datetime.now()
        self.model_used = model_used

class Agent:
    """Enhanced Base Agent class with AI model integration"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.model_config = {"simulation_mode": True}
    
    def get_model_info(self) -> str:
        """Get current model info for display"""
        if self.model_config.get("simulation_mode", True):
            return f"🎭 Simulation Mode (Production: {self.model_config.get('model', 'o4-mini-2025-04-16')})"
        
        model = self.model_config.get('model', 'o4-mini-2025-04-16')
        # Only show temperature for models that support it (not o4-mini)
        if 'o4-mini' in model:
            return f"🤖 {model}"
        else:
            return f"🤖 {model} @ {self.model_config.get('temperature', 0.5)} temp"

class ResearchAgent(Agent):
    """Enhanced Research specialist with AI integration"""
    def __init__(self):
        super().__init__("research_agent", "Analyzes topics using AI research models")
        self.model_config = ai_config.research_config  # Use AI config settings
    
    async def process(self, message: Message) -> Message:
        topic = message.content["topic"]
        model_info = self.get_model_info()
        print(f"🔍 [ResearchAgent]: Analyzing '{topic}' using {model_info}")
        
        # Try real AI first, fall back to simulation
        if not self.model_config.get("simulation_mode", True) and ai_config.has_valid_api_key(AIProvider.OPENAI):
            try:
                brief = await self._call_real_ai(topic)
                model_used = f"{self.model_config.get('model', 'o4-mini-2025-04-16')}"
            except Exception as e:
                print(f"⚠️ OpenAI API error: {e}, falling back to simulation")
                brief = get_enhanced_research_content(topic)
                model_used = "Enhanced Simulation"
        else:
            # Use enhanced simulation
            await asyncio.sleep(0.5)
            brief = get_enhanced_research_content(topic)
            model_used = "Enhanced Simulation"
        
        print(f"✅ [ResearchAgent]: Research complete - {brief['research_confidence']*100:.1f}% confidence")
        return Message(brief, model_used=model_used)
    
    async def _call_real_ai(self, topic: str) -> Dict[str, Any]:
        """Call real OpenAI API for research analysis"""
        try:
            prompt = f"""Analyze the topic "{topic}" and provide comprehensive research insights.
            
            Return a JSON object with:
            - title: Comprehensive analysis title
            - executive_summary: 2-3 sentence overview
            - key_points: Array of 4-5 key insights
            - keywords: Array of relevant keywords
            - research_confidence: Confidence score (0.0-1.0)
            - methodology: Brief description of analysis approach
            
            Focus on technological, business, and strategic implications.
            
            IMPORTANT: Return ONLY the JSON object, no other text."""
            
            completion = await openai_client.chat.completions.create(
                model=self.model_config.get("model", "o4-mini-2025-04-16"),
                messages=[
                    {"role": "system", "content": "You are a research analysis AI that returns data in JSON format. Always return valid JSON without any other text."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=self.model_config.get("max_completion_tokens", 1500),
                response_format={"type": "json_object"}  # Force JSON response
            )
            
            # Parse JSON response
            result = json.loads(completion.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Real AI error: {e}")
            raise e

class WriterAgent(Agent):
    """Enhanced Content creation specialist with AI integration"""
    def __init__(self):
        super().__init__("writer_agent", "Creates professional articles using AI writing models")
        self.model_config = ai_config.writing_config  # Use AI config settings
    
    async def process(self, message: Message) -> Message:
        brief = message.content
        model_info = self.get_model_info()
        print(f"✍️ [WriterAgent]: Creating article using {model_info}")
        
        # Try real AI first, fall back to simulation
        if not self.model_config.get("simulation_mode", True) and ai_config.has_valid_api_key(AIProvider.OPENAI):
            try:
                article_html = await self._call_real_ai(brief)
                model_used = f"{self.model_config.get('model', 'o4-mini-2025-04-16')}"
            except Exception as e:
                print(f"⚠️ OpenAI API error: {e}, falling back to simulation")
                article_html = get_enhanced_writing_content(brief)
                model_used = "Enhanced Simulation"
        else:
            # Use enhanced simulation
            await asyncio.sleep(0.7)
            article_html = get_enhanced_writing_content(brief)
            model_used = "Enhanced Simulation"
        
        result = {
            "article_text": article_html,
            "keywords": brief.get("keywords", []),
            "word_count": len(article_html.split()),
            "writing_style": "professional"
        }
        
        print(f"✅ [WriterAgent]: Article complete ({result['word_count']} words)")
        return Message(result, model_used=model_used)
    
    async def _call_real_ai(self, brief: Dict[str, Any]) -> str:
        """Call real OpenAI API for content generation"""
        try:
            prompt = f"""Create a professional article based on this research brief:
            
            Title: {brief['title']}
            Executive Summary: {brief['executive_summary']}
            Key Points: {json.dumps(brief['key_points'])}
            
            Create a well-structured HTML article with:
            - Professional introduction
            - Detailed sections covering key points
            - Strategic recommendations
            - Compelling conclusion
            
            Target length: 400-600 words. Use professional business writing style."""
            
            completion = await openai_client.chat.completions.create(
                model=self.model_config.get("model", "o4-mini-2025-04-16"),
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=self.model_config.get("max_completion_tokens", 2000)
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Real AI error: {e}")
            raise e

class ImageAgent(Agent):
    """Enhanced Image generation specialist with AI integration"""
    def __init__(self):
        super().__init__("image_agent", "Generates images using AI image models")
        self.model_config = ai_config.image_config  # Use AI config settings
    
    async def process(self, message: Message) -> Message:
        keywords = message.content.get("keywords", [])
        model_info = self.get_model_info()
        print(f"🎨 [ImageAgent]: Creating image using {model_info}")
        
        # Try real AI first, fall back to simulation
        if not self.model_config.get("simulation_mode", True) and ai_config.has_valid_api_key(AIProvider.OPENAI):
            try:
                result = await self._call_real_ai(keywords)
                model_used = "dall-e-3"
            except Exception as e:
                print(f"⚠️ DALL-E API error: {e}, falling back to simulation")
                result = self._generate_simulation_image(keywords)
                model_used = "Enhanced Simulation"
        else:
            # Use enhanced simulation
            await asyncio.sleep(0.3)
            result = self._generate_simulation_image(keywords)
            model_used = "Enhanced Simulation"
        
        print(f"✅ [ImageAgent]: Image generated - {result['image_url']}")
        return Message(result, model_used=model_used)
    
    def _generate_simulation_image(self, keywords: List[str]) -> Dict[str, Any]:
        """Generate simulation image using Picsum"""
        import hashlib
        keyword_text = " ".join(keywords[:3])
        seed = hashlib.md5(keyword_text.encode()).hexdigest()[:12]
        
        return {
            "image_url": f"https://picsum.photos/seed/{seed}/800/400",
            "alt_text": f"Professional illustration representing {keyword_text}",
            "dimensions": "800x400",
            "format": "JPEG",
            "generation_method": "Procedural (DALL-E 3 Ready)"
        }
    
    async def _call_real_ai(self, keywords: List[str]) -> Dict[str, Any]:
        """Call real OpenAI DALL-E API for image generation"""
        try:
            prompt = f"Professional, modern illustration representing {', '.join(keywords[:3])}, suitable for business article header, clean design, high quality"
            
            response = await openai_client.images.generate(
                model=self.model_config.get("model", "dall-e-3"),
                prompt=prompt,
                size=self.model_config.get("size", "1024x1024"),
                quality=self.model_config.get("quality", "standard"),
                n=1
            )
            
            return {
                "image_url": response.data[0].url,
                "alt_text": f"AI-generated illustration: {prompt}",
                "dimensions": self.model_config.get("size", "1024x1024"),
                "format": "PNG",
                "generation_method": "OpenAI DALL-E 3"
            }
            
        except Exception as e:
            print(f"Real AI error: {e}")
            raise e

class OrchestratorAgent(Agent):
    """Enhanced orchestrator with AI model awareness"""
    def __init__(self):
        super().__init__("orchestrator_agent", "Orchestrates AI-powered content workflow")
        self.research_agent = ResearchAgent()
        self.writer_agent = WriterAgent()
        self.image_agent = ImageAgent()
    
    async def process(self, topic: str) -> Message:
        print(f"\n🎬 [Orchestrator]: Starting AI-powered workflow for: '{topic}'")
        print("="*70)
        
        # Show AI model configuration
        self._display_ai_config()
        
        # Execute workflow
        print(f"\n📋 Step 1: AI Research Analysis")
        research_input = Message({"topic": topic})
        research_result = await self.research_agent.process(research_input)
        
        print(f"\n📋 Step 2: AI Content Generation")
        writer_result = await self.writer_agent.process(research_result)
        
        print(f"\n📋 Step 3: AI Image Creation")
        image_input = Message({"keywords": writer_result.content["keywords"]})
        image_result = await self.image_agent.process(image_input)
        
        print(f"\n📋 Step 4: Final Assembly & Metadata")
        final_html = self._create_enhanced_html(research_result, writer_result, image_result)
        
        # Display results
        self._display_results(research_result, writer_result, image_result)
        
        return Message(final_html, media_type="text/html", model_used="Orchestrator")
    
    def _display_ai_config(self):
        """Display current AI model configuration"""
        print(f"🤖 AI Models Configuration:")
        print(f"   • Research: {self.research_agent.get_model_info()}")
        print(f"   • Writing:  {self.writer_agent.get_model_info()}")
        print(f"   • Images:   {self.image_agent.get_model_info()}")
        
        if ai_config.provider == AIProvider.SIMULATION:
            print(f"   💡 To use real AI: Set API keys and call ai_config.enable_real_ai(AIProvider.OPENAI)")
    
    def _display_results(self, research_result, writer_result, image_result):
        """Display comprehensive workflow results"""
        print("✅ [Orchestrator]: AI Workflow Complete!")
        print("📊 Workflow Results:")
        print(f"   • Research Model: {research_result.model_used}")
        print(f"   • Writing Model:  {writer_result.model_used}")
        print(f"   • Image Model:    {image_result.model_used}")
        print(f"   • Content Quality: {research_result.content['research_confidence']*100:.1f}% confidence")
        print(f"   • Article Length:  {writer_result.content['word_count']} words")
        print(f"   • Image Format:    {image_result.content['dimensions']} {image_result.content['format']}")
    
    def _create_enhanced_html(self, research_result, writer_result, image_result) -> str:
        """Create enhanced HTML output with AI model attribution"""
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{research_result.content['title']}</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #333;
                }}
                .header-image {{
                    width: 100%;
                    max-height: 400px;
                    object-fit: cover;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
                .ai-attribution {{
                    background: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 20px 0;
                    font-size: 0.9em;
                    color: #666;
                }}
                .content {{
                    margin-top: 30px;
                }}
                h1 {{
                    color: #2c3e50;
                    margin-bottom: 1em;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 1.5em;
                }}
                ul {{
                    padding-left: 1.5em;
                }}
                li {{
                    margin-bottom: 0.5em;
                }}
                .executive-summary {{
                    font-size: 1.1em;
                    color: #444;
                    border-left: 4px solid #3498db;
                    padding-left: 1em;
                    margin: 1.5em 0;
                }}
                .key-points {{
                    background: #f7f9fc;
                    padding: 1.5em;
                    border-radius: 8px;
                    margin: 1.5em 0;
                }}
                .methodology {{
                    font-style: italic;
                    color: #666;
                    margin-top: 2em;
                    padding-top: 1em;
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            <img src="{image_result.content['image_url']}" 
                 alt="{image_result.content['alt_text']}"
                 class="header-image">
            
            <div class="ai-attribution">
                <h4>🤖 AI Model Attribution</h4>
                <p>This content was generated using multiple AI models:</p>
                <ul>
                    <li>Research Analysis: {research_result.model_used}</li>
                    <li>Content Generation: {writer_result.model_used}</li>
                    <li>Image Creation: {image_result.model_used}</li>
                </ul>
                <p>Content Quality Score: {research_result.content['research_confidence']*100:.1f}%</p>
            </div>
            
            <div class="content">
                <h1>{research_result.content['title']}</h1>
                
                <div class="executive-summary">
                    <p>{research_result.content['executive_summary']}</p>
                </div>

                <div class="key-points">
                    <h2>Key Insights</h2>
                    <ul>
                        {''.join(f'<li>{point}</li>' for point in research_result.content['key_points'])}
                    </ul>
                </div>

                {writer_result.content['article_text']}
                
                <div class="methodology">
                    <p><strong>Research Methodology:</strong> {research_result.content['methodology']}</p>
                </div>
            </div>
            
            <footer class="ai-attribution">
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Keywords:</strong> {', '.join(research_result.content['keywords'])}</p>
            </footer>
        </body>
        </html>
        """
        return html_template

async def main():
    """Main entry point for enhanced agentic workflow"""
    print("🚀 ENHANCED AGENTIC WORKFLOW ENGINE")
    print("🤖 Multi-AI Model Integration Demo")
    print("="*60)
    
    # Check for OpenAI API key
    if ai_config.has_valid_api_key(AIProvider.OPENAI):
        print("✅ OpenAI API key detected!")
        use_real = input("Use real OpenAI models? (y/N): ").lower().startswith('y')
        if use_real:
            print("🤖 Enabled real AI models using openai")
            ai_config.enable_real_ai(AIProvider.OPENAI)
            init_openai_client()  # Initialize the global client
            print("✅ OpenAI integration configured")
    else:
        print("💡 No AI API keys found - using enhanced simulation mode")
        print("   Set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_AI_API_KEY for real AI")
    
    print()
    
    # Create and run orchestrator
    orchestrator = OrchestratorAgent()
    result = await orchestrator.process("The Future of Collaborative AI")
    
    # Save output
    output_file = "enhanced_agentic_output.html"
    with open(output_file, "w") as f:
        f.write(result.content)
    
    print("\n" + "="*70)
    print(f"\n🎉 SUCCESS! Enhanced output saved to: {output_file}")
    print(f"⏱️  Total execution time: {(datetime.now() - result.timestamp).total_seconds():.2f} seconds")
    print(f"🌐 Open the file to see AI model attributions and enhanced content!")

if __name__ == "__main__":
    asyncio.run(main()) 