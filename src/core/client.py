from openai import OpenAI
from supabase import create_client

from src.core.config import settings

supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

openai_client = OpenAI(
    api_key=settings.LLAMA_API_KEY,
    base_url=settings.LLAMA_BASE_URL,
)
