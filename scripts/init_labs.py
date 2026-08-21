import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Lab
from dotenv import load_dotenv

load_dotenv()

# Create database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_labs():
    db = SessionLocal()

    # Define the available labs
    labs_data = [
        {
            "id": 1,
            "name": "Simple Login",
            "description": "Vulnerable login application with SQL Injection and weak authentication",
            "docker_image": "attack-simulation-login",
            "port": 5001,
            "status": "stopped"
        },
        {
            "id": 2,
            "name": "Blog",
            "description": "Blog application with Stored and Reflected XSS vulnerabilities",
            "docker_image": "attack-simulation-blog",
            "port": 5002,
            "status": "stopped"
        },
        {
            "id": 3,
            "name": "Ecommerce",
            "description": "Ecommerce application with IDOR vulnerabilities",
            "docker_image": "attack-simulation-ecommerce",
            "port": 5003,
            "status": "stopped"
        },
        {
            "id": 4,
            "name": "File Upload",
            "description": "File upload service with unsafe file upload vulnerability",
            "docker_image": "attack-simulation-fileupload",
            "port": 5004,
            "status": "stopped"
        }
    ]

    # Add labs to database
    for lab_data in labs_data:
        lab = db.query(Lab).filter(Lab.id == lab_data["id"]).first()
        if not lab:
            lab = Lab(**lab_data)
            db.add(lab)
        else:
            # Update existing lab
            for key, value in lab_data.items():
                setattr(lab, key, value)

    db.commit()
    db.close()
    print("Labs initialized successfully!")

if __name__ == "__main__":
    init_labs()