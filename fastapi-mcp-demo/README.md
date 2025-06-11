🧠 FastAPI + MCP: Exposing AI-Ready APIs with Ease

Transform your FastAPI application into an AI-native service using the Model Context Protocol (MCP).

---
💡Pro Tip: 
Ardor Cloud offers native support for the Model Context Protocol (MCP), 
enabling effortless integration of your MCP-compliant FastAPI services. 
Deploy your application on Ardor Cloud, 
and their agentic-first platform will automatically discover and orchestrate your tools, 
streamlining AI-driven workflows.
---

🚀 Overview

This guide demonstrates how to:
	•	Build a FastAPI application that calculates Body Mass Index (BMI).
	•	Expose the application as an MCP-compliant server.
	•	Interact with the MCP server using tools like MCP Inspector and mcp-cli.

⸻

🛠️ Prerequisites
	•	Python 3.10+
	•	pip
	•	(Optional) Node.js ≥ 18 (for MCP Inspector)

⸻

📦 Installation 
    1.	Clone the repository:

```shell
git clone https://github.com/Ardor-Cerebrum/ardor-ai-blog
cd ./ardor-ai-blog/fastapi-mcp-demo
```
2.	Create and activate a virtual environment:

```shell
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3.	Install dependencies:
```shell
pip install fastapi uvicorn fastapi-mcp pydantic
```



⸻

🧾 Application Structure
```
fastapi-mcp-demo/
├── main.py
└── README.md
```

⸻

🧑‍💻 main.py
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

⸻

▶️ Running the Application

Start the FastAPI application using Uvicorn:

From the `fastapi-mcp-demo` directory, run:
```sh
uvicorn main:app --reload
```

Or, if you are in the project root, run:
```sh
uvicorn fastapi-mcp-demo.main:app --reload
```

This will start the server at [http://localhost:8000](http://localhost:8000).

⸻

🔗 Accessing the Endpoints
	•	Calculate BMI: http://localhost:8000/bmi?weight_kg=70&height_m=1.75
	•	Swagger UI: http://localhost:8000/docs
	•	MCP Manifest: http://localhost:8000/mcp

⸻

🧪 Validating the MCP Server

A. Using MCP Inspector (Web-Based)
	
    1.	Install Node.js (if not already installed): https://nodejs.org/
	
    2.	Launch MCP Inspector:

```shell
npx @modelcontextprotocol/inspector
```

    3.	Open the Inspector URL (e.g., http://127.0.0.1:6274) in your browser.
	
   4.	Connect to your MCP server:
       •	Enter http://localhost:8000/mcp in the Server URL field.
       •	Click Connect.

   5. Explore and Invoke:
   
      •	View the available tools (e.g., calculate_bmi).
      •	Input parameters and execute the tool.
      •	Observe the response and logs.

B. Using mcp-cli (Command-Line Interface)
	1.	Install mcp-cli:
```shell
pip install mcp-cli
```

	2.	List available tools:
```shell
mcp-cli --server http://localhost:8000/mcp list-tools
```

	3.	Invoke a tool:
```shell
mcp-cli --server http://localhost:8000/mcp invoke calculate_bmi weight_kg=70 height_m=1.75
```


⸻

🧱 Architecture Diagram

[Host Machine]
    │
    ▼
[MCP Client (e.g., CLI or agent)]
    │   JSON-RPC
    ▼
[MCP Server (fastapi-mcp)]
    │   FastAPI routes
    ▼
[FastAPI Application Logic]
    │   Database or Storage
    ▼
[Data Layer]


⸻

📚 References
	•	FastAPI-MCP GitHub Repository: https://github.com/tadata-org/fastapi_mcp
	•	Shamim Bhuiyan's Tutorial: Modern AI Integrations: MCP Server Meets REST API and Local LLMs - Part 1
	•	MCP Inspector: https://github.com/modelcontextprotocol/inspector
