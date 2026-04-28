from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.cases import router as cases_router
from app.api.v1.extensions import router as extensions_router
from app.api.v1.reports import router as reports_router
from app.api.v1.users import router as users_router
from app.api.v1.statistics import router as statistics_router

from app.api.v1.cases_pdf import router as cases_pdf_router
from app.api.v1.predictions import router as predictions_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(cases_router, prefix="/cases", tags=["cases"])
api_router.include_router(cases_pdf_router, prefix="/cases-pdf", tags=["cases-pdf"])
api_router.include_router(extensions_router, prefix="/extensions", tags=["extensions"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(predictions_router, prefix="/predictions", tags=["predictions"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(statistics_router, prefix="/statistics", tags=["statistics"])
