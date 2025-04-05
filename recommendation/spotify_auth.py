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
    """returns a Spotipy client, and ensures that token is refreshed if required."""
    if user_authenticated and user_token:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope="user-top-read playlist-modify-private user-read-recently-played user-library-read",
            cache_path=".cache"  # used only when logged in
        )

        try:
            token_info = auth_manager.get_cached_token()
            if not token_info or auth_manager.is_token_expired(token_info):
                token_info = auth_manager.refresh_access_token(user_token)

            if not token_info or "access_token" not in token_info:
                logger.error("Failed to get a valid Spotify token.")
                return None

            return spotipy.Spotify(auth=token_info["access_token"])

        except Exception as e:
            logger.error(f"Error with Spotify authentication: {str(e)}")
            return None

    # prevent .cache usage for non-authenticated users
    return spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    ))