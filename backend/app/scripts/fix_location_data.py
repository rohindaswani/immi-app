"""
Fix location data references in the database.
This script directly fixes references in the database without trying to create new records.
"""

import sys
import os
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.postgres import get_db, engine, Base

def fix_location_references():
    """
    Fix location data references by directly updating database records.
    """
    db = next(get_db())
    
    # Required UUIDs from the error message
    country_id = "123e4567-e89b-12d3-a456-426614174000"  # USA
    state_id = "423e4567-e89b-12d3-a456-426614174000"    # California 
    city_id = "a23e4567-e89b-12d3-a456-426614174000"     # San Francisco
    
    # Use raw SQL to avoid SQLAlchemy ORM constraints

    # 1. Check if USA exists first
    country_count = db.execute(
        text("SELECT COUNT(*) FROM countries WHERE country_code = 'USA'")
    ).scalar()
    
    current_country_id = None
    if country_count > 0:
        # Get the current ID if it exists
        current_country_id = db.execute(
            text("SELECT country_id FROM countries WHERE country_code = 'USA'")
        ).scalar()
        print(f"Found existing USA country record with ID: {current_country_id}")
    
    # Create a temporary ID mapping table
    existing_countries = {}
    if current_country_id:
        existing_countries[current_country_id] = country_id
    
    # 2. Either create the USA record or update existing one
    if country_count == 0:
        print("Creating USA country record")
        db.execute(
            text("""
            INSERT INTO countries (country_id, country_name, country_code, is_visa_required_for_us_travel, region)
            VALUES (:country_id, 'United States of America', 'USA', FALSE, 'North America')
            """),
            {"country_id": country_id}
        )
    else:
        # If the country exists with a different ID, we need to create a new one
        if str(current_country_id) != country_id:
            print(f"Creating new USA country record with ID: {country_id}")
            
            # Check if we can safely delete the old country
            has_dependencies = db.execute(
                text("""
                SELECT COUNT(*) FROM (
                    SELECT 1 FROM states WHERE country_id = :old_id
                    UNION ALL
                    SELECT 1 FROM cities WHERE country_id = :old_id
                ) AS dependencies
                """),
                {"old_id": current_country_id}
            ).scalar()
            
            if has_dependencies > 0:
                print("Country has dependencies - can't safely replace it. Keeping existing ID.")
                # We'll use the existing ID instead
                country_id = str(current_country_id)
                print(f"Using existing country ID: {country_id}")
            else:
                # Safe to replace
                print("Deleting old country record and creating new one")
                db.execute(
                    text("DELETE FROM countries WHERE country_id = :old_id"),
                    {"old_id": current_country_id}
                )
                db.execute(
                    text("""
                    INSERT INTO countries (country_id, country_name, country_code, is_visa_required_for_us_travel, region)
                    VALUES (:country_id, 'United States of America', 'USA', FALSE, 'North America')
                    """),
                    {"country_id": country_id}
                )
    
    # Commit after country creation
    db.commit()
    
    # 3. Check if California exists
    state_count = db.execute(
        text("""
        SELECT COUNT(*) FROM states 
        WHERE state_code = 'CA' AND country_id = :country_id
        """),
        {"country_id": country_id}
    ).scalar()
    
    current_state_id = None
    if state_count > 0:
        # Get the current ID if it exists
        current_state_id = db.execute(
            text("""
            SELECT state_id FROM states 
            WHERE state_code = 'CA' AND country_id = :country_id
            """),
            {"country_id": country_id}
        ).scalar()
        print(f"Found existing CA state record with ID: {current_state_id}")
    
    # 4. Either create or update the state
    if state_count == 0:
        print("Creating California state record")
        db.execute(
            text("""
            INSERT INTO states (state_id, state_name, state_code, country_id)
            VALUES (:state_id, 'California', 'CA', :country_id)
            """),
            {"state_id": state_id, "country_id": country_id}
        )
    else:
        # If the state exists but with a different ID
        if str(current_state_id) != state_id:
            print(f"State 'CA' exists with ID: {current_state_id}, need: {state_id}")
            
            # We'll use the existing ID instead since changing it would break references
            print(f"Using existing state ID: {current_state_id}")
            state_id = str(current_state_id)
    
    # Commit after state creation/update
    db.commit()
    
    # 5. Check if San Francisco exists
    city_count = db.execute(
        text("""
        SELECT COUNT(*) FROM cities 
        WHERE city_name = 'San Francisco' AND country_id = :country_id
        """),
        {"country_id": country_id}
    ).scalar()
    
    if city_count == 0:
        print("Creating San Francisco city record")
        db.execute(
            text("""
            INSERT INTO cities (city_id, city_name, state_id, country_id)
            VALUES (:city_id, 'San Francisco', :state_id, :country_id)
            """),
            {"city_id": city_id, "state_id": state_id, "country_id": country_id}
        )
    else:
        # If the city exists, update its ID
        current_city_id = db.execute(
            text("""
            SELECT city_id FROM cities 
            WHERE city_name = 'San Francisco' AND country_id = :country_id
            """),
            {"country_id": country_id}
        ).scalar()
        
        if str(current_city_id) != city_id:
            print(f"Updating existing city ID from {current_city_id} to {city_id}")
            db.execute(
                text("""
                UPDATE cities
                SET city_id = :new_city_id
                WHERE city_id = :old_city_id
                """),
                {"new_city_id": city_id, "old_city_id": current_city_id}
            )
    
    # Commit all city changes
    db.commit()
    
    # 6. Add New York state and city
    print("Adding New York locations...")
    
    ny_state_id = "523e4567-e89b-12d3-a456-426614174000"
    ny_city_id = "b23e4567-e89b-12d3-a456-426614174000"
    
    # Check if NY state exists
    ny_state_count = db.execute(
        text("""
        SELECT COUNT(*) FROM states 
        WHERE state_code = 'NY' AND country_id = :country_id
        """),
        {"country_id": country_id}
    ).scalar()
    
    current_ny_state_id = None
    if ny_state_count > 0:
        current_ny_state_id = db.execute(
            text("""
            SELECT state_id FROM states 
            WHERE state_code = 'NY' AND country_id = :country_id
            """),
            {"country_id": country_id}
        ).scalar()
        print(f"Found existing NY state with ID: {current_ny_state_id}")
    
    # Create or update NY state
    if ny_state_count == 0:
        print("Creating New York state record")
        db.execute(
            text("""
            INSERT INTO states (state_id, state_name, state_code, country_id)
            VALUES (:state_id, 'New York', 'NY', :country_id)
            """),
            {"state_id": ny_state_id, "country_id": country_id}
        )
    else:
        if str(current_ny_state_id) != ny_state_id:
            print(f"State 'NY' exists with ID: {current_ny_state_id}, need: {ny_state_id}")
            
            # We'll use the existing ID instead since changing it would break references
            print(f"Using existing state ID: {current_ny_state_id}")
            ny_state_id = str(current_ny_state_id)
    
    # Commit state changes
    db.commit()
    
    # Check if NYC exists
    nyc_count = db.execute(
        text("""
        SELECT COUNT(*) FROM cities 
        WHERE city_name = 'New York City' AND country_id = :country_id
        """),
        {"country_id": country_id}
    ).scalar()
    
    if nyc_count == 0:
        print("Creating New York City record")
        db.execute(
            text("""
            INSERT INTO cities (city_id, city_name, state_id, country_id)
            VALUES (:city_id, 'New York City', :state_id, :country_id)
            """),
            {"city_id": ny_city_id, "state_id": ny_state_id, "country_id": country_id}
        )
    else:
        current_nyc_id = db.execute(
            text("""
            SELECT city_id FROM cities 
            WHERE city_name = 'New York City' AND country_id = :country_id
            """),
            {"country_id": country_id}
        ).scalar()
        
        if str(current_nyc_id) != ny_city_id:
            print(f"Updating NYC ID from {current_nyc_id} to {ny_city_id}")
            db.execute(
                text("""
                UPDATE cities
                SET city_id = :new_city_id
                WHERE city_id = :old_city_id
                """),
                {"new_city_id": ny_city_id, "old_city_id": current_nyc_id}
            )
    
    # Commit city changes
    db.commit()
    
    # Commit all changes
    db.commit()
    print("Location data fix complete.")


if __name__ == "__main__":
    print("Fixing location data references...")
    fix_location_references()