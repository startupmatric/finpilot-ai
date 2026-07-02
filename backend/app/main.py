from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ✅ Add this import
from app.config import APP_NAME, APP_VERSION, DEBUG
from app.database import engine, Base
import app.models

# Import routers
from app.api.routes.upload import router as upload_router
from app.api.routes.transactions import router as transactions_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.chat import router as chat_router
from app.api.routes.auth import router as auth_router

# Create FastAPI instance
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    debug=DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
    print(f"✅ {APP_NAME} database tables created successfully!")
    print(f"📊 Environment: {'DEBUG' if DEBUG else 'PRODUCTION'}")
    print(f"📚 Swagger UI: http://127.0.0.1:8000/docs")
    print(f"🌐 CORS enabled for all origins (development mode)")

@app.on_event("shutdown")
def shutdown_event():
    print("🔄 Shutting down application...")

# Include routers
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(upload_router, prefix="/api/v1", tags=["Upload"])
app.include_router(transactions_router, prefix="/api/v1", tags=["Transactions"])
app.include_router(analytics_router, prefix="/api/v1", tags=["Analytics"])
app.include_router(chat_router, prefix="/api/v1", tags=["AI Chat"])

@app.get("/")
async def root():
    return {
        "message": f"{APP_NAME} API is running!",
        "version": APP_VERSION,
        "status": "healthy",
        "endpoints": {
            "auth": {
                "register": "/api/v1/auth/register",
                "login": "/api/v1/auth/login",
                "refresh": "/api/v1/auth/refresh",
                "me": "/api/v1/auth/me"
            },
            "upload": "/api/v1/upload",
            "transactions": "/api/v1/transactions",
            "categories": "/api/v1/categories",
            "analytics": {
                "spending": "/api/v1/analytics/spending/*",
                "merchant": "/api/v1/analytics/merchant/*",
                "monthly": "/api/v1/analytics/monthly/*",
                "statistics": "/api/v1/analytics/statistics",
                "budget": "/api/v1/analytics/budget",
                "health": "/api/v1/analytics/health",
                "coach": "/api/v1/analytics/coach/weekly",
                "subscriptions": "/api/v1/analytics/subscriptions",
                "forecast": "/api/v1/analytics/forecast/*"
            },
            "chat": "/api/v1/chat",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "version": APP_VERSION
    }