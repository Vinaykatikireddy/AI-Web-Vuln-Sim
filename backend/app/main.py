from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from api import attack, auth, dashboard, report, payload, lab
from core.limiter import limiter

# Initialize database
# from database import engine
# from models import base
# from scripts.init_db import init_db
# from scripts.init_payloads import init_payloads

# Create database tables
# base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Attack Simulation Platform API",
    description="Backend API for educational cybersecurity training platform",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS - restrict to known frontend origins via CORS_ORIGINS 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://vinaykatikireddy-portfolio.hf.space/ai-web-vuln-sim"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(attack.router)
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(report.router)
app.include_router(payload.router)
app.include_router(lab.router)


@app.get("/")
async def root():
    return {"message": "AI-Powered Attack Simulation Platform API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port="8000")
