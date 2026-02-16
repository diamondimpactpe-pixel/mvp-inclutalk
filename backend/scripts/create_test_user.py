#!/usr/bin/env python3
"""
Script para crear un nuevo usuario de prueba
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import User, UserRole
from app.auth.security import get_password_hash

def create_test_user():
    db = SessionLocal()
    
    try:
        # Crear nuevo operador de prueba
        new_user = User(
            institution_id=1,  # Usar la institución existente
            email="test@inclutalk.com",
            username="testuser",
            password_hash=get_password_hash("Test1234!"),
            role=UserRole.OPERATOR,
            first_name="Usuario",
            last_name="Prueba",
            is_active=1
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print("\n" + "="*60)
        print("✅ NUEVO USUARIO CREADO!")
        print("="*60)
        print(f"\nEmail: test@inclutalk.com")
        print(f"Password: Test1234!")
        print(f"Rol: {new_user.role}")
        print(f"ID: {new_user.id}")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
