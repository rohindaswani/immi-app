#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.postgres import Base, engine
from app.db.init_db import init_db
from app.db.postgres import SessionLocal

def main():
    print("Creating database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        # Initialize with seed data
        db = SessionLocal()
        try:
            init_db(db)
            print("✅ Database initialized with seed data")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()