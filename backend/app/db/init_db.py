import logging
from sqlalchemy.orm import Session
import uuid

from app.db.postgres import Base, engine
from app.db.models import (
    User, UserSettings, ImmigrationStatus, Country, State, City
)
from app.core.security import get_password_hash

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """
    Initialize database with seed data.
    """
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create immigration statuses
    create_immigration_statuses(db)
    
    # Create some basic country data
    create_countries(db)
    
    # Create admin user if in development
    try:
        create_admin_user(db)
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")


def create_immigration_statuses(db: Session) -> None:
    """
    Create seed data for immigration statuses.
    """
    # Check if there are any existing statuses
    existing = db.query(ImmigrationStatus).first()
    if existing:
        logger.info("Immigration statuses already exist, skipping seed")
        return
    
    # Common immigration statuses
    statuses = [
        {
            "status_code": "H1-B",
            "status_name": "H-1B Specialty Occupation",
            "status_category": "Employment",
            "allows_employment": True,
            "employment_restrictions": "Limited to H-1B sponsoring employer",
            "max_duration": "6 years (3 years initially with 3-year extension)",
            "grace_period": "60 days",
            "is_dual_intent": True,
            "can_apply_for_adjustment_of_status": True,
            "requires_sponsor": True,
            "potential_next_statuses": ["H1-B1", "H1-B2", "H1-B3", "H4", "Green Card"]
        },
        {
            "status_code": "F1",
            "status_name": "F-1 Student",
            "status_category": "Student",
            "allows_employment": True,
            "employment_restrictions": "On-campus employment or CPT/OPT with approval",
            "max_duration": "Duration of studies",
            "grace_period": "60 days",
            "is_dual_intent": False,
            "can_apply_for_adjustment_of_status": True,
            "requires_sponsor": False,
            "potential_next_statuses": ["OPT", "STEM OPT", "H1-B", "O1"]
        },
        {
            "status_code": "L1",
            "status_name": "L-1 Intracompany Transferee",
            "status_category": "Employment",
            "allows_employment": True,
            "employment_restrictions": "Limited to L-1 sponsoring employer",
            "max_duration": "5-7 years depending on L-1A or L-1B",
            "grace_period": "10 days",
            "is_dual_intent": True,
            "can_apply_for_adjustment_of_status": True,
            "requires_sponsor": True,
            "potential_next_statuses": ["L2", "H1-B", "Green Card"]
        },
        {
            "status_code": "OPT",
            "status_name": "Optional Practical Training",
            "status_category": "Student",
            "allows_employment": True,
            "employment_restrictions": "Must be related to field of study",
            "max_duration": "12 months",
            "grace_period": "60 days",
            "is_dual_intent": False,
            "can_apply_for_adjustment_of_status": True,
            "requires_sponsor": False,
            "potential_next_statuses": ["STEM OPT", "H1-B", "O1"]
        },
        {
            "status_code": "STEM_OPT",
            "status_name": "STEM OPT Extension",
            "status_category": "Student",
            "allows_employment": True,
            "employment_restrictions": "Must be related to STEM field of study and have e-verify employer",
            "max_duration": "24 months",
            "grace_period": "60 days",
            "is_dual_intent": False,
            "can_apply_for_adjustment_of_status": True,
            "requires_sponsor": False,
            "potential_next_statuses": ["H1-B", "O1"]
        }
    ]
    
    for status_data in statuses:
        status = ImmigrationStatus(**status_data)
        db.add(status)
    
    db.commit()
    logger.info(f"Created {len(statuses)} immigration statuses")


def create_countries(db: Session) -> None:
    """
    Create seed data for countries.
    """
    # Check if there are any existing countries
    existing = db.query(Country).first()
    if existing:
        logger.info("Countries already exist, skipping seed")
        return
    
    # Common countries
    countries = [
        {
            "country_name": "United States",
            "country_code": "USA",
            "is_visa_required_for_us_travel": False,
            "region": "North America"
        },
        {
            "country_name": "Canada",
            "country_code": "CAN",
            "is_visa_required_for_us_travel": False,
            "region": "North America"
        },
        {
            "country_name": "Mexico",
            "country_code": "MEX",
            "is_visa_required_for_us_travel": True,
            "region": "North America"
        },
        {
            "country_name": "United Kingdom",
            "country_code": "GBR",
            "is_visa_required_for_us_travel": False,
            "region": "Europe"
        },
        {
            "country_name": "India",
            "country_code": "IND",
            "is_visa_required_for_us_travel": True,
            "region": "Asia"
        },
        {
            "country_name": "China",
            "country_code": "CHN",
            "is_visa_required_for_us_travel": True,
            "region": "Asia"
        }
    ]
    
    for country_data in countries:
        country = Country(**country_data)
        db.add(country)
    
    db.commit()
    logger.info(f"Created {len(countries)} countries")
    
    # Add some states for USA
    usa = db.query(Country).filter(Country.country_code == "USA").first()
    if usa:
        states = [
            {"state_name": "California", "state_code": "CA", "country_id": usa.country_id},
            {"state_name": "New York", "state_code": "NY", "country_id": usa.country_id},
            {"state_name": "Texas", "state_code": "TX", "country_id": usa.country_id},
            {"state_name": "Florida", "state_code": "FL", "country_id": usa.country_id},
            {"state_name": "Washington", "state_code": "WA", "country_id": usa.country_id}
        ]
        
        for state_data in states:
            state = State(**state_data)
            db.add(state)
        
        db.commit()
        logger.info(f"Created {len(states)} states")
        
        # Add some cities
        california = db.query(State).filter(State.state_code == "CA").first()
        if california:
            cities = [
                {"city_name": "San Francisco", "state_id": california.state_id, "country_id": usa.country_id},
                {"city_name": "Los Angeles", "state_id": california.state_id, "country_id": usa.country_id},
                {"city_name": "San Diego", "state_id": california.state_id, "country_id": usa.country_id}
            ]
            
            for city_data in cities:
                city = City(**city_data)
                db.add(city)
            
            db.commit()
            logger.info(f"Created {len(cities)} cities")


def create_admin_user(db: Session) -> None:
    """
    Create an admin user for development purposes.
    """
    # Check if admin user already exists
    admin_email = "admin@example.com"
    existing = db.query(User).filter(User.email == admin_email).first()
    if existing:
        logger.info("Admin user already exists, skipping creation")
        return
    
    # Create admin user
    admin_user = User(
        user_id=uuid.uuid4(),
        email=admin_email,
        password_hash=get_password_hash("adminpassword"),  # DO NOT USE IN PRODUCTION
        first_name="Admin",
        last_name="User",
        is_active=True,
        email_verified=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    # Create user settings
    admin_settings = UserSettings(
        setting_id=uuid.uuid4(),
        user_id=admin_user.user_id,
        notification_preferences={
            "email": True,
            "in_app": True
        },
        ui_preferences={
            "theme": "light",
            "language": "en"
        },
        time_zone="America/New_York",
        language_preference="en"
    )
    db.add(admin_settings)
    db.commit()
    
    logger.info("Created admin user with settings")