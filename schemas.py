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

from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List

# Example schemas (you can keep these as references):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# MU Foods specific schemas

class Beverage(BaseModel):
    """
    MU Foods beverage collection
    Collection name: "beverage"
    """
    name: str = Field(..., description="Beverage name")
    flavor: str = Field(..., description="Primary flavor")
    description: Optional[str] = Field(None, description="Short description")
    price: float = Field(..., ge=0, description="Price in local currency")
    size_ml: int = Field(..., ge=50, le=5000, description="Bottle size in milliliters")
    image_url: Optional[HttpUrl] = Field(None, description="Product image URL")
    tags: List[str] = Field(default_factory=list, description="Search/filter tags")
    in_stock: bool = Field(True, description="Whether item is available")

class ContactInquiry(BaseModel):
    """
    Contact inquiries from the website
    Collection name: "contactinquiry"
    """
    name: str = Field(..., description="Sender name")
    email: EmailStr = Field(..., description="Sender email")
    phone: Optional[str] = Field(None, description="Phone number")
    subject: str = Field(..., description="Subject")
    message: str = Field(..., description="Message body")
