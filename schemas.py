"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Core app schemas for the AI Legal Chatbot

class Conversation(BaseModel):
    """
    Conversations collection schema
    Collection name: "conversation"
    """
    title: str = Field("New Conversation", description="Display title for the conversation")

class Message(BaseModel):
    """
    Messages collection schema
    Collection name: "message"
    """
    conversation_id: str = Field(..., description="ID of the parent conversation (as string)")
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text content")

# Optional content models for marketing sections
class CaseStudy(BaseModel):
    """
    Case studies collection schema
    Collection name: "casestudy"
    """
    title: str
    industry: str
    summary: str
    impact: str
    metrics: Optional[List[str]] = None

class Plan(BaseModel):
    """
    Pricing plans collection schema
    Collection name: "plan"
    """
    name: str
    price: str
    description: str
    features: List[str]

# Example schemas retained for reference (not used by app directly)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")
