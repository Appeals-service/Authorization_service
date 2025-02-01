from fastapi import APIRouter

from routers.v1.base_v1 import router as router_v1

router = APIRouter()
router.include_router(router_v1)
