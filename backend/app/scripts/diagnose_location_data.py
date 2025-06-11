"""
Diagnose and fix location data issues.
This script will print out the current state of location data and fix specific records.
"""

import sys
import os
import uuid
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.postgres import get_db, engine, Base

def diagnose_and_fix():
    """
    Print current state of location data and fix issues.
    """
    db = next(get_db())
    
    # Target IDs from the form
    target_country_id = "123e4567-e89b-12d3-a456-426614174000"  # USA
    target_state_id = "423e4567-e89b-12d3-a456-426614174000"    # California 
    target_city_id = "a23e4567-e89b-12d3-a456-426614174000"     # San Francisco
    
    print("\n=== COUNTRIES ===")
    countries = db.execute(text("SELECT country_id, country_name, country_code FROM countries")).fetchall()
    for country in countries:
        print(f"{country.country_id} | {country.country_name} | {country.country_code}")
    
    print("\n=== STATES ===")
    states = db.execute(text("SELECT state_id, state_name, state_code, country_id FROM states")).fetchall()
    for state in states:
        print(f"{state.state_id} | {state.state_name} | {state.state_code} | {state.country_id}")
    
    print("\n=== CITIES ===")
    cities = db.execute(text("SELECT city_id, city_name, state_id, country_id FROM cities")).fetchall()
    for city in cities:
        print(f"{city.city_id} | {city.city_name} | {city.state_id} | {city.country_id}")
    
    # Check if the target California state exists
    ca_state = db.execute(
        text("SELECT state_id FROM states WHERE state_code = 'CA'")
    ).fetchone()
    
    if ca_state:
        actual_state_id = str(ca_state.state_id)
        print(f"\nCalifornia state exists with ID: {actual_state_id}")
        print(f"Target state ID from form: {target_state_id}")
        
        if actual_state_id != target_state_id:
            print(f"\nWARNING: The California state ID in the database ({actual_state_id}) " 
                  f"does not match the ID used in the form ({target_state_id}).")
            
            # Fix option 1: Create a new state with the target ID
            print("\nOption 1: Creating a new California state with the target ID.")
            try:
                db.execute(
                    text("""
                    INSERT INTO states (state_id, state_name, state_code, country_id)
                    VALUES (:state_id, 'California', 'CA', :country_id)
                    """),
                    {"state_id": target_state_id, "country_id": target_country_id}
                )
                db.commit()
                print("Successfully created new California state with the target ID.")
            except Exception as e:
                print(f"Error creating new state: {e}")
                db.rollback()
            
            # Fix option 2: Update form schema to use existing ID
            print(f"\nOption 2: Update your form schema to use the existing California state ID: {actual_state_id}")
            print("To do this, update your AddressCreate schema to use this ID.")
    else:
        print("\nCalifornia state does not exist. Creating it now...")
        try:
            db.execute(
                text("""
                INSERT INTO states (state_id, state_name, state_code, country_id)
                VALUES (:state_id, 'California', 'CA', :country_id)
                """),
                {"state_id": target_state_id, "country_id": target_country_id}
            )
            db.commit()
            print(f"Successfully created California state with ID: {target_state_id}")
        except Exception as e:
            print(f"Error creating state: {e}")
            db.rollback()

if __name__ == "__main__":
    print("Diagnosing location data issues...")
    diagnose_and_fix()