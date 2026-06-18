"""v1 API router aggregation."""
from fastapi import APIRouter

from . import agents, apikeys, auth, chat, datasources, files, llm_configs, skills

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(apikeys.router)
api_router.include_router(datasources.router)
api_router.include_router(llm_configs.router)
api_router.include_router(agents.router)
api_router.include_router(skills.router)
api_router.include_router(chat.router)
api_router.include_router(files.router)

__all__ = ["api_router"]
