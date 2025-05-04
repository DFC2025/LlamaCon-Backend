import modal
import os 
from dotenv import load_dotenv
from google import genai
from supabase import create_client, Client
import asyncio
from functools import lru_cache
load_dotenv()

# Cache size of 1000 entries
CACHE_SIZE = 1000

image = (
    modal.Image.debian_slim(python_version="3.10")
    .apt_install("git")
    .pip_install("asyncio>=3.4.3",
                 "fastapi>=0.115.12",
                 "google-genai>=1.10.0",
                 "ipykernel>=6.29.5",
                 "modal>=0.73.169",
                 "nest-asyncio>=1.6.0",
                 "openai>=1.72.0",
                 "pydantic>=2.11.3",
                 "python-dotenv>=1.1.0",
                 "supabase>=2.15.0",
                 "uvicorn>=0.34.0",
                 )
    .env({"HALT_AND_CATCH_FIRE": "0",
          "SUPABASE_URL": "https://vjzymbdtfyfwveghnmfh.supabase.co",
          "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZqenltYmR0Znlmd3ZlZ2hubWZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYzMDI0MzcsImV4cCI6MjA2MTg3ODQzN30.Ww2ivXl_NlR108ffLqTRKIQEomxCwc6BH7ErG5J5KoA",
          "GEMINI_API_KEY": "AIzaSyA0Fseiu0ScMPZEmRiNQXgoNbAkuFiJfZ0",
          }))

app = modal.App(image=image,name="search_bar")

# Cache the Supabase client
_supabase_client = None

def get_supabase():
    """Get or create Supabase client singleton"""
    global _supabase_client
    if _supabase_client is None:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        _supabase_client = create_client(url, key)
    return _supabase_client

_gemini_client = None

def get_gemini():
    """Get or create Gemini client singleton"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    return _gemini_client

@lru_cache(maxsize=CACHE_SIZE)
def get_embeddings(content:str, model="models/text-embedding-004"):
    """Cache embeddings for frequently searched queries"""
    client = get_gemini()
    result = client.models.embed_content(
        model=model,
        contents=content)
    return tuple(result.embeddings[0].values)  

def transform_response(response):
    return [{"content": item['content'],
             "content_id": item['content_id'],
             "tags": item['tags']} 
            for item in response.data]

@app.function(scaledown_window=900)
@modal.fastapi_endpoint(method="POST")
def search(query: str,user_id: str):
    # Get embedding (cached if query was seen before)
    embedding = get_embeddings(query)
    
    # Execute search
    supabase = get_supabase()
    response = supabase.rpc("hybrid_search",
                                {"query_text": query,    
                                 "query_embedding": list(embedding),
                                 "for_user":"dddbe848-2225-42bd-9e5e-44ffa1043ef3",
                                 "match_count": 10}).execute()
    print(response)
    return transform_response(response)