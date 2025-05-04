from fastapi import APIRouter, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.core.client import openai_client
from src.core.config import settings

router = APIRouter()


class ChatRequest(BaseModel):
    msg: str


@router.post("/{chat_id}")
def chat_with_openai(chat_id: str, body: ChatRequest = Body(...)):
    msg = body.msg

    def stream_response():
        response = openai_client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": msg}],
            temperature=0.6,
            max_completion_tokens=2048,
            top_p=0.9,
            frequency_penalty=1,
            stream=True,
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content

    return StreamingResponse(stream_response(), media_type="text/plain")
