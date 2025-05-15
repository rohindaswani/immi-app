#!/usr/bin/env python3

import sys
import os
import logging
from sqlalchemy import text
from pymongo import MongoClient
import redis

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("test_db")

# Import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings
from app.db.postgres import engine
from app.db.mongodb import client as mongo_client

def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        logger.info("Testing PostgreSQL connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            for row in result:
                logger.info(f"PostgreSQL connection test result: {row}")
        logger.info("PostgreSQL connection is working ✅")
        return True
    except Exception as e:
        logger.error(f"PostgreSQL connection error: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        logger.info("Testing MongoDB connection...")
        if mongo_client is None:
            logger.error("MongoDB client is not initialized")
            return False
            
        # Get server info to test connection
        server_info = mongo_client.server_info()
        logger.info(f"MongoDB version: {server_info.get('version', 'unknown')}")
        logger.info("MongoDB connection is working ✅")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        return False

def test_redis_connection():
    """Test Redis connection"""
    try:
        logger.info("Testing Redis connection...")
        
        # Create Redis client
        redis_client = redis.from_url(settings.REDIS_URL)
        
        # Set a test value
        redis_client.set("test_key", "test_value")
        
        # Get the test value
        value = redis_client.get("test_key")
        logger.info(f"Redis test value: {value}")
        
        # Clean up
        redis_client.delete("test_key")
        
        logger.info("Redis connection is working ✅")
        return True
    except Exception as e:
        logger.error(f"Redis connection error: {e}")
        return False

def main():
    """Run all database connection tests"""
    logger.info("Running database connection tests...\n")
    
    # PostgreSQL
    postgres_success = test_postgres_connection()
    
    # MongoDB
    mongodb_success = test_mongodb_connection()
    
    # Redis
    redis_success = test_redis_connection()
    
    # Print summary
    logger.info("\nTest Summary:")
    logger.info(f"PostgreSQL: {'✅ PASSED' if postgres_success else '❌ FAILED'}")
    logger.info(f"MongoDB: {'✅ PASSED' if mongodb_success else '❌ FAILED'}")
    logger.info(f"Redis: {'✅ PASSED' if redis_success else '❌ FAILED'}")
    
    # Return overall success/failure
    if postgres_success and mongodb_success and redis_success:
        logger.info("All database connections are working! 🎉")
        return 0
    else:
        logger.error("Some database connections failed. Please check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())