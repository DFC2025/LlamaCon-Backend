import os
from pathlib import Path

import modal
import tomli
from dotenv import find_dotenv, load_dotenv

from src.main import app as web_app

load_dotenv(find_dotenv())


def get_dependencies():
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject = tomli.load(f)
            # Get dependencies from project.dependencies
            dependencies = pyproject.get("project", {}).get("dependencies", [])
            return dependencies
    except Exception as e:
        print(f"Error loading dependencies: {e}")
        return ["fastapi[standard]"]  # Fallback to minimum required


image = (
    modal.Image.debian_slim()
    .pip_install(*get_dependencies())
    .env(
        {
            "SUPABASE_URL": os.getenv("SUPABASE_URL"),
            "SUPABASE_ANON_KEY": os.getenv("SUPABASE_ANON_KEY"),
        }
    )
)

app = modal.App("LlamaBuddy", image=image)


@app.function(image=image)
@modal.asgi_app()
def fastapi_app():
    return web_app
