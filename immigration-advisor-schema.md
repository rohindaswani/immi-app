# Flexible Immigration Advisor System
## Database Schema & API Design

This document outlines the database schema and API design for a flexible immigration advisor system that supports multiple visa types and immigration pathways.

## Table of Contents
- [Database Schema](#database-schema)
  - [PostgreSQL Tables](#postgresql-tables)
  - [MongoDB Collections](#mongodb-collections)
  - [Vector Storage](#vector-storage)
- [API Design](#api-design)
  - [Authentication Endpoints](#authentication-endpoints)
  - [User Management Endpoints](#user-management-endpoints)
  - [Profile Management Endpoints](#profile-management-endpoints)
  - [Immigration Status Endpoints](#immigration-status-endpoints)
  - [Application Management Endpoints](#application-management-endpoints)
  - [Sponsor Management Endpoints](#sponsor-management-endpoints)
  - [Document Management Endpoints](#document-management-endpoints)
  - [Travel History Endpoints](#travel-history-endpoints)
  - [Address & Contact Endpoints](#address--contact-endpoints)
  - [Family Member Endpoints](#family-member-endpoints)
  - [Timeline & Events Endpoints](#timeline--events-endpoints)
  - [Notification Endpoints](#notification-endpoints)
  - [Analysis & Reporting Endpoints](#analysis--reporting-endpoints)
  - [Knowledge Base Endpoints](#knowledge-base-endpoints)
  - [AI Assistant Endpoints](#ai-assistant-endpoints)
  - [Lookup Data Endpoints](#lookup-data-endpoints)
  - [Admin Endpoints](#admin-endpoints)

## Database Schema

### PostgreSQL Tables

#### 1. Users Table
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 2. User Settings Table
```sql
CREATE TABLE user_settings (
    setting_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    notification_preferences JSONB,
    ui_preferences JSONB,
    time_zone VARCHAR(100),
    language_preference VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 3. Immigration Profiles Table
```sql
CREATE TABLE immigration_profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    current_status_id UUID REFERENCES immigration_statuses(status_id),
    most_recent_i94_number VARCHAR(255),
    most_recent_entry_date DATE,
    immigration_goals TEXT,
    alien_registration_number VARCHAR(255),
    current_priority_dates JSONB, -- Store multiple priority dates by category
    authorized_stay_until DATE,
    ead_expiry_date DATE, -- Employment Authorization Document
    visa_expiry_date DATE,
    passport_number VARCHAR(100),
    passport_country_id UUID REFERENCES countries(country_id),
    passport_expiry_date DATE,
    is_primary_beneficiary BOOLEAN DEFAULT TRUE,
    primary_beneficiary_id UUID REFERENCES immigration_profiles(profile_id), -- For dependents
    profile_type VARCHAR(50), -- primary, dependent
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 4. Immigration Statuses Table
```sql
CREATE TABLE immigration_statuses (
    status_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status_code VARCHAR(50), -- H1-B, L-1, F-1, OPT, J-1, EAD, etc.
    status_name VARCHAR(255),
    status_category VARCHAR(100), -- Employment, Student, Exchange, Family, etc.
    allows_employment BOOLEAN,
    employment_restrictions TEXT,
    max_duration VARCHAR(100), -- "6 years", "Duration of study + 60 days", etc.
    grace_period VARCHAR(100), -- "60 days", "10 days", etc.
    is_dual_intent BOOLEAN,
    can_apply_for_adjustment_of_status BOOLEAN,
    requires_sponsor BOOLEAN,
    potential_next_statuses JSONB, -- Array of possible next status codes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 5. Sponsors Table
```sql
CREATE TABLE sponsors (
    sponsor_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sponsor_name VARCHAR(255),
    sponsor_type VARCHAR(100), -- Employer, educational institution, family member, self
    identification_number VARCHAR(255), -- EIN for employers, etc.
    address_id UUID REFERENCES addresses(address_id),
    contact_person VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(100),
    sponsor_status VARCHAR(100), -- active, inactive, etc.
    sponsorship_capacity JSONB, -- What types of sponsorship this entity can provide
    additional_data JSONB, -- Type-specific details
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 6. Application Types Table
```sql
CREATE TABLE application_types (
    type_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type_code VARCHAR(100), -- I-129, I-485, I-765, etc.
    type_name VARCHAR(255), -- "H-1B Petition", "Adjustment of Status", etc.
    uscis_form_number VARCHAR(100),
    category VARCHAR(100), -- Employment, Family, Humanitarian, etc.
    prerequisites JSONB, -- What statuses/conditions qualify for this application
    processing_time_range VARCHAR(100), -- "2-4 months", etc.
    premium_processing_eligible BOOLEAN,
    filing_fee DECIMAL(10,2),
    premium_processing_fee DECIMAL(10,2),
    current_version VARCHAR(50), -- Current form version
    form_expiration_date DATE,
    supporting_documents_required JSONB, -- Array of required document types
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 7. Immigration Applications Table
```sql
CREATE TABLE immigration_applications (
    application_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    application_type_id UUID REFERENCES application_types(type_id),
    application_number VARCHAR(255),
    receipt_number VARCHAR(255),
    case_status VARCHAR(100),
    filing_date DATE,
    notice_date DATE,
    approval_date DATE,
    denial_date DATE,
    validity_start_date DATE,
    validity_end_date DATE,
    sponsor_id UUID REFERENCES sponsors(sponsor_id), -- Could be employer, family member, etc.
    sponsorship_type VARCHAR(100), -- Employment, family, self, etc.
    processing_type VARCHAR(100), -- Regular, premium, etc.
    category VARCHAR(100), -- EB-1, EB-2, EB-3, Family-1, etc.
    current_stage VARCHAR(100), -- Initial filing, RFE, approved, etc.
    priority_date DATE,
    attorney_id UUID REFERENCES attorneys(attorney_id),
    rfe_received_date DATE,
    rfe_due_date DATE,
    rfe_response_date DATE,
    additional_data JSONB, -- Flexible storage for type-specific fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 8. Attorneys Table
```sql
CREATE TABLE attorneys (
    attorney_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    attorney_name VARCHAR(255),
    firm_name VARCHAR(255),
    address_id UUID REFERENCES addresses(address_id),
    email VARCHAR(255),
    phone VARCHAR(100),
    bar_number VARCHAR(100),
    g28_on_file BOOLEAN,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 9. Status Transitions Table
```sql
CREATE TABLE status_transitions (
    transition_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    previous_status_id UUID REFERENCES immigration_statuses(status_id),
    new_status_id UUID REFERENCES immigration_statuses(status_id),
    transition_date DATE,
    transition_reason VARCHAR(255),
    authorizing_application_id UUID REFERENCES immigration_applications(application_id),
    maintenance_of_status_status VARCHAR(100), -- maintained, gap, violation, etc.
    gap_details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 10. Education History Table
```sql
CREATE TABLE education_history (
    education_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    institution_name VARCHAR(255),
    degree_id UUID REFERENCES degrees(degree_id),
    field_of_study VARCHAR(255),
    start_date DATE,
    end_date DATE,
    country_id UUID REFERENCES countries(country_id),
    is_verified BOOLEAN DEFAULT FALSE,
    verification_document_id UUID, -- Reference to documents in MongoDB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 11. Employment History Table
```sql
CREATE TABLE employment_history (
    employment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    sponsor_id UUID REFERENCES sponsors(sponsor_id),
    job_title VARCHAR(255),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    job_description TEXT,
    work_location_address_id UUID REFERENCES addresses(address_id),
    supervisor_name VARCHAR(255),
    supervisor_contact VARCHAR(255),
    wage_information JSONB, -- Salary, hourly rate, etc.
    employment_type VARCHAR(100), -- Full-time, part-time, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 12. Addresses Table
```sql
CREATE TABLE addresses (
    address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    street_address_1 VARCHAR(255),
    street_address_2 VARCHAR(255),
    city_id UUID REFERENCES cities(city_id),
    state_id UUID REFERENCES states(state_id),
    zip_code VARCHAR(20),
    country_id UUID REFERENCES countries(country_id),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    address_type VARCHAR(100), -- Home, work, mailing, etc.
    is_verified BOOLEAN DEFAULT FALSE,
    verification_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 13. Address History Table
```sql
CREATE TABLE address_history (
    address_history_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    address_id UUID REFERENCES addresses(address_id),
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT FALSE,
    address_type VARCHAR(100), -- residential, mailing, work
    verification_document_id UUID, -- Reference to documents in MongoDB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 14. Countries Table
```sql
CREATE TABLE countries (
    country_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_name VARCHAR(255),
    country_code VARCHAR(3),
    is_visa_required_for_us_travel BOOLEAN,
    region VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 15. States Table
```sql
CREATE TABLE states (
    state_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    state_name VARCHAR(255),
    state_code VARCHAR(10),
    country_id UUID REFERENCES countries(country_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 16. Cities Table
```sql
CREATE TABLE cities (
    city_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    city_name VARCHAR(255),
    state_id UUID REFERENCES states(state_id),
    country_id UUID REFERENCES countries(country_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 17. Travel History Table
```sql
CREATE TABLE travel_history (
    travel_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    departure_date DATE,
    departure_country_id UUID REFERENCES countries(country_id),
    departure_city_id UUID REFERENCES cities(city_id),
    departure_port VARCHAR(255),
    arrival_date DATE,
    arrival_country_id UUID REFERENCES countries(country_id),
    arrival_city_id UUID REFERENCES cities(city_id),
    arrival_port VARCHAR(255),
    visa_type_id UUID REFERENCES immigration_statuses(status_id),
    i94_number VARCHAR(255),
    mode_of_transportation VARCHAR(100), -- Air, land, sea
    purpose VARCHAR(255),
    carrier_info VARCHAR(255), -- Airline, flight number, etc.
    is_verified BOOLEAN DEFAULT FALSE,
    verification_document_id UUID, -- Reference to documents in MongoDB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 18. Family Members Table
```sql
CREATE TABLE family_members (
    family_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    related_profile_id UUID REFERENCES immigration_profiles(profile_id), -- If they have their own profile
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    relationship VARCHAR(100), -- Spouse, child, parent, etc.
    date_of_birth DATE,
    country_of_birth_id UUID REFERENCES countries(country_id),
    current_status_id UUID REFERENCES immigration_statuses(status_id),
    i94_number VARCHAR(255),
    passport_number VARCHAR(100),
    passport_country_id UUID REFERENCES countries(country_id),
    passport_expiry_date DATE,
    alien_registration_number VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 19. Notifications Table
```sql
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    type VARCHAR(100), -- check-in, deadline, alert, etc.
    title VARCHAR(255),
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    priority VARCHAR(50), -- high, medium, low
    related_entity_type VARCHAR(100), -- profile, application, document, etc.
    related_entity_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scheduled_for TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);
```

#### 20. Immigration Timeline Table
```sql
CREATE TABLE immigration_timeline (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    event_type VARCHAR(100), -- visa_approval, entry, exit, status_change, etc.
    event_date DATE,
    event_title VARCHAR(255),
    description TEXT,
    reference_id UUID, -- ID of the related record
    reference_table VARCHAR(100), -- Name of the related table
    supporting_document_id UUID, -- Reference to documents in MongoDB
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 21. Immigration Pathways Table
```sql
CREATE TABLE immigration_pathways (
    pathway_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    pathway_name VARCHAR(255),
    initial_status_id UUID REFERENCES immigration_statuses(status_id),
    target_status_id UUID REFERENCES immigration_statuses(status_id),
    estimated_timeline VARCHAR(255),
    pathway_steps JSONB, -- Array of steps with status transitions and applications
    requirements TEXT,
    common_challenges TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 22. Immigration Rules Table
```sql
CREATE TABLE immigration_rules (
    rule_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(255),
    applies_to_status_ids UUID[], -- Array of status_ids this rule applies to
    applies_to_application_types UUID[], -- Array of application_type_ids
    rule_description TEXT,
    rule_check_type VARCHAR(100), -- time-based, document-based, travel-based, etc.
    rule_parameters JSONB, -- Dynamic parameters for this rule
    rule_severity VARCHAR(50), -- critical, warning, informational
    rule_logic TEXT, -- Pseudocode or reference to rule implementation
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 23. Compliance Checks Table
```sql
CREATE TABLE compliance_checks (
    check_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id UUID REFERENCES immigration_profiles(profile_id),
    rule_id UUID REFERENCES immigration_rules(rule_id),
    check_date TIMESTAMP WITH TIME ZONE,
    status VARCHAR(100), -- passed, warning, failed
    details TEXT,
    remediation_steps TEXT,
    verified BOOLEAN DEFAULT FALSE,
    verified_by UUID,
    verified_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID
);
```

#### 24. Degrees Table
```sql
CREATE TABLE degrees (
    degree_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    degree_name VARCHAR(255),
    degree_level VARCHAR(100), -- associate, bachelor, master, doctorate
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### 25. Audit Log Table
```sql
CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(100),
    record_id UUID,
    action VARCHAR(50), -- insert, update, delete
    user_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    old_values JSONB,
    new_values JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT
);
```

### MongoDB Collections

#### 1. Documents Collection
```json
{
  "_id": "ObjectId",
  "user_id": "UUID",
  "document_type": "String", // passport, visa, I-797, I-94, etc.
  "document_subtype": "String", // optional subcategory
  "document_number": "String",
  "issuing_authority": "String",
  "related_immigration_type": "String", // H1-B, L-1, OPT, etc.
  "issue_date": "Date",
  "expiry_date": "Date",
  "related_documents": ["ObjectId"], // array of related document IDs
  "related_applications": ["UUID"], // References to immigration_applications
  "file_name": "String",
  "file_path": "String",
  "file_size": "Number",
  "file_type": "String", // MIME type
  "version": "Number",
  "is_verified": "Boolean",
  "verified_by": "String",
  "verified_date": "Date",
  "related_entity_type": "String", // profile, application, travel, etc.
  "related_entity_id": "UUID",
  "metadata": {
    "form_type": "String",
    "form_version": "String",
    "page_count": "Number",
    "ocr_processed": "Boolean",
    "extracted_text": "String",
    "extracted_data": {
      "form_specific_fields": "Object" // Dynamic based on document type
    }
  },
  "tags": ["String"],
  "upload_date": "Date",
  "uploaded_by": "UUID",
  "last_accessed": "Date",
  "last_accessed_by": "UUID"
}
```

#### 2. Conversations Collection
```json
{
  "_id": "ObjectId",
  "user_id": "UUID",
  "messages": [
    {
      "message_id": "UUID",
      "sender_type": "String", // user or system
      "content": "String",
      "timestamp": "Date",
      "read": "Boolean",
      "context": {
        "related_entity_type": "String",
        "related_entity_id": "UUID"
      },
      "actions_taken": [
        {
          "action_type": "String",
          "action_details": "Object",
          "timestamp": "Date"
        }
      ]
    }
  ],
  "created_at": "Date",
  "updated_at": "Date",
  "status": "String", // active, archived
  "topic": "String",
  "summary": "String",
  "tags": ["String"]
}
```

#### 3. Knowledge Base Collection
```json
{
  "_id": "ObjectId",
  "title": "String",
  "content": "String",
  "category": "String",
  "subcategory": "String",
  "applies_to_statuses": ["String"], // H1-B, L-1, etc.
  "tags": ["String"],
  "last_updated": "Date",
  "source_url": "String",
  "source_authority": "String",
  "is_verified": "Boolean",
  "verification_date": "Date",
  "related_articles": ["ObjectId"]
}
```

### Vector Storage (Pinecone)

The vector database will store embeddings for:
1. Documents and their extracted text
2. Knowledge base articles
3. Conversation history
4. User queries for semantic search

Each vector will include:
- Vector ID (matching the source document/article ID)
- Vector embedding (768 or 1536 dimensions depending on the model)
- Metadata including:
  - Source type (document, article, conversation)
  - Source ID
  - User ID
  - Timestamp
  - Relevant tags or categories

## API Design

### Authentication Endpoints
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
- POST /api/v1/auth/reset-password
- POST /api/v1/auth/verify-email
- GET /api/v1/auth/status

### User Management Endpoints
- GET /api/v1/users/me
- PUT /api/v1/users/me
- DELETE /api/v1/users/me
- GET /api/v1/users/me/settings
- PUT /api/v1/users/me/settings
- GET /api/v1/users/me/activity-log

### Profile Management Endpoints
- GET /api/v1/profiles
- POST /api/v1/profiles
- GET /api/v1/profiles/{profile_id}
- PUT /api/v1/profiles/{profile_id}
- DELETE /api/v1/profiles/{profile_id}
- GET /api/v1/profiles/{profile_id}/summary
- POST /api/v1/profiles/{profile_id}/clone
- GET /api/v1/profiles/{profile_id}/dependents

### Immigration Status Endpoints
- GET /api/v1/statuses
- GET /api/v1/statuses/{status_id}
- GET /api/v1/profiles/{profile_id}/status-history
- POST /api/v1/profiles/{profile_id}/status-transitions
- GET /api/v1/profiles/{profile_id}/status-transitions/{transition_id}
- PUT /api/v1/profiles/{profile_id}/status-transitions/{transition_id}

### Application Management Endpoints
- GET /api/v1/application-types
- GET /api/v1/application-types/{type_id}
- GET /api/v1/profiles/{profile_id}/applications
- POST /api/v1/profiles/{profile_id}/applications
- GET /api/v1/profiles/{profile_id}/applications/{application_id}
- PUT /api/v1/profiles/{profile_id}/applications/{application_id}
- DELETE /api/v1/profiles/{profile_id}/applications/{application_id}
- POST /api/v1/profiles/{profile_id}/applications/{application_id}/check-status
- POST /api/v1/profiles/{profile_id}/applications/{application_id}/rfe
- GET /api/v1/profiles/{profile_id}/applications/upcoming-expirations

### Sponsor Management Endpoints
- GET /api/v1/sponsors
- POST /api/v1/sponsors
- GET /api/v1/sponsors/{sponsor_id}
- PUT /api/v1/sponsors/{sponsor_id}
- DELETE /api/v1/sponsors/{sponsor_id}
- GET /api/v1/profiles/{profile_id}/sponsors
- POST /api/v1/profiles/{profile_id}/sponsorships

### Document Management Endpoints
- GET /api/v1/documents
- POST /api/v1/documents
- GET /api/v1/documents/{document_id}
- PUT /api/v1/documents/{document_id}
- DELETE /api/v1/documents/{document_id}
- GET /api/v1/documents/search
- POST /api/v1/documents/{document_id}/verify
- GET /api/v1/documents/{document_id}/related
- POST /api/v1/documents/{document_id}/extract-data
- GET /api/v1/profiles/{profile_id}/documents
- GET /api/v1/applications/{application_id}/documents

### Travel History Endpoints
- GET /api/v1/profiles/{profile_id}/travel
- POST /api/v1/profiles/{profile_id}/travel
- GET /api/v1/profiles/{profile_id}/travel/{travel_id}
- PUT /api/v1/profiles/{profile_id}/travel/{travel_id}
- DELETE /api/v1/profiles/{profile_id}/travel/{travel_id}
- GET /api/v1/profiles/{profile_id}/travel/analysis
- POST /api/v1/profiles/{profile_id}/travel/validate

### Address & Contact Endpoints
- GET /api/v1/addresses
- POST /api/v1/addresses
- GET /api/v1/addresses/{address_id}
- PUT /api/v1/addresses/{address_id}
- DELETE /api/v1/addresses/{address_id}
- GET /api/v1/profiles/{profile_id}/address-history
- POST /api/v1/profiles/{profile_id}/address-history
- GET /api/v1/profiles/{profile_id}/address-history/{history_id}
- PUT /api/v1/profiles/{profile_id}/address-history/{history_id}
- DELETE /api/v1/profiles/{profile_id}/address-history/{history_id}

### Family Member Endpoints
- GET /api/v1/profiles/{profile_id}/family
- POST /api/v1/profiles/{profile_id}/family
- GET /api/v1/profiles/{profile_id}/family/{family_id}
- PUT /api/v1/profiles/{profile_id}/family/{family_id}
- DELETE /api/v1/profiles/{profile_id}/family/{family_id}
- POST /api/v1/profiles/{profile_id}/family/{family_id}/create-profile

### Timeline & Events Endpoints
- GET /api/v1/profiles/{profile_id}/timeline
- POST /api/v1/profiles/{profile_id}/timeline
- GET /api/v1/profiles/{profile_id}/timeline/{event_id}
- PUT /api/v1/profiles/{profile_id}/timeline/{event_id}
- DELETE /api/v1/profiles/{profile_id}/timeline/{event_id}
- GET /api/v1/profiles/{profile_id}/timeline/filter

### Notification Endpoints
- GET /api/v1/notifications
- PUT /api/v1/notifications/{notification_id}/read
- DELETE /api/v1/notifications/{notification_id}
- GET /api/v1/notifications/settings
- PUT /api/v1/notifications/settings
- POST /api/v1/notifications/test
- GET /api/v1/profiles/{profile_id}/check-in/schedule
- POST /api/v1/profiles/{profile_id}/check-in

### Analysis & Reporting Endpoints
- GET /api/v1/profiles/{profile_id}/analysis/status-summary
- GET /api/v1/profiles/{profile_id}/analysis/upcoming-deadlines
- GET /api/v1/profiles/{profile_id}/analysis/compliance-risks
- GET /api/v1/profiles/{profile_id}/analysis/pathway-progress
- GET /api/v1/profiles/{profile_id}/analysis/eligibility-check
- GET /api/v1/profiles/{profile_id}/reports/travel-history
- GET /api/v1/profiles/{profile_id}/reports/status-maintenance
- GET /api/v1/profiles/{profile_id}/reports/residence-history
- POST /api/v1/profiles/{profile_id}/reports/export

### Knowledge Base Endpoints
- GET /api/v1/knowledge
- GET /api/v1/knowledge/{article_id}
- GET /api/v1/knowledge/search
- GET /api/v1/knowledge/categories
- GET /api/v1/knowledge/related-to/{entity_type}/{entity_id}

### AI Assistant Endpoints
- POST /api/v1/chat/message
- GET /api/v1/chat/history
- GET /api/v1/chat/history/{conversation_id}
- DELETE /api/v1/chat/history/{conversation_id}
- POST /api/v1/chat/feedback
- GET /api/v1/chat/suggested-topics
- POST /api/v1/chat/analyze

### Lookup Data Endpoints
- GET /api/v1/lookup/countries
- GET /api/v1/lookup/states
- GET /api/v1/lookup/cities
- GET /api/v1/lookup/visa-types
- GET /api/v1/lookup/document-types
- GET /api/v1/lookup/degrees
- GET /api/v1/lookup/application-types

### Admin Endpoints
- GET /api/v1/admin/users
- GET /api/v1/admin/users/{user_id}
- PUT /api/v1/admin/users/{user_id}/status
- GET /api/v1/admin/audit-log
- GET /api/v1/admin/system-health
- GET /api/v1/admin/knowledge/manage
- POST /api/v1/admin/knowledge
- PUT /api/v1/admin/knowledge/{article_id}
- DELETE /api/v1/admin/knowledge/{article_id}

## Implementation Considerations

### 1. Security Implementation

Given the sensitive nature of immigration data, the following security measures are essential:

#### Data Protection
- **Encryption**: Implement both at-rest and in-transit encryption
- **Data Masking**: Mask sensitive fields like Alien Registration Numbers in logs
- **Access Controls**: Role-based access control for all endpoints
- **Audit Trails**: Comprehensive logging of all data access and modifications

#### Authentication & Authorization
- **Multi-factor Authentication**: For all user accounts
- **JWT Token Management**: Short expiration times with refresh token rotation
- **Fine-grained Permissions**: Different access levels for different data types

#### Compliance
- **GDPR/CCPA Compliance**: Implementation of data subject rights (right to access, delete, etc.)
- **Data Retention Policies**: Automated enforcement of retention periods
- **Privacy by Design**: Minimizing data collection to necessary fields only

### 2. AI Integration Architecture

The system leverages LangChain for Model Context Protocol (MCP) implementation with the following components:

#### Vector Database Integration
- **Document Indexing Pipeline**: Automatically extract and index document text
- **Semantic Search**: Implementation of hybrid search (keyword + semantic)
- **Relevance Feedback**: Mechanism to improve search results based on user feedback

#### LLM Integration
- **Context Assembly**: Dynamically assemble relevant context for each query
- **Response Generation**: Generate natural language responses to immigration queries
- **Fact Checking**: Verify generated responses against knowledge base

#### Personalization
- **User Profile Adaptation**: Tailor responses based on user's immigration status and goals
- **Learning Loop**: Improve responses based on user feedback and interactions

### 3. Notification System Design

Implement a robust notification system with the following features:

#### Proactive Monitoring
- **Rule-based Triggers**: Automatic notifications based on rules engine
- **Calendar Integration**: Sync with user's calendar for important dates
- **Document Expiration Tracking**: Monitor visa, passport, and I-94 expiration dates

#### Communication Channels
- **In-app Notifications**: Real-time alerts within the application
- **Email Notifications**: Configurable email digest of important events
- **SMS Alerts**: Optional text messages for critical deadlines

#### Periodic Check-ins
- **Monthly Health Checks**: Automated check-ins for life changes
- **Travel Plans Monitoring**: Regular prompts about upcoming travel
- **Address Verification**: Periodic verification of current residence

### 4. Scalability Considerations

Design the system for growth with:

#### Database Scalability
- **Read Replicas**: For PostgreSQL to handle increased read traffic
- **Sharding Strategy**: For MongoDB collections as document volume grows
- **Connection Pooling**: Efficient database connection management

#### API Performance
- **Caching Layer**: Redis implementation for frequently accessed data
- **Rate Limiting**: To prevent abuse and ensure fair resource allocation
- **Pagination**: Consistent implementation across all list endpoints

#### Infrastructure
- **Containerization**: Docker-based deployment for consistency
- **Kubernetes Orchestration**: For managing container scaling
- **CDN Integration**: For static assets and document previews

### 5. Data Migration Strategy

For users transitioning from other systems:

#### Import Utilities
- **Standardized Import Format**: CSV/JSON templates for data import
- **Document Processing**: OCR and extraction for scanned documents
- **Validation Pipeline**: Ensure data quality during migration

#### Incremental Migration
- **Phased Approach**: Migrate core data first, then supporting information
- **Continuous Validation**: Verify data integrity throughout the process
- **Rollback Capability**: Ability to revert migrations if issues arise

### 6. Onboarding Experience

Design an intuitive onboarding flow:

#### Progressive Data Collection
- **Step-by-step Wizard**: Break down comprehensive data collection
- **Save Progress**: Allow users to save and continue later
- **Import Options**: Connect to existing systems or upload documents

#### Initial Assessment
- **Status Analyzer**: Determine current immigration status
- **Goal Setting**: Establish immigration objectives
- **Document Checklist**: Generate personalized document requirements

#### Personalization
- **Pathway Recommendation**: Suggest optimal immigration pathways
- **Custom Dashboard**: Configure based on immigration status and goals
- **Priority Alerts**: Set up critical notifications based on status

### 7. Technical Implementation Stack

Detailed technology stack for implementation:

#### Backend
- **Framework**: Python with FastAPI
- **ORM/ODM**: SQLAlchemy for PostgreSQL, PyMongo for MongoDB
- **Authentication**: JWT with OAuth2
- **Validation**: Pydantic for request/response validation
- **Background Tasks**: Celery with Redis for asynchronous processing
- **AI Integration**: LangChain with OpenAI API

#### Frontend
- **Framework**: React with TypeScript
- **State Management**: Redux Toolkit
- **UI Components**: Chakra UI or Material UI
- **Form Handling**: React Hook Form with Zod validation
- **Data Visualization**: Recharts for timeline and analytics
- **Document Viewer**: PDF.js for document preview

#### DevOps
- **CI/CD**: GitHub Actions
- **Infrastructure as Code**: Terraform
- **Monitoring**: Prometheus with Grafana dashboards
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)
- **Error Tracking**: Sentry

#### Storage
- **Document Storage**: AWS S3 with lifecycle policies
- **Database Hosting**: AWS RDS for PostgreSQL, MongoDB Atlas
- **Vector Database**: Pinecone or Weaviate
- **Cache**: Redis

This comprehensive architecture provides a solid foundation for building a flexible immigration advisor system that can adapt to various immigration pathways while maintaining robust security, compliance, and user experience.
