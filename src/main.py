from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import api_router
from src.core.config import settings
from src.web import web_router
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"message": "Welcome to LlamaCon Backend!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(api_router, prefix=settings.api_str)
app.include_router(web_router,include_in_schema=False)