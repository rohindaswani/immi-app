from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, profiles, documents, timeline, history, debug, chat

api_router = APIRouter()

# Include all the endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["Profiles"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(timeline.router, prefix="/timeline", tags=["Timeline"])
api_router.include_router(history.router, prefix="/history", tags=["History"])
api_router.include_router(debug.router, prefix="/debug", tags=["Debug"])
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])