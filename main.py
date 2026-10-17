
import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel, Field

from sales_agent import (
    LeadInformation,
    build_system_prompt,
    classify_lead,
)
from tools import check_budget_eligibility, estimate_price

load_dotenv()

app = FastAPI(
    title="AI Sales Qualification Agent",
    description="An AI agent that understands customer needs and qualifies sales leads.",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[dict[str, str]] = Field(default_factory=list)


class QualificationRequest(BaseModel):
    lead: LeadInformation


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key is not configured.",
        )
    return OpenAI(api_key=api_key)


@app.get("/")
def home():
    return {"message": "AI Sales Qualification Agent is running."}


@app.get("/tools/price")
def price_tool():
    return estimate_price()


@app.get("/tools/budget/{budget}")
def budget_tool(budget: float):
    result = check_budget_eligibility(budget)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/chat")
def chat(request: ChatRequest):
    client = get_client()

    messages = [
        {"role": "system", "content": build_system_prompt()}
    ]

    # Keep only valid user/assistant messages from the recent history.
    for item in request.history[-10:]:
        role = item.get("role")
        content = item.get("content", "")

        if role in ("user", "assistant") and isinstance(content, str):
            messages.append({
                "role": role,
                "content": content[:2000],
            })

    messages.append({
        "role": "user",
        "content": request.message,
    })

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.2,
        )

        answer = response.choices[0].message.content

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="The AI model returned an empty response.",
            )

        return {"reply": answer}

    except Exception as exc:
      print(f"OpenAI API error ({type(exc).__name__}): {exc}")
    raise HTTPException(
        status_code=502,
        detail="The OpenAI API request failed. Check the server terminal.",
    )


@app.post("/qualify")
def qualify_lead(request: QualificationRequest):
    lead = classify_lead(request.lead)
    return lead.model_dump()
