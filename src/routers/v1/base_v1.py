from fastapi import APIRouter

from src.routers.v1.users import router as user_router


router = APIRouter(prefix="/api/v1")

router.include_router(user_router)
