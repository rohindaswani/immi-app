"""
Test script for creating address history.
"""
import sys
import os
import requests
import json
import uuid
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import our app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def test_create_address_history():
    """
    Test creating address history with different payload formats.
    """
    base_url = "http://localhost:8000/api/v1"
    
    # First, create an address to use in the history record
    address_payload = {
        "street_address_1": "123 Test Street",
        "street_address_2": "Apt 4B",
        "city_id": "a23e4567-e89b-12d3-a456-426614174000",  # San Francisco
        "state_id": "423e4567-e89b-12d3-a456-426614174000",  # California
        "zip_code": "94109",
        "country_id": "123e4567-e89b-12d3-a456-426614174000",  # USA
        "address_type": "residential"
    }
    
    print("Creating test address...")
    address_response = requests.post(f"{base_url}/history/addresses", json=address_payload)
    
    if address_response.status_code != 200 and address_response.status_code != 201:
        print(f"Failed to create address: {address_response.status_code}")
        print(address_response.text)
        return
    
    address_id = address_response.json().get("address_id")
    print(f"Successfully created address with ID: {address_id}")
    
    # Now try creating an address history record
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Test 1: With UUID as string for address_id, no verification_document_id
    history_payload_1 = {
        "address_id": address_id,
        "start_date": yesterday,
        "end_date": None,
        "is_current": True,
        "address_type": "residential"
    }
    
    print("\nTest 1: Creating address history with string UUID...")
    history_response_1 = requests.post(
        f"{base_url}/history/address-history", 
        json=history_payload_1
    )
    
    print(f"Status Code: {history_response_1.status_code}")
    print(f"Response: {history_response_1.text}")
    
    if history_response_1.status_code == 200 or history_response_1.status_code == 201:
        print("Success! Address history record created.")
        return
    
    # Test 2: With UUID in proper UUID format for both fields
    history_payload_2 = {
        "address_id": address_id,
        "start_date": yesterday,
        "is_current": True,
        "address_type": "residential",
        "verification_document_id": None  # Explicitly set to None
    }
    
    print("\nTest 2: Creating address history with explicit None for verification_document_id...")
    history_response_2 = requests.post(
        f"{base_url}/history/address-history", 
        json=history_payload_2
    )
    
    print(f"Status Code: {history_response_2.status_code}")
    print(f"Response: {history_response_2.text}")
    
    # Test 3: Without the verification_document_id field at all
    history_payload_3 = {
        "address_id": address_id,
        "start_date": yesterday,
        "is_current": True,
        "address_type": "residential"
    }
    
    print("\nTest 3: Creating address history without verification_document_id field...")
    history_response_3 = requests.post(
        f"{base_url}/debug/debug-request",  # Use debug endpoint to see the exact payload
        json=history_payload_3
    )
    
    print(f"Status Code: {history_response_3.status_code}")
    print(f"Response: {history_response_3.text}")

if __name__ == "__main__":
    print("Testing address history creation...")
    test_create_address_history()