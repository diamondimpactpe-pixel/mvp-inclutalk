#!/usr/bin/env python3
"""Seed initial data"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import Institution, User, InstitutionSector, UserRole
from app.auth.security import get_password_hash

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        existing = db.query(Institution).filter(Institution.name == "Hospital Central").first()
        if existing:
            print("Data already exists. Skipping.")
            return
        
        institution = Institution(
            name="Hospital Central",
            sector=InstitutionSector.HEALTHCARE,
            contact_email="contacto@hospital.com",
            is_active=1
        )
        db.add(institution)
        db.commit()
        db.refresh(institution)
        
        admin = User(
            institution_id=institution.id,
            email="admin@hospital.com",
            username="admin_hospital",
            password_hash=get_password_hash("Admin123!"),
            role=UserRole.ADMIN,
            first_name="Admin",
            last_name="Hospital",
            is_active=1
        )
        db.add(admin)
        
        operator = User(
            institution_id=institution.id,
            email="operator@hospital.com",
            username="operator1",
            password_hash=get_password_hash("Operator123!"),
            role=UserRole.OPERATOR,
            first_name="María",
            last_name="García",
            is_active=1
        )
        db.add(operator)
        db.commit()
        
        print("\n✅ SEED EXITOSO!")
        print(f"\nAdmin: {admin.email} / Admin123!")
        print(f"Operator: {operator.email} / Operator123!\n")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
