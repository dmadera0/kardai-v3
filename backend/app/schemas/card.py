from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CardBase(BaseModel):
    title: str
    occasion: str
    style: Optional[str] = None
    tone: Optional[str] = None
    prompt: str
    personal_message: Optional[str] = None
    recipient_email: Optional[EmailStr] = None

class CardCreate(CardBase):
    pass

class CardResponse(CardBase):
    id: int
    user_id: int
    generated_text: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    sent_at: Optional[datetime]
    
    class Config:
        from_attributes = True