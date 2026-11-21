from sqlalchemy.orm import Session
from models import base
from database import get_db
from fastapi import Depends

def init_db(db: Session = Depends(get_db)):
    available_labs = [
        {
            "id": 1,
            "name": "Simple Login",
            "description": "Vulnerable login application with SQL Injection and weak authentication",
            "external_url": "https://login-system-6tla.onrender.com/",
        },
        {
            "id": 2,
            "name": "Blog",
            "description": "Blog application with Stored and Reflected XSS vulnerabilities",
            "external_url": "https://xss-blog-site.onrender.com/",
        },
        {
            "id": 3,
            "name": "Ecommerce",
            "description": "Ecommerce application with IDOR vulnerabilities",
            "external_url": "https://e-commerce-b6wh.onrender.com/",
        },
        {
            "id": 4,
            "name": "File Upload",
            "description": "File upload service with unsafe file upload vulnerability",
            "external_url": "https://file-upload-mlnv.onrender.com/",
        },
    ]

    # Create or update lab records in database
    for lab_data in available_labs:
        db_lab = db.query(base.Lab).filter(base.Lab.id == lab_data['id']).first()
        if not db_lab:
            db_lab = base.Lab(
                id=lab_data['id'],
                name=lab_data['name'],
                description=lab_data['description'],
                external_url=lab_data['external_url']
            )
            print(f"Adding lab {lab_data['name']} to DB")
            db.add(db_lab)
        else:
            db_lab.name = lab_data['name']
            db_lab.description = lab_data['description']
            db_lab.external_url = lab_data['external_url']
            print(f"Updating lab {lab_data['name']} in DB")

    db.commit()
    print("Labs initialized in the Database.")

if __name__ == "__main__":
    db = next(get_db())
    init_db(db)
