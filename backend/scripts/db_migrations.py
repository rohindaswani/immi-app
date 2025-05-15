#!/usr/bin/env python3

import logging
import sys
import os
import argparse
from sqlalchemy import text, inspect, MetaData, Table, Column, create_engine
from sqlalchemy.exc import SQLAlchemyError

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.db.postgres import engine, Base
from app.db.init_db import init_db
from app.db.models import *  # Import all models
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("db_migrations")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """
    Create all tables defined in models.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error creating tables: {e}")
        sys.exit(1)

def drop_tables():
    """
    Drop all tables in the database (DANGEROUS).
    """
    try:
        logger.info("Dropping all database tables...")
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except SQLAlchemyError as e:
        logger.error(f"Error dropping tables: {e}")
        sys.exit(1)

def reset_database():
    """
    Reset the database by dropping and recreating all tables (DANGEROUS).
    """
    try:
        logger.info("Resetting database...")
        drop_tables()
        create_tables()
        
        # Initialize database with seed data
        db = SessionLocal()
        try:
            init_db(db)
            logger.info("Database initialized with seed data")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
        finally:
            db.close()
            
        logger.info("Database reset successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        sys.exit(1)

def test_connection():
    """
    Test database connection.
    """
    try:
        logger.info("Testing database connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            for row in result:
                logger.info(f"Connection test result: {row}")
        logger.info("Database connection is working")
    except SQLAlchemyError as e:
        logger.error(f"Database connection error: {e}")
        sys.exit(1)

def list_tables():
    """
    List all tables in the database.
    """
    try:
        logger.info("Listing database tables...")
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            logger.info("No tables found in the database")
        else:
            logger.info("Database tables:")
            for table in tables:
                logger.info(f"- {table}")
    except SQLAlchemyError as e:
        logger.error(f"Error listing tables: {e}")
        sys.exit(1)

def main():
    """
    Main function to parse arguments and run commands.
    """
    parser = argparse.ArgumentParser(description="Database migration tool")
    parser.add_argument(
        "--action", 
        choices=["create", "drop", "reset", "test", "list_tables"], 
        required=True,
        help="Action to perform"
    )
    parser.add_argument(
        "--confirm", 
        action="store_true",
        help="Confirm dangerous operations"
    )
    
    args = parser.parse_args()
    
    # Check confirmation for dangerous operations
    if args.action in ["drop", "reset"] and not args.confirm:
        logger.error(f"Action '{args.action}' requires confirmation. Use --confirm flag to proceed.")
        sys.exit(1)
    
    # Execute the requested action
    if args.action == "create":
        create_tables()
    elif args.action == "drop":
        drop_tables()
    elif args.action == "reset":
        reset_database()
    elif args.action == "test":
        test_connection()
    elif args.action == "list_tables":
        list_tables()

if __name__ == "__main__":
    main()