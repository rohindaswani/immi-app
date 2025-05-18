# Google OAuth Setup Guide

This guide walks through the process of setting up Google OAuth for the Immigration Advisor application.

## 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top of the page
3. Click "New Project"
4. Enter a name for your project (e.g., "Immigration Advisor")
5. Click "Create"

## 2. Configure OAuth Consent Screen

1. In the left sidebar, navigate to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (for development) and click "Create"
3. Fill in the required fields:
   - App name: "Immigration Advisor"
   - User support email: Your email address
   - Developer contact information: Your email address
4. Click "Save and Continue"
5. On the Scopes screen, click "Add or Remove Scopes"
6. Add the following scopes:
   - `openid`
   - `https://www.googleapis.com/auth/userinfo.email`
   - `https://www.googleapis.com/auth/userinfo.profile`
7. Click "Save and Continue"
8. If asked to add test users, you can add your email
9. Click "Save and Continue" to complete the configuration

## 3. Create OAuth Client ID

1. In the left sidebar, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. For Application type, select "Web application"
4. Name: "Immigration Advisor Web Client"
5. Add Authorized JavaScript origins:
   - `http://localhost:8000`
   - `http://localhost:3000`
6. Add Authorized redirect URIs:
   - `http://localhost:8000/api/v1/auth/google/callback`
7. Click "Create"
8. A popup will display your Client ID and Client Secret. Copy these values.

## 4. Configure Application with Google OAuth Credentials

1. Open the file at `/Users/rohindaswani/Projects/immigration_app/backend/app/core/config.py`
2. Update the following settings with your OAuth credentials:
   ```python
   # GOOGLE OAUTH
   GOOGLE_CLIENT_ID: str = "your-google-client-id.apps.googleusercontent.com"
   GOOGLE_CLIENT_SECRET: str = "your-google-client-secret"
   ```

3. Save the file

## 5. Verify Configuration

Once the credentials are configured, you can test the Google OAuth flow by:

1. Ensuring the backend server is running
2. Visiting: `http://localhost:8000/api/v1/auth/google/login`
3. You should be redirected to Google's login page
4. After successful authentication, you should be redirected back to the application

## Notes

- For development, Google allows OAuth without verification
- For production, you would need to verify your application and add your production domain to the authorized domains list
- Keep your client secret secure and never commit it to version control
- For production, consider using environment variables instead of hardcoding the credentials