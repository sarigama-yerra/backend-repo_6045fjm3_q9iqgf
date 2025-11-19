import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson.objectid import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="AI Legal Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models for requests ----------
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    conversation_id: str
    reply: str

# ---------- Utility ----------
def to_str_id(doc):
    if not doc:
        return doc
    doc["id"] = str(doc.pop("_id"))
    return doc

# ---------- Routes ----------
@app.get("/")
def read_root():
    return {"message": "AI Legal Chatbot Backend Running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
                response["connection_status"] = "Connected"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Minimal, safe placeholder: echo with legal assistant framing
    # Note: Replace with real LLM integration later if desired
    user_msg = req.message.strip()
    assistant_reply = (
        "I am not a lawyer, but here is general information based on your question: "
        + user_msg
        + " — For legal advice, consult a licensed attorney in your jurisdiction."
    )

    # Ensure a conversation exists
    conv_id = req.conversation_id
    if not conv_id:
        conv_id = create_document("conversation", {"title": user_msg[:60] or "New Conversation"})

    # Save messages
    try:
        create_document("message", {"conversation_id": conv_id, "role": "user", "content": user_msg})
        create_document("message", {"conversation_id": conv_id, "role": "assistant", "content": assistant_reply})
    except Exception as e:
        # If DB unavailable, still respond but mark conversation_id as provided or temp
        conv_id = conv_id or "temporary"

    return ChatResponse(conversation_id=str(conv_id), reply=assistant_reply)

@app.get("/api/case-studies")
def get_case_studies():
    # Return a few curated examples; if DB available, try to read from it
    items = [
        {
            "title": "Contract Review for SaaS Provider",
            "industry": "Technology",
            "summary": "Automated early risk flags in MSAs and DPAs.",
            "impact": "70% faster first-pass review",
            "metrics": ["-70% review time", "+30% throughput", "99% clause coverage"]
        },
        {
            "title": "Compliance Intake for HR Policies",
            "industry": "Healthcare",
            "summary": "Answer common employee compliance questions.",
            "impact": "Reduced legal tickets by 45%",
            "metrics": ["45% fewer tickets", "24/7 availability"]
        },
        {
            "title": "Discovery Q&A for Litigation Team",
            "industry": "Legal Services",
            "summary": "Natural-language search over prior filings.",
            "impact": "Improved first-draft quality",
            "metrics": ["2x faster drafting", "Centralized knowledge"]
        }
    ]

    try:
        # If there are custom case studies in DB, prefer them
        docs = get_documents("casestudy", {}, limit=50)
        if docs:
            items = [
                {
                    "title": d.get("title"),
                    "industry": d.get("industry"),
                    "summary": d.get("summary"),
                    "impact": d.get("impact"),
                    "metrics": d.get("metrics") or []
                }
                for d in docs
            ]
    except Exception:
        pass

    return {"caseStudies": items}

@app.get("/api/plans")
def get_plans():
    plans = [
        {
            "name": "Starter",
            "price": "$29/mo",
            "description": "For solos and small teams exploring AI assistance.",
            "features": [
                "100 chats/mo",
                "Basic contract Q&A",
                "Email summaries",
                "Community support"
            ]
        },
        {
            "name": "Pro",
            "price": "$99/mo",
            "description": "For growing teams that need faster reviews and guardrails.",
            "features": [
                "1000 chats/mo",
                "Clause extraction",
                "Upload + annotate PDFs",
                "SAML SSO"
            ]
        },
        {
            "name": "Enterprise",
            "price": "Custom",
            "description": "Tailored deployments, private data, and advanced controls.",
            "features": [
                "Unlimited chats",
                "Private knowledge base",
                "SOC2, HIPAA options",
                "Dedicated support"
            ]
        }
    ]

    try:
        docs = get_documents("plan", {}, limit=20)
        if docs:
            plans = [
                {
                    "name": d.get("name"),
                    "price": d.get("price"),
                    "description": d.get("description"),
                    "features": d.get("features") or []
                }
                for d in docs
            ]
    except Exception:
        pass

    return {"plans": plans}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
