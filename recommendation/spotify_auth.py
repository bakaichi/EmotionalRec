import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from dotenv import load_dotenv
import logging

# setting up the logger
logger = logging.getLogger(__name__)

# load environment variables
load_dotenv()

# get the Spotify credentials from .env
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET or not REDIRECT_URI:
    raise ValueError("Spotify credentials are missing. Double check your .env file.")

def get_spotify_oauth():
    """returns a Spotify0Auth instance with correct configuration."""
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-top-read playlist-modify-private user-read-recently-played user-library-read"
    )

def get_spotify_client(user_authenticated=False, user_token=None):
    """
    Returns a Spotipy client. If token is invalid or expired, falls back to unauthenticated (public) mode.
    """
    if user_authenticated and user_token:
        try:
            # use token directly (skip .cache/refresh flow)
            return spotipy.Spotify(auth=user_token)
        except Exception as e:
            logger.error(f"error with Spotify authentication: {str(e)}")
            logger.warning("falling back to public client due to auth failure.")
            return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET
            ))

    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))
