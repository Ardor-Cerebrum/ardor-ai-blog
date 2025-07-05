# ACP Agentic Workflow Engine 🚀

A powerful demonstration of multi-agent AI workflows using OpenAI's latest models (o4-mini & DALL-E 3) to create professional content.

## Features 🌟

- **Multi-Agent Architecture**: Research, Writing, and Image generation agents working in harmony
- **Real AI Integration**: Uses OpenAI's latest models with graceful fallback to simulation
- **Professional Output**: Generates well-structured HTML articles with AI-generated images
- **Configurable**: Easy to customize AI models and parameters
- **Error Handling**: Robust error handling with simulation fallback

## Quick Start 🏃‍♂️

1. **Setup Environment**:
   ```bash
   # Create and activate virtual environment using uv
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # OR
   .venv\Scripts\activate  # On Windows
   
   # Install dependencies
   uv pip install -r requirements.txt
   ```

2. **Configure API Key**:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

3. **Run Demo**:
   ```bash
   python enhanced_demo.py
   ```

## Project Structure 📁

```
agentic-workflow-engine/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── research.py
│   │   ├── writer.py
│   │   └── image.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── ai_models.py
│   └── utils/
│       ├── __init__.py
│       └── html_generator.py
├── examples/
│   └── enhanced_demo.py
├── tests/
│   └── __init__.py
├── docs/
│   ├── ARTICLE.md
│   └── AI_MODELS_GUIDE.md
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Configuration 🔧

The system supports multiple AI models and configurations through `config/ai_models.py`:

- Research Agent: o4-mini-2025-04-16
- Writer Agent: o4-mini-2025-04-16
- Image Agent: DALL-E 3

## Output Example 📝

The system generates professional HTML articles with:
- AI-generated header images
- Well-structured content
- Executive summary
- Key insights
- Strategic recommendations
- Model attributions

## Error Handling 🛡️

The system includes robust error handling:
- API authentication errors
- Model-specific parameter validation
- Graceful fallback to simulation mode
- Detailed error logging

## Contributing 🤝

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License 📄

MIT License - see LICENSE file for details
