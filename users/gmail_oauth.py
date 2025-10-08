import base64
import smtplib
import logging
import traceback
from email.message import EmailMessage
from typing import Optional
from django.conf import settings

try:
    import requests
except Exception:
    requests = None

logger = logging.getLogger(__name__)


def _get_access_token() -> Optional[str]:
    """Exchange refresh token for an access token using OAuth2 endpoint."""
    client_id = getattr(settings, 'GMAIL_OAUTH2_CLIENT_ID', '')
    client_secret = getattr(settings, 'GMAIL_OAUTH2_CLIENT_SECRET', '')
    refresh_token = getattr(settings, 'GMAIL_OAUTH2_REFRESH_TOKEN', '')
    if not (client_id and client_secret and refresh_token):
        return None

    token_url = 'https://oauth2.googleapis.com/token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
    }
    try:
        resp = requests.post(token_url, data=payload, timeout=10)
        try:
            resp.raise_for_status()
        except Exception:
            # Log response body for debugging
            try:
                logger.error('Token endpoint returned error: %s', resp.text)
            except Exception:
                logger.exception('Token endpoint returned non-JSON error')
            return None
        data = resp.json()
        access_token = data.get('access_token')
        if not access_token:
            logger.error('No access_token in token response: %s', data)
        return access_token
    except Exception:
        logger.exception('Exception while exchanging refresh token')
        return None


def send_via_gmail_oauth2(subject: str, body: str, from_email: str, to_list: list):
    access_token = _get_access_token()
    if not access_token:
        logger.error('Gmail OAuth2 access token unavailable. client_id=%s refresh_token_set=%s',
                     bool(getattr(settings, 'GMAIL_OAUTH2_CLIENT_ID', '')),
                     bool(getattr(settings, 'GMAIL_OAUTH2_REFRESH_TOKEN', '')))
        raise RuntimeError('Gmail OAuth2 access token unavailable. Ensure client_id, client_secret and refresh_token env vars are set.')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = ', '.join(to_list)
    msg.set_content(body)

    smtp_host = getattr(settings, 'GMAIL_SMTP_HOST', 'smtp.gmail.com')
    smtp_port = getattr(settings, 'GMAIL_SMTP_PORT', 587)

    # Build XOAUTH2 string
    auth_string = f'user={from_email}\1auth=Bearer {access_token}\1\1'
    auth_b64 = base64.b64encode(auth_string.encode('utf-8'))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            code, resp = smtp.docmd('AUTH', 'XOAUTH2 ' + auth_b64.decode())
            logger.debug('SMTP AUTH XOAUTH2 response: %s %s', code, resp)
            if code != 235:
                # Authentication failed
                raise smtplib.SMTPAuthenticationError(code, resp)
            smtp.send_message(msg)
    except Exception:
        logger.exception('Failed to send message via XOAUTH2 SMTP')
        raise
