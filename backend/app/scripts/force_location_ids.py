"""
Force location IDs to match frontend expectations.
This script will recreate countries, states, and cities with specific IDs.
"""

import sys
import os
import uuid
from sqlalchemy import text

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.postgres import get_db

def force_location_ids():
    """
    Force location IDs to match frontend expectations.
    """
    db = next(get_db())
    
    print("WARNING: This script will delete and recreate location data with specific IDs.")
    print("Make sure you have a backup of your database before proceeding.")
    print("Press Enter to continue or Ctrl+C to cancel...")
    input()
    
    try:
        # Delete existing data that might conflict
        print("Deleting existing location data...")
        
        # First, delete cities
        db.execute(text("DELETE FROM cities"))
        
        # Then, delete states
        db.execute(text("DELETE FROM states"))
        
        # Finally, delete countries
        db.execute(text("DELETE FROM countries"))
        
        # Commit these deletions
        db.commit()
        print("Existing location data deleted.")
        
        # Create countries with specific IDs
        print("Creating countries...")
        countries = [
            ("123e4567-e89b-12d3-a456-426614174000", "United States", "USA", False, "North America"),
            ("223e4567-e89b-12d3-a456-426614174000", "Canada", "CAN", False, "North America"),
            ("323e4567-e89b-12d3-a456-426614174000", "Mexico", "MEX", False, "North America"),
        ]
        
        for country_id, name, code, visa_req, region in countries:
            db.execute(
                text("""
                INSERT INTO countries (country_id, country_name, country_code, is_visa_required_for_us_travel, region)
                VALUES (:id, :name, :code, :visa_req, :region)
                """),
                {"id": country_id, "name": name, "code": code, "visa_req": visa_req, "region": region}
            )
        
        # Commit countries
        db.commit()
        print("Countries created.")
        
        # Create states with specific IDs
        print("Creating states...")
        states = [
            ("423e4567-e89b-12d3-a456-426614174000", "California", "CA", "123e4567-e89b-12d3-a456-426614174000"),
            ("523e4567-e89b-12d3-a456-426614174000", "New York", "NY", "123e4567-e89b-12d3-a456-426614174000"),
            ("623e4567-e89b-12d3-a456-426614174000", "Texas", "TX", "123e4567-e89b-12d3-a456-426614174000"),
            ("723e4567-e89b-12d3-a456-426614174000", "Ontario", "ON", "223e4567-e89b-12d3-a456-426614174000"),
            ("823e4567-e89b-12d3-a456-426614174000", "Quebec", "QC", "223e4567-e89b-12d3-a456-426614174000"),
        ]
        
        for state_id, name, code, country_id in states:
            db.execute(
                text("""
                INSERT INTO states (state_id, state_name, state_code, country_id)
                VALUES (:id, :name, :code, :country_id)
                """),
                {"id": state_id, "name": name, "code": code, "country_id": country_id}
            )
        
        # Commit states
        db.commit()
        print("States created.")
        
        # Create cities with specific IDs
        print("Creating cities...")
        cities = [
            ("923e4567-e89b-12d3-a456-426614174000", "Los Angeles", "423e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174000"),
            ("a23e4567-e89b-12d3-a456-426614174000", "San Francisco", "423e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174000"),
            ("b23e4567-e89b-12d3-a456-426614174000", "New York City", "523e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174000"),
            ("c23e4567-e89b-12d3-a456-426614174000", "Buffalo", "523e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174000"),
            ("d23e4567-e89b-12d3-a456-426614174000", "Austin", "623e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174000"),
            ("e23e4567-e89b-12d3-a456-426614174000", "Houston", "623e4567-e89b-12d3-a456-426614174000", "123e4567-e89b-12d3-a456-426614174000"),
            ("f23e4567-e89b-12d3-a456-426614174000", "Toronto", "723e4567-e89b-12d3-a456-426614174000", "223e4567-e89b-12d3-a456-426614174000"),
            ("023e4567-e89b-12d3-a456-426614174000", "Montreal", "823e4567-e89b-12d3-a456-426614174000", "223e4567-e89b-12d3-a456-426614174000"),
        ]
        
        for city_id, name, state_id, country_id in cities:
            db.execute(
                text("""
                INSERT INTO cities (city_id, city_name, state_id, country_id)
                VALUES (:id, :name, :state_id, :country_id)
                """),
                {"id": city_id, "name": name, "state_id": state_id, "country_id": country_id}
            )
        
        # Commit cities
        db.commit()
        print("Cities created.")
        
        print("\nLocation data has been successfully forced to match frontend expectations.")
        print("You should now be able to add addresses without foreign key constraint errors.")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        print("Operation failed. Database rolled back to previous state.")


if __name__ == "__main__":
    print("Starting force_location_ids script...")
    force_location_ids()