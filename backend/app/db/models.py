from sqlalchemy import (
    Boolean, Column, DateTime, String, Text, 
    Integer, ForeignKey, Date, JSON, Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.db.postgres import Base

class User(Base):
    """
    User account model
    """
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    profiles = relationship("ImmigrationProfile", back_populates="user")
    notifications = relationship("Notification", back_populates="user")


class UserSettings(Base):
    """
    User settings model
    """
    __tablename__ = "user_settings"

    setting_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    notification_preferences = Column(JSON, default={})
    ui_preferences = Column(JSON, default={})
    time_zone = Column(String(100))
    language_preference = Column(String(50), default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="settings")


class ImmigrationStatus(Base):
    """
    Immigration status types model
    """
    __tablename__ = "immigration_statuses"

    status_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status_code = Column(String(50), unique=True, index=True, nullable=False)  # H1-B, L-1, F-1, etc.
    status_name = Column(String(255), nullable=False)
    status_category = Column(String(100))  # Employment, Student, Exchange, Family, etc.
    allows_employment = Column(Boolean, default=False)
    employment_restrictions = Column(Text)
    max_duration = Column(String(100))  # "6 years", "Duration of study + 60 days", etc.
    grace_period = Column(String(100))  # "60 days", "10 days", etc.
    is_dual_intent = Column(Boolean, default=False)
    can_apply_for_adjustment_of_status = Column(Boolean, default=False)
    requires_sponsor = Column(Boolean, default=False)
    potential_next_statuses = Column(JSON)  # Array of possible next status codes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    profiles = relationship("ImmigrationProfile", back_populates="current_status")


class ImmigrationProfile(Base):
    """
    Immigration profile model
    """
    __tablename__ = "immigration_profiles"

    profile_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    current_status_id = Column(UUID(as_uuid=True), ForeignKey("immigration_statuses.status_id"))
    most_recent_i94_number = Column(String(255))
    most_recent_entry_date = Column(Date)
    immigration_goals = Column(Text)
    alien_registration_number = Column(String(255))
    current_priority_dates = Column(JSON)  # Store multiple priority dates by category
    authorized_stay_until = Column(Date)
    ead_expiry_date = Column(Date)  # Employment Authorization Document
    visa_expiry_date = Column(Date)
    passport_number = Column(String(100))
    passport_country_id = Column(UUID(as_uuid=True), ForeignKey("countries.country_id"))
    passport_expiry_date = Column(Date)
    is_primary_beneficiary = Column(Boolean, default=True)
    primary_beneficiary_id = Column(UUID(as_uuid=True), ForeignKey("immigration_profiles.profile_id"), nullable=True)
    profile_type = Column(String(50), default="primary")  # primary, dependent
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    user = relationship("User", back_populates="profiles")
    current_status = relationship("ImmigrationStatus", back_populates="profiles")
    passport_country = relationship("Country", foreign_keys=[passport_country_id])
    dependents = relationship("ImmigrationProfile", 
                             foreign_keys=[primary_beneficiary_id],
                             remote_side=[profile_id])
    documents = relationship("DocumentMetadata", back_populates="profile")
    travel_history = relationship("TravelHistory", back_populates="profile")
    address_history = relationship("AddressHistory", back_populates="profile")
    timeline_events = relationship("ImmigrationTimeline", back_populates="profile")


class Country(Base):
    """
    Countries model
    """
    __tablename__ = "countries"

    country_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country_name = Column(String(255), nullable=False)
    country_code = Column(String(3), nullable=False, unique=True, index=True)
    is_visa_required_for_us_travel = Column(Boolean, default=True)
    region = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    states = relationship("State", back_populates="country")


class State(Base):
    """
    States/Provinces model
    """
    __tablename__ = "states"

    state_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_name = Column(String(255), nullable=False)
    state_code = Column(String(10), nullable=False)
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.country_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    country = relationship("Country", back_populates="states")
    cities = relationship("City", back_populates="state")


class City(Base):
    """
    Cities model
    """
    __tablename__ = "cities"

    city_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    city_name = Column(String(255), nullable=False)
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.state_id"))
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.country_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    state = relationship("State", back_populates="cities")
    country = relationship("Country")


class Address(Base):
    """
    Addresses model
    """
    __tablename__ = "addresses"

    address_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    street_address_1 = Column(String(255), nullable=False)
    street_address_2 = Column(String(255))
    city_id = Column(UUID(as_uuid=True), ForeignKey("cities.city_id"))
    state_id = Column(UUID(as_uuid=True), ForeignKey("states.state_id"))
    zip_code = Column(String(20))
    country_id = Column(UUID(as_uuid=True), ForeignKey("countries.country_id"), nullable=False)
    latitude = Column(Float(precision=9))
    longitude = Column(Float(precision=9))
    address_type = Column(String(100))  # Home, work, mailing, etc.
    is_verified = Column(Boolean, default=False)
    verification_date = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    city = relationship("City")
    state = relationship("State")
    country = relationship("Country")
    address_history = relationship("AddressHistory", back_populates="address")


class AddressHistory(Base):
    """
    Address history model
    """
    __tablename__ = "address_history"

    address_history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("immigration_profiles.profile_id", ondelete="CASCADE"), nullable=False)
    address_id = Column(UUID(as_uuid=True), ForeignKey("addresses.address_id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_current = Column(Boolean, default=False)
    address_type = Column(String(100))  # residential, mailing, work
    verification_document_id = Column(UUID(as_uuid=True))  # Reference to MongoDB document
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    profile = relationship("ImmigrationProfile", back_populates="address_history")
    address = relationship("Address", back_populates="address_history")


class TravelHistory(Base):
    """
    Travel history model
    """
    __tablename__ = "travel_history"

    travel_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("immigration_profiles.profile_id", ondelete="CASCADE"), nullable=False)
    departure_date = Column(Date, nullable=False)
    departure_country_id = Column(UUID(as_uuid=True), ForeignKey("countries.country_id"), nullable=False)
    departure_city_id = Column(UUID(as_uuid=True), ForeignKey("cities.city_id"))
    departure_port = Column(String(255))
    arrival_date = Column(Date, nullable=False)
    arrival_country_id = Column(UUID(as_uuid=True), ForeignKey("countries.country_id"), nullable=False)
    arrival_city_id = Column(UUID(as_uuid=True), ForeignKey("cities.city_id"))
    arrival_port = Column(String(255))
    visa_type_id = Column(UUID(as_uuid=True), ForeignKey("immigration_statuses.status_id"))
    i94_number = Column(String(255))
    mode_of_transportation = Column(String(100))  # Air, land, sea
    purpose = Column(String(255))
    carrier_info = Column(String(255))  # Airline, flight number, etc.
    is_verified = Column(Boolean, default=False)
    verification_document_id = Column(UUID(as_uuid=True))  # Reference to MongoDB document
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    profile = relationship("ImmigrationProfile", back_populates="travel_history")
    departure_country = relationship("Country", foreign_keys=[departure_country_id])
    departure_city = relationship("City", foreign_keys=[departure_city_id])
    arrival_country = relationship("Country", foreign_keys=[arrival_country_id])
    arrival_city = relationship("City", foreign_keys=[arrival_city_id])
    visa_type = relationship("ImmigrationStatus")


class DocumentMetadata(Base):
    """
    Document metadata model (actual document stored in MongoDB)
    """
    __tablename__ = "document_metadata"

    document_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("immigration_profiles.profile_id", ondelete="CASCADE"), nullable=False)
    document_type = Column(String(100), nullable=False)  # passport, visa, I-797, I-94, etc.
    document_subtype = Column(String(100))
    document_number = Column(String(255))
    issuing_authority = Column(String(255))
    related_immigration_type = Column(String(100))  # H1-B, L-1, OPT, etc.
    issue_date = Column(Date)
    expiry_date = Column(Date)
    mongodb_id = Column(String(255), nullable=False)  # ID of the document in MongoDB
    s3_key = Column(String(1024))  # S3 storage key
    file_name = Column(String(255))
    file_size = Column(Integer)
    file_type = Column(String(100))  # MIME type
    is_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True))
    verified_date = Column(DateTime(timezone=True))
    tags = Column(JSON)  # Array of tags
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    profile = relationship("ImmigrationProfile", back_populates="documents")


class ImmigrationTimeline(Base):
    """
    Immigration timeline model
    """
    __tablename__ = "immigration_timeline"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("immigration_profiles.profile_id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(100), nullable=False)  # visa_approval, entry, exit, status_change, etc.
    event_date = Column(Date, nullable=False)
    event_title = Column(String(255), nullable=False)
    description = Column(Text)
    reference_id = Column(UUID(as_uuid=True))  # ID of the related record
    reference_table = Column(String(100))  # Name of the related table
    supporting_document_id = Column(UUID(as_uuid=True))  # Reference to documents in MongoDB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True))
    updated_by = Column(UUID(as_uuid=True))

    # Relationships
    profile = relationship("ImmigrationProfile", back_populates="timeline_events")


class Notification(Base):
    """
    Notifications model
    """
    __tablename__ = "notifications"

    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=False)  # check-in, deadline, alert, etc.
    title = Column(String(255), nullable=False)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    priority = Column(String(50), default="medium")  # high, medium, low
    related_entity_type = Column(String(100))  # profile, application, document, etc.
    related_entity_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_for = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="notifications")