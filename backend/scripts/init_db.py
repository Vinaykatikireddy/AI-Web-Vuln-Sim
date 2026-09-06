from sqlalchemy.orm import Session
from models import base
from database import get_db
from fastapi import Depends
from services.lab_manager import LabManager

lab_manager = LabManager()
def init_db(db: Session = Depends(get_db)):
    available_labs = [
        {
            "id": 1,
            "name": "Simple Login",
            "description": "Vulnerable login application with SQL Injection and weak authentication",
            "docker_image": "attack-simulation-login",
            "port": 5001,
            "external_url": "https://login-system-6tla.onrender.com/",
        },
        {
            "id": 2,
            "name": "Blog",
            "description": "Blog application with Stored and Reflected XSS vulnerabilities",
            "docker_image": "attack-simulation-blog",
            "port": 5002,
            "external_url": "https://xss-blog-site.onrender.com/",
        },
        {
            "id": 3,
            "name": "Ecommerce",
            "description": "Ecommerce application with IDOR vulnerabilities",
            "docker_image": "attack-simulation-ecommerce",
            "port": 5003,
            "external_url": "https://e-commerce-b6wh.onrender.com/",
        },
        {
            "id": 4,
            "name": "File Upload",
            "description": "File upload service with unsafe file upload vulnerability",
            "docker_image": "attack-simulation-fileupload",
            "port": 5004,
            "external_url": "https://file-upload-mlnv.onrender.com/",
        },
    ]

    # Create lab records in database
    for lab_data in available_labs:
        db_lab = db.query(base.Lab).filter(base.Lab.id == lab_data['id']).first()
        if not db_lab:
            db_lab = base.Lab(
                id=lab_data['id'],
                name=lab_data['name'],
                description=lab_data['description'],
                status="stopped",
                docker_image=lab_data['docker_image'],
                port=lab_data['port'],
                external_url=lab_data.get('external_url')
            )
            db.add(db_lab)
    print("Labs added to the Database.")

    db.commit()

db = next(get_db())
init_db(db)