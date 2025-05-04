from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.core.client import openai_client
from src.core.config import settings

router = APIRouter()


@router.post("/chat/{chat_id}")
async def chat_with_openai(chat_id: str, msg: str):
    async def stream_response():
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
                yield f"data: {content}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
