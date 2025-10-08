This document explains how to wire email and Gmail OAuth2 credentials into the environment for the FundiConnect project.

Overview
- Settings will read environment variables first. If a variable is missing, the settings module will try to read a Docker secret file at /run/secrets/<NAME>.

Environment variable names used by settings
- EMAIL_HOST_USER
- EMAIL_HOST_PASSWORD
- DEFAULT_FROM_EMAIL
- GMAIL_OAUTH2_CLIENT_ID
- GMAIL_OAUTH2_CLIENT_SECRET
- GMAIL_OAUTH2_REFRESH_TOKEN
- GMAIL_SMTP_HOST (optional — default smtp.gmail.com)
- GMAIL_SMTP_PORT (optional — default 587)

PowerShell: set env vars for local development (temporary for that shell session)
Replace placeholder values with your real secrets.

```powershell
$env:EMAIL_HOST_USER = 'your-gmail-username@gmail.com'
$env:EMAIL_HOST_PASSWORD = 'your-smtp-password-or-empty-if-using-oauth'
$env:DEFAULT_FROM_EMAIL = 'fguila2357@gmail.com'
$env:GMAIL_OAUTH2_CLIENT_ID = '<your-client-id.apps.googleusercontent.com>'
$env:GMAIL_OAUTH2_CLIENT_SECRET = '<your-client-secret>'
$env:GMAIL_OAUTH2_REFRESH_TOKEN = '<your-refresh-token>'
$env:GMAIL_SMTP_HOST = 'smtp.gmail.com'
$env:GMAIL_SMTP_PORT = '587'
```

Notes:
- These env vars only persist for the current PowerShell session. For persistent configuration use Windows System Environment Variables or add them to your profile script.
- If you use Gmail OAuth2 (recommended), set the GMAIL_* variables; EMAIL_HOST_PASSWORD can remain empty.

Create Docker secrets on the host
Recommended secret names match the env var names used by settings. Run these commands on the Docker host (or in WSL if on Windows):

```bash
# create secrets from literal values (Unix-like shell)
echo -n 'my-email-password' | docker secret create EMAIL_HOST_PASSWORD -
echo -n 'fguila2357@gmail.com' | docker secret create DEFAULT_FROM_EMAIL -
echo -n '<client-id>' | docker secret create GMAIL_OAUTH2_CLIENT_ID -
echo -n '<client-secret>' | docker secret create GMAIL_OAUTH2_CLIENT_SECRET -
echo -n '<refresh-token>' | docker secret create GMAIL_OAUTH2_REFRESH_TOKEN -
echo -n 'smtp.gmail.com' | docker secret create GMAIL_SMTP_HOST -
echo -n '587' | docker secret create GMAIL_SMTP_PORT -
```

If you're on Windows and using Docker Desktop, create the secret files first and then create secrets from files, or use WSL for the above commands.

docker-compose example (secrets)
This example maps the secrets into the service and relies on `fundiconnect/settings.py` to read /run/secrets/<NAME>:

```yaml
version: '3.8'
services:
  web:
    image: your-image:latest
    build: .
    ports:
      - "8000:8000"
    secrets:
      - EMAIL_HOST_PASSWORD
      - DEFAULT_FROM_EMAIL
      - GMAIL_OAUTH2_CLIENT_ID
      - GMAIL_OAUTH2_CLIENT_SECRET
      - GMAIL_OAUTH2_REFRESH_TOKEN
      - GMAIL_SMTP_HOST
      - GMAIL_SMTP_PORT
    environment:
      - EMAIL_HOST_USER=your-gmail-username@gmail.com
      - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
    command: gunicorn fundiconnect.wsgi:application --bind 0.0.0.0:8000

secrets:
  EMAIL_HOST_PASSWORD:
    external: true
  DEFAULT_FROM_EMAIL:
    external: true
  GMAIL_OAUTH2_CLIENT_ID:
    external: true
  GMAIL_OAUTH2_CLIENT_SECRET:
    external: true
  GMAIL_OAUTH2_REFRESH_TOKEN:
    external: true
  GMAIL_SMTP_HOST:
    external: true
  GMAIL_SMTP_PORT:
    external: true
```

How the app reads secrets
- When the container runs, Docker makes each secret available at `/run/secrets/<NAME>`.
- `fundiconnect/settings.py` first checks environment variables; if a value is empty it will try the corresponding `/run/secrets/<NAME>` file and use that value.

Quick test (after setting env vars)
1. Set env vars in PowerShell (see earlier snippet).
2. From project root, run:

```powershell
python manage.py send_test_otp recipient@example.com
```

- If you get an authentication or XOAUTH2 error, double-check your OAuth2 client/refresh token and ensure the Gmail account allows SMTP access (for app-passwords) or that the OAuth2 refresh token is valid and has the proper scopes.

Security recommendations
- Use a managed secret store in production (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) or Docker secrets.
- Rotate client secrets and refresh tokens regularly.
- Configure SPF/DKIM/DMARC for the sending domain.
- Consider a transactional email provider (SES, SendGrid, Mailgun) if you send significant volumes.

Troubleshooting tips
- If you see an invalid_client or redirect_uri error when obtaining a refresh token, verify the client type (Desktop vs Web) and the redirect URI or use `google-auth-oauthlib` for a local flow.
- If SMTP authentication fails with 530, make sure the credentials are correct or the OAuth2 flow is working.

If you'd like, I can add this to README.md or commit a short section into your main README. I can also create a tiny Python helper script to generate a refresh token using `google-auth-oauthlib` if you want to avoid the OAuth2 Playground.