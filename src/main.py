from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.db import get_supabase_client

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context lifespan to initialize and clean up resources.
    """
    client = get_supabase_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    app.state.supabase_client = client
    yield
    # Cleanup logic if needed
    print("shutting down . . . Bye Bye!")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Welcome to LlamaCon Backend!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
