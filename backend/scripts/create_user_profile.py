#!/usr/bin/env python3
"""
Script to create a user profile in the database for testing
"""

import asyncio
import sys
from datetime import date, datetime
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import ImmigrationProfile, User
from app.core.config import settings
import uuid

# Database connection
DATABASE_URL = "postgresql://postgres:password@localhost:5432/immigration_advisor"

def create_profile_for_user(user_email: str):
    """Create an immigration profile for a user"""
    
    # Create database session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find the user by email
        user = db.query(User).filter(User.email == user_email).first()
        
        if not user:
            print(f"User with email {user_email} not found!")
            print("\nCreating a new user first...")
            
            # Create a new user
            new_user = User(
                user_id=uuid.uuid4(),
                email=user_email,
                password_hash="dummy_hash",  # Required field
                first_name="Test",
                last_name="User",
                is_active=True,
                email_verified=True
            )
            db.add(new_user)
            db.commit()
            user = new_user
            print(f"Created user: {user.email}")
        
        # Check if profile already exists
        existing_profile = db.query(ImmigrationProfile).filter(
            ImmigrationProfile.user_id == user.user_id
        ).first()
        
        if existing_profile:
            print(f"Profile already exists for user {user_email}")
            print(f"Profile ID: {existing_profile.profile_id}")
            return existing_profile
        
        # Create a new immigration profile
        profile = ImmigrationProfile(
            profile_id=uuid.uuid4(),
            user_id=user.user_id,
            
            # Entry Information
            most_recent_entry_date=date(2023, 1, 10),
            most_recent_i94_number="I94-123456789",
            authorized_stay_until=date(2026, 9, 30),
            
            # Passport Information
            passport_number="P123456789",
            passport_expiry_date=date(2028, 12, 31),
            
            # Visa Information
            visa_expiry_date=date(2026, 9, 30),
            ead_expiry_date=date(2026, 9, 30),
            
            # Priority Dates (for green card)
            current_priority_dates={
                "EB2": {
                    "date": "2020-06-15",
                    "current": False
                }
            },
            
            # Additional fields
            immigration_goals="Obtain green card through employment",
            is_primary_beneficiary=True,
            profile_type="primary",
            notes="H1-B visa holder working at tech company"
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        print(f"\nSuccessfully created immigration profile!")
        print(f"Profile ID: {profile.profile_id}")
        print(f"User: {user.email}")
        print(f"I-94: {profile.most_recent_i94_number}")
        print(f"Authorized Stay Until: {profile.authorized_stay_until}")
        print(f"Visa Expiry: {profile.visa_expiry_date}")
        
        return profile
        
    except Exception as e:
        print(f"Error creating profile: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    """Main function"""
    
    # Default email or get from command line args
    if len(sys.argv) > 1:
        user_email = sys.argv[1]
    else:
        user_email = "test@example.com"
    
    print(f"Creating profile for user: {user_email}")
    
    try:
        profile = create_profile_for_user(user_email)
        print("\n✅ Profile creation completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Failed to create profile: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()