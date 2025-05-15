#!/usr/bin/env python3

import requests
import json
import sys
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def test_health_endpoint():
    """Test the health check endpoint"""
    url = f"{BASE_URL}/health"
    try:
        response = requests.get(url)
        response_data = response.json()
        
        print(f"Health Endpoint Test: {'SUCCESS' if response.status_code == 200 else 'FAILED'}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        print()
        
        return response.status_code == 200
    except Exception as e:
        print(f"Health Endpoint Test FAILED with error: {e}")
        return False

def test_root_endpoint():
    """Test the root endpoint"""
    url = BASE_URL
    try:
        response = requests.get(url)
        response_data = response.json()
        
        print(f"Root Endpoint Test: {'SUCCESS' if response.status_code == 200 else 'FAILED'}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response_data, indent=2)}")
        print()
        
        return response.status_code == 200
    except Exception as e:
        print(f"Root Endpoint Test FAILED with error: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    url = f"{API_URL}/docs"
    try:
        response = requests.get(url)
        
        print(f"API Docs Test: {'SUCCESS' if response.status_code == 200 else 'FAILED'}")
        print(f"Status Code: {response.status_code}")
        print(f"Content Type: {response.headers.get('Content-Type', 'N/A')}")
        print()
        
        return response.status_code == 200
    except Exception as e:
        print(f"API Docs Test FAILED with error: {e}")
        return False

def run_tests():
    """Run all API tests"""
    print("Running API Tests...\n")
    
    # List of all tests
    tests = [
        test_health_endpoint,
        test_root_endpoint,
        test_api_docs
    ]
    
    # Run all tests
    results = [test() for test in tests]
    
    # Print summary
    print("\nTest Summary:")
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {results.count(True)}")
    print(f"Failed: {results.count(False)}")
    
    # Return overall success/failure
    return all(results)

if __name__ == "__main__":
    # Wait a bit to make sure the server is up
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Run the tests
    success = run_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if success else 1)