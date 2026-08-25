from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import auth, dashboard, report, payload, lab
from database import engine
from models import base
from api import attack

# Create database tables
base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Attack Simulation Platform API",
    description="Backend API for educational cybersecurity training platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
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
