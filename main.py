# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Question(BaseModel):
    text: str

# Initialize Gemini
try:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    print(f"Error initializing Gemini: {str(e)}")
    raise

def create_prompt(question: str) -> str:
    """Create a focused prompt for women's rights questions"""
    base_prompt = """
    You are a helpful assistant specializing in women's rights information. 
    Provide accurate, clear, and supportive information about women's rights, laws, and resources.
    If the question involves immediate danger or legal advice, always include relevant helpline numbers 
    and suggest consulting with legal professionals.
    
    Question: {question}
    
    Please provide a clear, factual response focusing on:
    1. Direct information about the rights or issue
    2. Relevant laws or regulations if applicable
    3. Practical steps or resources
    4. Emergency contacts if relevant
    """
    return base_prompt.format(question=question)

async def generate_gemini_response(question: str) -> str:
    try:
        # Create the complete prompt
        prompt = create_prompt(question)
        
        # Generate response from Gemini
        response = model.generate_content(prompt)
        
        # Check if response is meaningful
        if not response or not response.text:
            raise Exception("Empty response from Gemini")

        # Clean up the response text
        formatted_response = format_response(response.text)

        return formatted_response
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        # Fallback response
        return ("I apologize, but I'm having trouble generating a response. "
                "Please try rephrasing your question or contact a women's rights "
                "organization for immediate assistance. Emergency helpline: 1091")

def format_response(text: str) -> str:
    # Create a list to hold formatted lines
    formatted_lines = []

    # Split the text into lines
    lines = text.split('\n')
    
    for line in lines:
        # Process each line for formatting
        # Handle bullet points
        if line.strip().startswith('*'):
            bullet_line = line.replace('*', '').strip()  # Remove the asterisk
            formatted_lines.append(f"• {bullet_line}")  # Add bullet point
        
        # Handle bold text
        elif '**' in line:
            bold_text = line.replace('**', '').strip()  # Remove the double asterisks
            formatted_lines.append(f"<strong>{bold_text}</strong>")  # Wrap bold text in HTML strong tags
        
        # Maintain regular lines
        else:
            clean_line = line.strip()  # Strip whitespace
            if clean_line:  # Only add non-empty lines
                formatted_lines.append(clean_line)
    
    # Join the lines back into a single string with <br> for line breaks
    return '<br>'.join(formatted_lines)



@app.post("/chat")
async def chat(question: Question):
    if not question.text:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        response = await generate_gemini_response(question.text)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Women's Rights Information Chatbot API is running"}