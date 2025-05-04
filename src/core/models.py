from typing import List, Literal, Optional

from pydantic import BaseModel


class Item(BaseModel):
    url: str
    title: str
    description: Optional[str] = None
    favicon: Optional[str] = None
    sourceUrl: Optional[str] = None
    sourceSite: Optional[str] = None
    context: Optional[str] = None
    imageUrl: Optional[str] = None
    savedFrom: Literal["web", "phone"] = "web"
    type: Literal[
        "article",
        "video",
        "image",
        "audio",
        "document",
        "link",
        "other",
    ] = "article"


class Tags(BaseModel):
    tags: List[str] = []
