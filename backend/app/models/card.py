from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    occasion = Column(String, nullable=False)  # birthday, anniversary, etc.
    style = Column(String)  # funny, romantic, professional
    tone = Column(String)   # casual, formal, humorous
    prompt = Column(Text, nullable=False)
    personal_message = Column(Text)
    generated_text = Column(Text)
    image_url = Column(String)
    recipient_email = Column(String)
    metadata = Column(JSON, default={})  # Store additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationship
    creator = relationship("User", back_populates="cards")