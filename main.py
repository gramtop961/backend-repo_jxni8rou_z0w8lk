import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import Beverage, ContactInquiry

app = FastAPI(title="MU Foods API", description="Backend for MU Foods fresh squashes beverage company website")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "MU Foods", "status": "ok"}


# Public endpoints
@app.get("/api/beverages", response_model=List[Beverage])
def list_beverages(tag: Optional[str] = None, q: Optional[str] = None):
    """List beverages with optional tag or search query"""
    filter_dict = {"in_stock": True}
    if tag:
        filter_dict["tags"] = {"$in": [tag]}
    if q:
        filter_dict["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"flavor": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}},
        ]
    items = get_documents("beverage", filter_dict)
    # Remove Mongo _id for response_model compatibility
    for i in items:
        i.pop("_id", None)
    return items


class CreateInquiry(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    subject: str
    message: str


@app.post("/api/contact")
def submit_contact(inquiry: CreateInquiry):
    ci = ContactInquiry(**inquiry.model_dump())
    _id = create_document("contactinquiry", ci)
    return {"ok": True, "id": _id}


@app.post("/api/beverages/seed")
def seed_beverages():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    count = db["beverage"].count_documents({})
    if count > 0:
        return {"ok": True, "message": "Beverages already seeded", "count": count}

    sample = [
        {
            "name": "Citrus Zing",
            "flavor": "Lemon + Lime",
            "description": "A bright, zesty squash made from sun-ripened lemons and limes.",
            "price": 3.99,
            "size_ml": 500,
            "image_url": "https://images.unsplash.com/photo-1524594227084-6df73d85d2f9?w=800&q=80",
            "tags": ["citrus", "refreshing", "vegan"],
            "in_stock": True,
        },
        {
            "name": "Mango Bliss",
            "flavor": "Alphonso Mango",
            "description": "Thick, luscious mango squash with no added preservatives.",
            "price": 4.49,
            "size_ml": 500,
            "image_url": "https://images.unsplash.com/photo-1547514701-42782101795e?w=800&q=80",
            "tags": ["tropical", "best-seller"],
            "in_stock": True,
        },
        {
            "name": "Guava Glow",
            "flavor": "Pink Guava",
            "description": "Delicately sweet guava squash perfect for summer coolers.",
            "price": 4.29,
            "size_ml": 500,
            "image_url": "https://images.unsplash.com/photo-1604908554027-6e2ce8f94bd7?w=800&q=80",
            "tags": ["tropical", "vitamin-c"],
            "in_stock": True,
        },
        {
            "name": "Orange Orchard",
            "flavor": "Valencia Orange",
            "description": "Classic orange squash with a clean, fresh finish.",
            "price": 3.79,
            "size_ml": 500,
            "image_url": "https://images.unsplash.com/photo-1557800636-894a64c1696f?w=800&q=80",
            "tags": ["citrus", "family"],
            "in_stock": True,
        },
    ]
    # Add timestamps
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    for s in sample:
        s["created_at"] = now
        s["updated_at"] = now

    db["beverage"].insert_many(sample)
    return {"ok": True, "message": "Seeded beverages", "count": len(sample)}


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
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
