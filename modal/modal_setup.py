import modal
import os 
from dotenv import load_dotenv

load_dotenv()

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git")
    .pip_install("asyncio>=3.4.3",
                 "fastapi>=0.115.12",
                 "firecrawl>=1.16.0",
                 "google-genai>=1.10.0",
                 "ipykernel>=6.29.5",
                 "modal>=0.73.169",
                 "nest-asyncio>=1.6.0",
                 "openai>=1.72.0",
                 "pydantic>=2.11.3",
                 "python-dotenv>=1.1.0",
                  "uvicorn>=0.34.0",
                  "nest-asyncio",
                 "supabase>=2.15.0",
                 "podgen>=1.1.0",
                 "pydub>=0.25.1",
                "elevenlabs>=1.56.0",
                "feedparser",
                 "git+https://github.com/unclecode/crawl4ai.git@2025-MAR-ALPHA-1",
                 )
    .env({"HALT_AND_CATCH_FIRE": "0",
          "SUPABASE_URL": "https://vjzymbdtfyfwveghnmfh.supabase.co",
          "SUPABASE_KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZqenltYmR0Znlmd3ZlZ2hubWZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDYzMDI0MzcsImV4cCI6MjA2MTg3ODQzN30.Ww2ivXl_NlR108ffLqTRKIQEomxCwc6BH7ErG5J5KoA",
          "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
          "LLAMA_API_KEY": os.getenv("LLAMA_API_KEY"),
          "ELEVENLABS_API_KEY": os.getenv("ELEVENLABS_API_KEY"),
          })
    .run_commands("crawl4ai-setup","apt install -y ffmpeg"))


github_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("asyncio>=3.4.3",
                 "fastapi>=0.115.12",
                 "firecrawl>=1.16.0",
                 "google-genai>=1.10.0",
                 "ipykernel>=6.29.5",
                 "nest-asyncio>=1.6.0",
                 "openai>=1.72.0",
                 "pydantic>=2.11.3",
                 "python-dotenv>=1.1.0",
                 "uvicorn>=0.34.0",
                 "nest-asyncio",))