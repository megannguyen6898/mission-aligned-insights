
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import (
    auth_router,
    users_router, 
    data_router,
    integrations_router,
    dashboards_router,
    reports_router,
    investors_router
)
from .routes.public.template import router as public_template_router
from .routes.ingest.upload import router as ingest_upload_router
from .routes.ingest.jobs import router as ingest_jobs_router
from .routes.metrics.recompute import router as metrics_recompute_router
from .routes.dashboards.embed import router as dashboards_embed_router
from .routes.reports import router as reports_generate_router

app = FastAPI(
    title="ImpactView API",
    description="AI-Powered Impact Reporting Platform for Social Enterprises",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1") 
app.include_router(data_router, prefix="/api/v1")
app.include_router(integrations_router, prefix="/api/v1")
app.include_router(dashboards_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(investors_router, prefix="/api/v1")
app.include_router(public_template_router)
app.include_router(ingest_upload_router)
app.include_router(ingest_jobs_router)
app.include_router(metrics_recompute_router)
app.include_router(dashboards_embed_router)
app.include_router(reports_generate_router)

@app.get("/")
async def root():
    return {"message": "Welcome to ImpactView API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
