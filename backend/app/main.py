from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
import os

from app.database import engine, get_db
from app.models import user, card
from app.schemas.card import CardCreate, CardResponse
from app.services.ai_service import ai_service
from app.utils.security import verify_password, get_password_hash, create_access_token, verify_token

# Create database tables
user.Base.metadata.create_all(bind=engine)
card.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kard.ai API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user_obj = db.query(user.User).filter(user.User.username == username).first()
    if user_obj is None:
        raise credentials_exception
    return user_obj

@app.get("/")
def read_root():
    return {"message": "Welcome to Kard.ai API"}

@app.post("/register")
def register(username: str, email: str, password: str, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(user.User).filter(
        (user.User.username == username) | (user.User.email == email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create new user
    hashed_password = get_password_hash(password)
    new_user = user.User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "username": username}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_obj = db.query(user.User).filter(user.User.username == form_data.username).first()
    
    if not user_obj or not verify_password(form_data.password, user_obj.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user_obj.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/cards", response_model=CardResponse)
async def create_card(
    card_data: CardCreate,
    current_user: user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Generate AI content
    generated_text = ai_service.generate_card_text(
        card_data.occasion,
        card_data.style or "creative",
        card_data.tone or "friendly",
        card_data.prompt
    )
    
    image_url = ai_service.generate_card_image(
        card_data.occasion,
        card_data.style or "creative",
        card_data.prompt
    )
    
    # Save to database
    new_card = card.Card(
        user_id=current_user.id,
        title=card_data.title,
        occasion=card_data.occasion,
        style=card_data.style,
        tone=card_data.tone,
        prompt=card_data.prompt,
        personal_message=card_data.personal_message,
        generated_text=generated_text,
        image_url=image_url,
        recipient_email=card_data.recipient_email
    )
    
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    
    return new_card

@app.get("/cards", response_model=List[CardResponse])
async def get_user_cards(
    current_user: user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cards = db.query(card.Card).filter(card.Card.user_id == current_user.id).all()
    return cards

@app.get("/cards/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: int,
    current_user: user.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    card_obj = db.query(card.Card).filter(
        card.Card.id == card_id,
        card.Card.user_id == current_user.id
    ).first()
    
    if not card_obj:
        raise HTTPException(status_code=404, detail="Card not found")
    
    return card_obj

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)