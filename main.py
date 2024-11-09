# main.py
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Dict
import google.generativeai as genai
import os
from dotenv import load_dotenv
import jwt
import requests
from functools import lru_cache

# Load environment variables
load_dotenv()

app = FastAPI()
security = HTTPBearer()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
   
)

# Auth0 configuration
AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
AUTH0_AUDIENCE = os.getenv('AUTH0_AUDIENCE')
ALGORITHMS = ["RS256"]

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

# Auth0 JWT verification
@lru_cache(maxsize=1)
def get_auth0_public_key():
    """Fetch and cache Auth0 public key"""
    try:
        response = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
        return response.json()
    except Exception as e:
        print(f"Error fetching Auth0 public key: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication system unavailable")

async def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify the Auth0 JWT token"""
    try:
        token = credentials.credentials
        jwks = get_auth0_public_key()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=401,
                detail="Unable to find appropriate key"
            )

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=AUTH0_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid claims")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

# Your existing helper functions remain the same
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
        prompt = create_prompt(question)
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise Exception("Empty response from Gemini")

        formatted_response = format_response(response.text)
        return formatted_response
        
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return ("I apologize, but I'm having trouble generating a response. "
                "Please try rephrasing your question or contact a women's rights "
                "organization for immediate assistance. Emergency helpline: 1091")

def format_response(text: str) -> str:
    formatted_lines = []
    lines = text.split('\n')
    
    for line in lines:
        if line.strip().startswith('*'):
            bullet_line = line.replace('*', '').strip()
            formatted_lines.append(f"• {bullet_line}")
        elif '**' in line:
            bold_text = line.replace('**', '').strip()
            formatted_lines.append(f"<strong>{bold_text}</strong>")
        else:
            clean_line = line.strip()
            if clean_line:
                formatted_lines.append(clean_line)
    
    return '<br>'.join(formatted_lines)

# Updated endpoints with authentication
@app.post("/chat")
async def chat(question: Question, token_data: dict = Depends(verify_token)):
    if not question.text:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        response = await generate_gemini_response(question.text)
        return {"response": response, "user": token_data.get("sub")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Women's Rights Information Chatbot API is running"}

# New endpoint to verify authentication status
@app.get("/verify-auth")
async def verify_auth(token_data: dict = Depends(verify_token)):
    return {"authenticated": True, "user": token_data.get("sub")}