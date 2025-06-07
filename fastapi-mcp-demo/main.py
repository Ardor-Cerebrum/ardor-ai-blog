from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from fastapi_mcp import FastApiMCP

# ── Data model ─────────────────────────────────────
class BMIResponse(BaseModel):
    bmi: float = Field(..., example=22.86,
                       description="Body‑mass index rounded to 2 dp")
    assessment: str = Field(..., example="Normal weight")

# ── FastAPI app ────────────────────────────────────
app = FastAPI(title="Intelligent Health API",
              description="Demo of FastAPI + MCP",
              version="1.0.0")

@app.get("/bmi",
         operation_id="calculate_bmi",
         summary="Calculate BMI & return a WHO assessment",
         response_model=BMIResponse,
         tags=["Health"])
def bmi(weight_kg: float = Query(..., gt=0, examples=70.5),
        height_m: float = Query(..., gt=0, examples=1.75)):
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

# ── MCP integration ────────────────────────────────
mcp = FastApiMCP(
    app,                                       # FastAPI instance
    name="Intelligent Health API MCP Server",
    description="Health tools exposed via MCP",
)

mcp.mount()