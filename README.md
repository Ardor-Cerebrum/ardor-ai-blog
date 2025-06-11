# ardor-ai-blog

> **Note:** This repository will serve as a developer blog. The first article will be available soon—stay tuned!

## Included Demo: fastapi-mcp-demo

This repository includes a demo project in the `fastapi-mcp-demo` folder, which demonstrates how to expose a FastAPI application as an AI-native service using the Model Context Protocol (MCP).

### What is `fastapi-mcp-demo`?
- A FastAPI app that calculates Body Mass Index (BMI) and exposes it as an MCP-compliant API.
- Shows how to integrate FastAPI with the [fastapi-mcp](https://github.com/tadata-org/fastapi_mcp) library.
- Includes a ready-to-run example and instructions for both web and CLI-based MCP clients.

### How to Run the Demo
1. **Navigate to the folder:**
   ```sh
   cd fastapi-mcp-demo
   ```
2. **Create a virtual environment and install dependencies with [uv](https://github.com/astral-sh/uv):**
   ```sh
   uv venv
   uv sync
   ```
3. **Run the server:**
   ```sh
   uvicorn main:app --reload
   ```
4. **Try it out:**
   - Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.
   - Access the MCP manifest at [http://localhost:8000/mcp](http://localhost:8000/mcp).
   - Calculate BMI: [http://localhost:8000/bmi?weight_kg=70&height_m=1.75](http://localhost:8000/bmi?weight_kg=70&height_m=1.75)

### More Info
See `fastapi-mcp-demo/README.md` for a detailed walkthrough, architecture, and advanced usage.
