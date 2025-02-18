from fastapi import APIRouter, Query, HTTPException
from recommendation.spotify_auth import get_spotify_oauth
from recommendation.recommender import EmotionRecommender


router = APIRouter()
sp_oauth = get_spotify_oauth()

@router.get("/recommend/{emotion}", summary="Get song recommendations based on emotion")
def get_recommendations(emotion: str, access_token: str = None):
    """
    Get song recommendations based on the user's emotion.

    - **emotion**: The emotion to base recommendations on (happy, sad, angry, calm).
    - **access_token**: Spotify access token for personalized recommendations.
    """
    VALID_EMOTIONS = {"happy", "sad", "angry", "calm"}
    if emotion not in VALID_EMOTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid emotion: {emotion}. Valid emotions are {VALID_EMOTIONS}.")

    user_authenticated = bool(access_token)
    recommender = EmotionRecommender(user_authenticated=user_authenticated, user_token=access_token)

    return {
        "emotion": emotion,
        "recommended_songs": recommender.recommend_songs(emotion),
    }


@router.get("/login", summary="Login to Spotify")
def login():
    """Redirects the user to Spotify's authorization page."""
    auth_url = sp_oauth.get_authorize_url()
    return {"message": "Click the link to login to Spotify", "auth_url": auth_url}

@router.get("/callback", summary="Spotify OAuth Callback")
def callback(code: str = Query(None)):
    """Handles the OAuth callback from Spotify and returns an access token."""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing.")
    
    token_info = sp_oauth.get_access_token(code)
    if not token_info:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token.")
    
    return {"message": "Login successful!", "access_token": token_info["access_token"]}
