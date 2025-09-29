#!/usr/bin/env python3
"""
Script to list users and create profiles
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import User, ImmigrationProfile

# Database connection
DATABASE_URL = "postgresql://postgres:password@localhost:5432/immigration_advisor"

def list_users():
    """List all users in the database"""
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        if not users:
            print("No users found in database")
            return
        
        print(f"\nFound {len(users)} users:")
        print("-" * 80)
        for user in users:
            # Check if profile exists
            profile = db.query(ImmigrationProfile).filter(
                ImmigrationProfile.user_id == user.user_id
            ).first()
            
            profile_status = "✅ Has Profile" if profile else "❌ No Profile"
            
            full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "No Name"
            
            print(f"Email: {user.email}")
            print(f"Name: {full_name}")
            print(f"User ID: {user.user_id}")
            print(f"Profile: {profile_status}")
            print(f"Created: {user.created_at}")
            print("-" * 80)
    
    except Exception as e:
        print(f"Error listing users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()