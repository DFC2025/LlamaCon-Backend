from typing import Annotated

from fastapi import Depends, HTTPException, Request
from openai import OpenAI
from supabase import Client

from src.core.client import openai_client, supabase_client


def get_supabase_client():
    return supabase_client


def get_openai_client():
    return openai_client


DBClientDep = Annotated[Client, Depends(get_supabase_client)]
OpenAIDep = Annotated[OpenAI, Depends(get_openai_client)]


async def get_current_user(request: Request, client: DBClientDep) -> dict:
    """
    Dependency function to verify the Supabase JWT token from the Authorization header.
    Returns the validated user object from Supabase.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401, detail="Invalid Authorization header format"
        )

    token = parts[1]

    try:
        user_response = client.auth.get_user(token)
        user = user_response.user
        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        print(f"Authenticated user: {user.id}")
        return user

    except Exception as e:
        print(f"Token validation error: {e}")
        raise HTTPException(
            status_code=401, detail=f"Invalid token or authentication error: {e}"
        )


CurrentUser = Annotated[dict, Depends(get_current_user)]
