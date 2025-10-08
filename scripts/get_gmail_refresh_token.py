"""Small helper to obtain a Gmail OAuth2 refresh token using the local browser flow.

Usage:
  python scripts/get_gmail_refresh_token.py --client-id <CLIENT_ID> --client-secret <CLIENT_SECRET>

It will open a browser to the Google consent screen and print a refresh token you can store securely.

Scopes:
- https://mail.google.com/ or https://www.googleapis.com/auth/gmail.send

Notes:
- Use an "Desktop" type OAuth client in Google Cloud Console for this flow.
- Do not commit the printed refresh token to source control; store it in a secret manager or Docker secret.
"""
import argparse
import os

from google_auth_oauthlib.flow import InstalledAppFlow


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client-id', required=True)
    parser.add_argument('--client-secret', required=True)
    parser.add_argument('--scopes', default='https://www.googleapis.com/auth/gmail.send')
    parser.add_argument('--use-console', action='store_true', help='Use console/oauth out-of-band flow (no local server)')
    parser.add_argument('--port', type=int, default=0, help='If >0 use this port for the local server (also prints redirect URI)')
    args = parser.parse_args()

    # The library expects a JSON client config similar to what Google provides.
    client_config = {
        "installed": {
            "client_id": args.client_id,
            "client_secret": args.client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }

    flow = InstalledAppFlow.from_client_config(client_config, scopes=[s.strip() for s in args.scopes.split(',')])

    creds = None
    if args.use_console:
        print('Using console/OOB flow. You will be asked to paste a code into the terminal.')
        creds = flow.run_console()
    else:
        if args.port and args.port > 0:
            redirect_uri = f'http://localhost:{args.port}/'
            print(f"Using local server on port {args.port}. If you registered a web client, add this redirect URI to the client: {redirect_uri}")
            creds = flow.run_local_server(port=args.port)
        else:
            creds = flow.run_local_server(port=0)

    # creds.refresh_token is the long-lived token you should store securely.
    print('\n--- Save this refresh token to your secret store ---')
    print(creds.refresh_token)
    print('--- Keep it secret and do not commit to source control ---')


if __name__ == '__main__':
    main()
