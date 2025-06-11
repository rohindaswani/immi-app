"""
Initialize location data (countries, states, cities) for development.
This script ensures the required reference data exists in the database.
"""

import sys
import os
import uuid
from sqlalchemy.orm import Session

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.postgres import get_db, engine, Base
from app.db.models import Country, State, City


def ensure_locations_exist():
    """
    Ensure that the required location data exists in the database.
    Create the data if it doesn't exist.
    """
    db = next(get_db())
    
    # Required UUIDs from the error message
    country_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")  # USA
    state_id = uuid.UUID("423e4567-e89b-12d3-a456-426614174000")    # California 
    city_id = uuid.UUID("a23e4567-e89b-12d3-a456-426614174000")     # San Francisco
    
    # Check if country exists by code (which has a unique constraint)
    country = db.query(Country).filter(Country.country_code == "USA").first()
    if not country:
        print(f"Creating country with ID: {country_id}")
        country = Country(
            country_id=country_id,
            country_name="United States of America",
            country_code="USA",
            is_visa_required_for_us_travel=False,
            region="North America"
        )
        db.add(country)
        db.commit()
    else:
        # If country exists but with different ID, handle the references and update
        if country.country_id != country_id:
            old_country_id = country.country_id
            print(f"Country 'USA' exists with ID: {old_country_id}, need: {country_id}")
            
            # Create a new country with the desired ID
            new_country = Country(
                country_id=country_id,
                country_name=country.country_name,
                country_code=country.country_code,
                is_visa_required_for_us_travel=country.is_visa_required_for_us_travel,
                region=country.region
            )
            db.add(new_country)
            db.commit()
            
            # Update all states that reference the old country ID
            states_to_update = db.query(State).filter(State.country_id == old_country_id).all()
            for state in states_to_update:
                print(f"Updating state {state.state_name} to use new country ID")
                state.country_id = country_id
            
            # Update all cities that reference the old country ID
            cities_to_update = db.query(City).filter(City.country_id == old_country_id).all()
            for city in cities_to_update:
                print(f"Updating city {city.city_name} to use new country ID")
                city.country_id = country_id
            
            # Commit the changes to states and cities
            db.commit()
            
            # Now delete the old country record
            print(f"Deleting old country record with ID: {old_country_id}")
            db.query(Country).filter(Country.country_id == old_country_id).delete()
            db.commit()
            
            # Assign the new country to the country variable for continued use
            country = new_country
    
    # Check if state exists, by name and country
    state = db.query(State).filter(
        State.state_code == "CA",
        State.country_id == country_id
    ).first()
    
    if not state:
        print(f"Creating state with ID: {state_id}")
        state = State(
            state_id=state_id,
            state_name="California",
            state_code="CA",
            country_id=country_id
        )
        db.add(state)
        db.commit()
    else:
        # If state exists but with different ID, handle the references and update
        if state.state_id != state_id:
            old_state_id = state.state_id
            print(f"State 'CA' exists with ID: {old_state_id}, need: {state_id}")
            
            # Create a new state with the desired ID
            new_state = State(
                state_id=state_id,
                state_name=state.state_name,
                state_code=state.state_code,
                country_id=country_id
            )
            db.add(new_state)
            db.commit()
            
            # Update all cities that reference the old state ID
            cities_to_update = db.query(City).filter(City.state_id == old_state_id).all()
            for city in cities_to_update:
                print(f"Updating city {city.city_name} to use new state ID")
                city.state_id = state_id
            
            # Commit the changes to cities
            db.commit()
            
            # Now delete the old state record
            print(f"Deleting old state record with ID: {old_state_id}")
            db.query(State).filter(State.state_id == old_state_id).delete()
            db.commit()
            
            # Assign the new state to the state variable for continued use
            state = new_state
    
    # Check if city exists, by name, state and country
    city = db.query(City).filter(
        City.city_name == "San Francisco",
        City.state_id == state_id,
        City.country_id == country_id
    ).first()
    
    if not city:
        print(f"Creating city with ID: {city_id}")
        city = City(
            city_id=city_id,
            city_name="San Francisco",
            state_id=state_id,
            country_id=country_id
        )
        db.add(city)
        db.commit()
    else:
        # If city exists but with different ID, update its ID to match what we need
        if city.city_id != city_id:
            print(f"Updating city ID from {city.city_id} to {city_id}")
            city.city_id = city_id
            db.commit()
    
    # Add a few more common locations
    ensure_common_locations(db)
    
    print("Location data initialization complete.")


def ensure_common_locations(db: Session):
    """Add some common locations"""
    # New York (NY, USA)
    ny_state_id = uuid.UUID("523e4567-e89b-12d3-a456-426614174000")
    ny_city_id = uuid.UUID("b23e4567-e89b-12d3-a456-426614174000")
    
    country_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")  # USA
    
    # Check if NY state exists by code and country
    state = db.query(State).filter(
        State.state_code == "NY",
        State.country_id == country_id
    ).first()
    
    if not state:
        print(f"Creating state with ID: {ny_state_id}")
        state = State(
            state_id=ny_state_id,
            state_name="New York",
            state_code="NY",
            country_id=country_id
        )
        db.add(state)
        db.commit()
    else:
        # If state exists but with different ID, handle the references and update
        if state.state_id != ny_state_id:
            old_state_id = state.state_id
            print(f"State 'NY' exists with ID: {old_state_id}, need: {ny_state_id}")
            
            # Create a new state with the desired ID
            new_state = State(
                state_id=ny_state_id,
                state_name=state.state_name,
                state_code=state.state_code,
                country_id=country_id
            )
            db.add(new_state)
            db.commit()
            
            # Update all cities that reference the old state ID
            cities_to_update = db.query(City).filter(City.state_id == old_state_id).all()
            for city in cities_to_update:
                print(f"Updating city {city.city_name} to use new state ID")
                city.state_id = ny_state_id
            
            # Commit the changes to cities
            db.commit()
            
            # Now delete the old state record
            print(f"Deleting old state record with ID: {old_state_id}")
            db.query(State).filter(State.state_id == old_state_id).delete()
            db.commit()
            
            # Assign the new state to the state variable for continued use
            state = new_state
    
    # Check if NY city exists by name, state and country
    city = db.query(City).filter(
        City.city_name == "New York City",
        City.state_id == ny_state_id,
        City.country_id == country_id
    ).first()
    
    if not city:
        print(f"Creating city with ID: {ny_city_id}")
        city = City(
            city_id=ny_city_id,
            city_name="New York City",
            state_id=ny_state_id,
            country_id=country_id
        )
        db.add(city)
        db.commit()
    else:
        # If city exists but with different ID, update its ID
        if city.city_id != ny_city_id:
            print(f"Updating city ID from {city.city_id} to {ny_city_id}")
            city.city_id = ny_city_id
            db.commit()


if __name__ == "__main__":
    print("Initializing location data...")
    ensure_locations_exist()