from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, RedirectResponse
from recommendation.spotify_auth import get_spotify_oauth
from recommendation.recommender import EmotionRecommender
import json
import os
import time
from pydrive2.auth import GoogleAuth 
from pydrive2.drive import GoogleDrive
from fastapi import BackgroundTasks
from threading import Event

router = APIRouter()
sp_oauth = get_spotify_oauth()

# storing emotion and playlist result here temporarily
latest_result = {"ready": False, "data": None}
response_event = Event()

@router.post("/logout", summary="Logout from Spotify")
def logout():
    """
    Deletes the Spotify .cache file to simulate logout.
    """
    cache_file = ".cache"

    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
            return JSONResponse(content={"message": "Logged out successfully."}, status_code=200)
        except Exception as e:
            return JSONResponse(content={"error": f"Error deleting cache: {e}"}, status_code=500)

    return JSONResponse(content={"message": "No active session to log out."}, status_code=200)


@router.post("/colab_callback")
def colab_callback(data: dict):
    """
    Called by Colab after processing to send the detected emotion.
    Calls /recommend internally and stores response.
    """
    emotion = data.get("emotion")
    access_token = data.get("access_token")  # optional

    if not emotion:
        raise HTTPException(status_code=400, detail="Emotion not provided.")

    recommender = EmotionRecommender(user_authenticated=bool(access_token), user_token=access_token)
    recommendations = recommender.recommend_songs(emotion)
    playlist = recommender.create_playlist(emotion, access_token) if access_token else None

    result = {
        "emotion": emotion,
        "recommended_songs": recommendations,
        "playlist_created": playlist
    }

    latest_result["data"] = result
    latest_result["ready"] = True
    response_event.set()

    return {"message": "✅ Callback received from Colab."}


@router.get("/token", summary="Get latest Spotify access token")
def get_access_token():
    """Reads the cached access token from the .cache file."""
    cache_file = ".cache"

    if os.path.exists(cache_file):
        with open(cache_file, "r") as file:
            token_data = json.load(file)
            access_token = token_data.get("access_token")
            if access_token:
                return {"access_token": access_token}

    raise HTTPException(status_code=404, detail="No valid access token found.")

@router.post("/recommend")
async def recommend_songs(data: dict):
    """Receive emotion from detection model and return recommended songs (and create a playlist if authenticated)."""
    emotion = data.get("emotion", "").lower()
    access_token = data.get("access_token", None)  # Get access token

    if emotion not in ["happy", "sad", "angry", "calm"]:
        return {"error": "Invalid emotion provided"}

    user_authenticated = bool(access_token)  # Determine if user is logged in
    recommender = EmotionRecommender(user_authenticated=user_authenticated, user_token=access_token)

    recommendations = recommender.recommend_songs(emotion)

    # if a user is authenticated, create a playlist automatically
    playlist_response = None
    if user_authenticated:
        playlist_response = recommender.create_playlist(emotion, access_token)

    return {
        "emotion": emotion,
        "user_authenticated": user_authenticated,
        "recommended_songs": recommendations,
        "playlist_created": playlist_response if user_authenticated else None
    }

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
    """
    Redirects user directly to Spotify auth page.
    """
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(auth_url)

@router.get("/callback", summary="Spotify OAuth Callback")
def callback(code: str = Query(None)):
    """
    Handles the OAuth callback from Spotify.
    Stores access token in .cache and redirects back to frontend.
    """
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing.")

    token_info = sp_oauth.get_access_token(code)
    if not token_info:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token.")

    return RedirectResponse("http://localhost:3000")  # route to be updated if hosted

@router.post("/create-playlist/{emotion}", summary="Create a Spotify playlist based on emotion")
def create_playlist(emotion: str, access_token: str):
    """
    Create a Spotify playlist based on a users emotion.

    - **emotion**: The emotion to base the playlist created on (e.g., happy, sad, angry, calm).
    - **access_token**: Spotify access token for playlist creation.
    """
    recommender = EmotionRecommender(user_authenticated=True, user_token=access_token)
    return recommender.create_playlist(emotion, access_token)

# google drive integration
if not os.path.exists("settings.yaml"):
    raise RuntimeError("Missing Google Drive settings.yaml for PyDrive.")

gauth = GoogleAuth(settings_file="settings.yaml")
gauth.ServiceAuth()
drive = GoogleDrive(gauth)

UPLOAD_FOLDER_ID = "1bb_NAIVPAy-LZiIAL5ydK21eR_8DlbaD"  # Replace with actual folder ID

@router.post("/upload_video")
async def upload_video(video: UploadFile = File(...)):
    try:
        contents = await video.read()
        local_filename = f"temp_{int(time.time())}_{video.filename}"
        with open(local_filename, "wb") as f:
            f.write(contents)

        gfile = drive.CreateFile({"parents": [{"id": UPLOAD_FOLDER_ID}]})
        gfile.SetContentFile(local_filename)
        gfile.Upload()

        os.remove(local_filename)
        return {"success": True, "filename": video.filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process_latest")
def process_latest():
    """
    Waits for Colab to finish processing and calls back with the playlist.
    """
    print("🧠 Waiting for Colab to respond with emotion...")

    # Reset result before waiting
    latest_result["ready"] = False
    latest_result["data"] = None
    response_event.clear()

    # Wait for Colab to send back emotion (timeout after 400s)
    is_set = response_event.wait(timeout=400)

    if not is_set:
        raise HTTPException(status_code=504, detail="Colab processing timed out.")
    
    print("✅ Returning from /process_latest:", latest_result["data"])

    return latest_result["data"]
