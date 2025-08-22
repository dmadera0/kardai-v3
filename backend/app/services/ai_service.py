import openai
import os
from typing import Dict, Optional
import base64
from io import BytesIO
import requests

class AIService:
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    def generate_card_text(self, occasion: str, style: str, tone: str, prompt: str) -> str:
        """Generate greeting card text using GPT-4"""
        system_prompt = f"""You are a creative greeting card writer. 
        Create a {style} and {tone} message for a {occasion} card.
        The message should be heartfelt and appropriate for the occasion."""
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a greeting card message based on: {prompt}"}
                ],
                max_tokens=300,
                temperature=0.8
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating text: {e}")
            return f"Happy {occasion}! {prompt}"
    
    def generate_card_image(self, occasion: str, style: str, prompt: str) -> Optional[str]:
        """Generate greeting card image using DALL-E"""
        image_prompt = f"A {style} greeting card illustration for {occasion}, {prompt}, digital art, high quality"
        
        try:
            response = openai.images.generate(
                model="dall-e-3",
                prompt=image_prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            return response.data[0].url
        except Exception as e:
            print(f"Error generating image: {e}")
            return None

ai_service = AIService()