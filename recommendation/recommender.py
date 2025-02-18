import logging
from .spotify_auth import get_spotify_client
from .spotify_utils import format_song_response

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# mood to genre map 🎵
MOOD_GENRE_MAPPING = {
    "happy": ["pop", "dance", "edm", "k-pop", "reggaeton", "house", "funk", "hip-hop", "trap"],
    "sad": ["acoustic", "indie folk", "singer-songwriter", "lo-fi", "blues", "jazz"],
    "angry": ["hard rock", "heavy metal", "punk", "hardcore hip-hop", "drill"],
    "calm": ["ambient", "classical", "soft rock", "indie folk", "chillstep", "lo-fi"]
}

class EmotionRecommender:
    def __init__(self, user_authenticated=False, user_token=None):
        """initialise the recommender system with spotifiy"""
        self.sp = get_spotify_client(user_authenticated, user_token)
        self.user_authenticated = user_authenticated

        if not self.sp:
            logger.error("Spotify client initialization failed.")

    def recommend_songs(self, emotion):
        """generate song recommendations based on emotion and user preferences."""
        if not self.sp:
            return {"error": "Spotify authentication failed"}

        mood_genres = MOOD_GENRE_MAPPING.get(emotion, [])
        all_recommendations = []

        try:
            if self.user_authenticated:
                # Get users top artists & tracks
                top_tracks_response = self.sp.current_user_top_tracks(limit=10, time_range='medium_term')
                top_tracks = [track['id'] for track in top_tracks_response.get('items', [])]

                # Use users top tracks if available
                if top_tracks:
                    track_recs = self.sp.recommendations(seed_tracks=top_tracks[:2], limit=10)
                    all_recommendations.extend(track_recs.get("tracks", []))

            # Fallback: Use genre-based recommendations
            if len(all_recommendations) < 10:
                for genre in mood_genres:
                    search_results = self.sp.search(q=f'genre:"{genre}"', type="track", limit=5)
                    all_recommendations.extend(search_results.get("tracks", {}).get("items", []))

            return format_song_response({"tracks": {"items": all_recommendations[:10]}})
        except Exception as e:
            logger.error(f"Error getting recommended songs: {str(e)}", exc_info=True)
            return {"error": "Spotify API request failed"}
