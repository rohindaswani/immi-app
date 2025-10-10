# Google OAuth Setup Instructions

## Step 1: Regenerate Google OAuth Credentials

⚠️ **CRITICAL**: Your old credentials were exposed in git history and MUST be regenerated.

1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)

2. **Delete the old OAuth 2.0 Client ID:**
   - Find the client ID: `23499702166-mna8jepgbrr1j9cv7clv2bsjlkbm177o`
   - Click the trash icon to delete it

3. **Create a new OAuth 2.0 Client ID:**
   - Click "+ CREATE CREDENTIALS" → "OAuth 2.0 Client ID"
   - Application type: **Web application**
   - Name: `Immigration Advisor`
   - Authorized JavaScript origins:
     - `http://localhost:8000`
     - `http://localhost:3000`
   - Authorized redirect URIs:
     - `http://localhost:8000/auth/google/callback`
     - `http://localhost:8000/api/v1/auth/google/callback`
   - Click **CREATE**

4. **Copy your new credentials:**
   - Client ID: `[YOUR-NEW-CLIENT-ID].apps.googleusercontent.com`
   - Client Secret: `[YOUR-NEW-CLIENT-SECRET]`

## Step 2: Add to ~/.zshrc

Add these lines to your `~/.zshrc` file:

```bash
# Immigration Advisor - Google OAuth Credentials
export GOOGLE_CLIENT_ID="YOUR-NEW-CLIENT-ID.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="YOUR-NEW-CLIENT-SECRET"

# Immigration Advisor - JWT Secret (generate this)
export SECRET_KEY="YOUR-GENERATED-SECRET-KEY"

# Optional: Other credentials
export OPENAI_API_KEY="your-openai-key-here"
export PINECONE_API_KEY="your-pinecone-key-here"
```

## Step 3: Generate JWT Secret Key

Run this command to generate a secure secret key:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and use it as your `SECRET_KEY` in the .zshrc file above.

## Step 4: Reload Your Shell

```bash
source ~/.zshrc
```

Or close and reopen your terminal.

## Step 5: Verify Environment Variables

```bash
# Check that variables are set (will show values)
echo $GOOGLE_CLIENT_ID
echo $GOOGLE_CLIENT_SECRET
echo $SECRET_KEY
```

## Step 6: Test the Application

Start the databases:
```bash
./start_databases.sh
```

Then start the backend (which will load credentials from environment):
```bash
./start_backend.sh
```

The application should now start with your new credentials loaded from environment variables.

**Note:** Don't use `run_with_hardcoded_config.sh` - that script overwrites the config with hardcoded values, defeating the purpose of using environment variables!

## Security Notes

✅ **DO:**
- Store credentials in `~/.zshrc` (not tracked by git)
- Regenerate credentials if ever exposed
- Use different credentials for production

❌ **DON'T:**
- Commit credentials to git
- Share your `.zshrc` file
- Use the same credentials across environments
- Reuse the old exposed credentials

## Troubleshooting

**If OAuth isn't working:**

1. Check environment variables are loaded:
   ```bash
   python3 -c "import os; print('CLIENT_ID:', os.getenv('GOOGLE_CLIENT_ID'))"
   ```

2. Verify redirect URI matches exactly in Google Console

3. Check browser console for CORS errors

4. Make sure you deleted the old OAuth client in Google Console
