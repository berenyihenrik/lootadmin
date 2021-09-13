from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
import os

# Environment Variables
CLIENT_ID = os.getenv('LA_CLIENT_ID')
CLIENT_SECRET = os.getenv('LA_CLIENT_SECRET')
REDIRECT = os.getenv('LA_REDIRECT')
CALLBACK = os.getenv('LA_CALLBACK')

# OAuth 2 client setup
client = WebApplicationClient(CLIENT_ID)

def make_session(token=None, state=None, scope=None):
    return OAuth2Session(
        client_id=CLIENT_ID,
        token=token,
        state=state,
        scope=scope,
        redirect_uri=REDIRECT
,
        auto_refresh_kwargs={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
        auto_refresh_url='https://discord.com/api/oauth2/token'
)