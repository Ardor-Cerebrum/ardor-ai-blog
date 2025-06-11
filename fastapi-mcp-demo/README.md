# 🧠 FastAPI + MCP Demo

Transform your FastAPI application into an AI-native service using the Model Context Protocol (MCP).

---

## 🚀 Overview

This demo shows how to:
- Build a FastAPI app that calculates Body Mass Index (BMI)
- Expose the app as an MCP-compliant server
- Interact with the MCP server using tools like MCP Inspector and mcp-cli

---

## 🛠️ Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (for environment and dependency management)
- (Optional) Node.js ≥ 18 (for MCP Inspector)

---

## 📦 Installation & Setup

Clone the repository and navigate to the demo folder:
```sh
git clone https://github.com/Ardor-Cerebrum/ardor-ai-blog
cd ardor-ai-blog/fastapi-mcp-demo
```

Create a virtual environment and install dependencies:
```sh
uv venv
uv sync
```

---

## ▶️ Running the Application

Start the FastAPI application:
```sh
uvicorn main:app --reload
```

The server will be available at [http://localhost:8000](http://localhost:8000).

---

## 🔗 Usage
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **MCP Manifest:** [http://localhost:8000/mcp](http://localhost:8000/mcp)
- **Calculate BMI:** [http://localhost:8000/bmi?weight_kg=70&height_m=1.75](http://localhost:8000/bmi?weight_kg=70&height_m=1.75)

---

## 🧪 Validating the MCP Server

### A. Using MCP Inspector (Web-Based)
1. Install Node.js: https://nodejs.org/
2. Launch MCP Inspector:
   ```sh
   npx @modelcontextprotocol/inspector
   ```
3. Open the Inspector URL (e.g., http://127.0.0.1:6274) in your browser.
4. Connect to your MCP server: enter `http://localhost:8000/mcp` and click Connect.

### B. Using mcp-cli (Command-Line)
1. Install mcp-cli:
   ```sh
   pip install mcp-cli
   ```
2. List available tools:
   ```sh
   mcp-cli --server http://localhost:8000/mcp list-tools
   ```
3. Invoke a tool:
   ```sh
   mcp-cli --server http://localhost:8000/mcp invoke calculate_bmi weight_kg=70 height_m=1.75
   ```

---

## 🧾 Application Structure
```
fastapi-mcp-demo/
├── main.py
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## 🧑‍💻 Example Endpoint
```python
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP

class BMIResponse(BaseModel):
    bmi: float = Field(..., example=22.9, description="Body Mass Index rounded to 2 decimal places")
    assessment: str = Field(..., example="Normal weight")

app = FastAPI(title="Intelligent Health API", description="Demo of FastAPI + MCP", version="1.0.0")

@app.get("/bmi", operation_id="calculate_bmi", summary="Calculate BMI and return assessment", response_model=BMIResponse, tags=["Health"])
def bmi(weight_kg: float = Query(..., gt=0, example=70.5), height_m: float = Query(..., gt=0, example=1.75)):
    value = round(weight_kg / height_m ** 2, 2)
    if value < 18.5:
        status = "Underweight"
    elif value <= 24.9:
        status = "Normal weight"
    elif value <= 29.9:
        status = "Overweight"
    else:
        status = "Obesity"
    return BMIResponse(bmi=value, assessment=status)

mcp = FastApiMCP(app, name="Intelligent Health API MCP Server", description="Health tools exposed via MCP")
mcp.mount()
```

---

## 📚 References
- [FastAPI-MCP GitHub Repository](https://github.com/tadata-org/fastapi_mcp)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- Shamim Bhuiyan's Tutorial: Modern AI Integrations: MCP Server Meets REST API and Local LLMs - Part 1

---

## ⚡️ Why UV?

This project uses [uv](https://github.com/astral-sh/uv) for all Python environment and dependency management. **Do not use pip or venv.**

- `uv` is faster, more reliable, and creates cleaner, reproducible environments.
- No more `pip install` or `python -m venv`—just use `uv venv` and `uv sync`.
- This keeps the repository minimal and ensures everyone gets the same setup.

### Quick Start

From the `fastapi-mcp-demo` directory:
```sh
uv venv
uv sync
uvicorn main:app --reload
```

Or from the project root:
```sh
uv venv
cd fastapi-mcp-demo
uv sync
uvicorn main:app --reload
```
