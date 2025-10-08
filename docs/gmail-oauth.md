How to obtain a Gmail OAuth2 refresh token (local flow)

1) Create OAuth credentials in Google Cloud Console
- Go to https://console.cloud.google.com/apis/credentials
- Create an OAuth 2.0 Client ID of type "Desktop app" (this avoids redirect URI issues with Playground).
- Note the Client ID and Client secret.

2) Use the provided helper script
- Activate your virtualenv and install the helper dependencies:

```powershell
# from project root (Windows PowerShell)
python -m pip install --upgrade pip
python -m pip install google-auth-oauthlib
```

- Run the helper script (replace placeholders):

```powershell
python scripts/get_gmail_refresh_token.py --client-id <CLIENT_ID> --client-secret <CLIENT_SECRET>
```

- The script will open a local browser window and prompt you to authorize. After you complete the flow the script will print a refresh token.

3) Store the refresh token securely
- Save the refresh token into your secret store. For Docker secrets on the host you can:

```bash
echo -n '<refresh-token>' | docker secret create GMAIL_OAUTH2_REFRESH_TOKEN -
```

- Or save it into your cloud provider secret manager (recommended).

4) Configure your app
- Set these values in the production secret store or Docker secrets:
  - GMAIL_OAUTH2_CLIENT_ID
  - GMAIL_OAUTH2_CLIENT_SECRET
  - GMAIL_OAUTH2_REFRESH_TOKEN
- `fundiconnect/settings.py` already reads these from environment variables or `/run/secrets/<NAME>`.

Notes & scopes
- The helper uses the `https://www.googleapis.com/auth/gmail.send` scope by default. If you need full mailbox access use `https://mail.google.com/` (not recommended unless necessary).
- Use a dedicated sending account and do not reuse a personal account.
- Revoke refresh tokens in the Google Account security console if compromised.
