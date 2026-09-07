from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from backend.app.config import settings
from backend.app.database import engine, Base
from backend.app.api.router import api_router
from backend.app.utils.logging import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    logger.info("Initializing database schema...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.warning(f"Database schema initialization warning: {e}")
    yield
    logger.info("Shutting down Urban Flood Nowcasting backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Production-oriented Urban Flood Nowcasting System for Lovely Professional University (LPU), "
        "Phagwara, Punjab, India (SIH 2026: Urban Flood Nowcasting System through Dynamic Coupling of "
        "Rainfall Forecasts and Urban Drainage Network Models)."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
def root_endpoint():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "study_area": settings.DEFAULT_STUDY_AREA_NAME,
        "api_docs": "/docs",
        "api_v1_prefix": settings.API_V1_STR
    }

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "version": settings.VERSION,
        "study_area": settings.DEFAULT_STUDY_AREA_ID
    }
