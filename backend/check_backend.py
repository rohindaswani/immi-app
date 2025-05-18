#!/usr/bin/env python3
"""
Script to check backend configuration and dependencies
"""

import sys
import importlib
import os
from pprint import pprint

def check_module(module_name):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError as e:
        return False, str(e)

def main():
    print("=== Backend Configuration Check ===")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check required packages
    required_packages = [
        "fastapi", "uvicorn", "pydantic", "sqlalchemy", "psycopg2",
        "pymongo", "python-jose", "passlib", "python-multipart",
        "httpx", "fastapi-sso", "itsdangerous"
    ]
    
    print("\nChecking required packages:")
    all_packages_installed = True
    for package in required_packages:
        result = check_module(package)
        if result is True:
            print(f"✅ {package}")
        else:
            print(f"❌ {package}: {result[1]}")
            all_packages_installed = False
    
    # Check configuration
    try:
        from app.core.config import settings
        print("\nConfiguration Settings:")
        print(f"API_V1_STR: {settings.API_V1_STR}")
        print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
        
        # Check for Server URL properties
        has_server_url = hasattr(settings, 'SERVER_URL')
        has_server_host = hasattr(settings, 'SERVER_HOST')
        has_server_port = hasattr(settings, 'SERVER_PORT')
        has_server_protocol = hasattr(settings, 'SERVER_PROTOCOL')
        
        print("\nServer URL Settings:")
        if has_server_url:
            if callable(settings.SERVER_URL):
                print(f"SERVER_URL: {settings.SERVER_URL()}")
            else:
                print(f"SERVER_URL: {settings.SERVER_URL}")
        else:
            print("SERVER_URL: ❌ Not defined")
            if has_server_host and has_server_port and has_server_protocol:
                print(f"  - Component parts exist (HOST: {settings.SERVER_HOST}, PORT: {settings.SERVER_PORT})")
            else:
                print("  - Component parts missing too")
        
        # Check Google OAuth settings
        print("\nGoogle OAuth Settings:")
        if hasattr(settings, 'GOOGLE_CLIENT_ID'):
            print(f"GOOGLE_CLIENT_ID: {'✅ Set' if settings.GOOGLE_CLIENT_ID else '❌ Empty'}")
        else:
            print("GOOGLE_CLIENT_ID: ❌ Not defined")
            
        if hasattr(settings, 'GOOGLE_CLIENT_SECRET'):
            print(f"GOOGLE_CLIENT_SECRET: {'✅ Set' if settings.GOOGLE_CLIENT_SECRET else '❌ Empty'}")
        else:
            print("GOOGLE_CLIENT_SECRET: ❌ Not defined")
            
        if hasattr(settings, 'GOOGLE_REDIRECT_URI'):
            print(f"GOOGLE_REDIRECT_URI: {settings.GOOGLE_REDIRECT_URI}")
        else:
            print("GOOGLE_REDIRECT_URI: ❌ Not defined")
            
        if hasattr(settings, 'GOOGLE_CALLBACK_URL'):
            if callable(settings.GOOGLE_CALLBACK_URL):
                print(f"GOOGLE_CALLBACK_URL: {settings.GOOGLE_CALLBACK_URL()}")
            else:
                print(f"GOOGLE_CALLBACK_URL: {settings.GOOGLE_CALLBACK_URL}")
        else:
            print("GOOGLE_CALLBACK_URL: ❌ Not defined")
            
        if hasattr(settings, 'GOOGLE_AUTHORIZE_URL'):
            if callable(settings.GOOGLE_AUTHORIZE_URL):
                print(f"GOOGLE_AUTHORIZE_URL: {settings.GOOGLE_AUTHORIZE_URL()}")
            else:
                print(f"GOOGLE_AUTHORIZE_URL: {settings.GOOGLE_AUTHORIZE_URL}")
        else:
            print("GOOGLE_AUTHORIZE_URL: ❌ Not defined")
            
        if hasattr(settings, 'GOOGLE_TOKEN_URL'):
            if callable(settings.GOOGLE_TOKEN_URL):
                print(f"GOOGLE_TOKEN_URL: {settings.GOOGLE_TOKEN_URL()}")
            else:
                print(f"GOOGLE_TOKEN_URL: {settings.GOOGLE_TOKEN_URL}")
        else:
            print("GOOGLE_TOKEN_URL: ❌ Not defined")
            
        if hasattr(settings, 'GOOGLE_USER_INFO_URL'):
            if callable(settings.GOOGLE_USER_INFO_URL):
                print(f"GOOGLE_USER_INFO_URL: {settings.GOOGLE_USER_INFO_URL()}")
            else:
                print(f"GOOGLE_USER_INFO_URL: {settings.GOOGLE_USER_INFO_URL}")
        else:
            print("GOOGLE_USER_INFO_URL: ❌ Not defined")
        
        # Import and check GoogleAuthService
        try:
            from app.services.google_auth import GoogleAuthService
            print("\nGoogleAuthService:")
            print("✅ Successfully imported")
        except ImportError as e:
            print(f"\n❌ Error importing GoogleAuthService: {str(e)}")
        
    except ImportError as e:
        print(f"\n❌ Error importing settings: {str(e)}")
    
    # Summary
    print("\n=== Summary ===")
    if all_packages_installed:
        print("✅ All required packages are installed")
    else:
        print("❌ Some packages are missing")
    
    print("\nTo fix missing packages, run:")
    print("pip install -r requirements.txt")
    
if __name__ == "__main__":
    main()