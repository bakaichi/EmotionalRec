import logging
from .spotify_auth import get_spotify_client
from .spotify_utils import format_song_response
import random

# logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# mood to genre map 🎵
MOOD_GENRE_MAPPING = {
    "happy": ["pop", "dance", "edm", "k-pop", "j-pop", "reggaeton", "house", "funk", "hip-hop", "trap", "afrobeats", "baile funk", "latin urban", "indie pop", "pop rock", "alternative rock", "ska", "trance", "future bass"],
    "sad": ["acoustic", "indie folk", "singer-songwriter", "folk rock", "blues", "jazz", "classical", "lo-fi", "chillhop", "shoegaze", "dream pop", "alt r&b", "soul", "chamber pop", "alternative rock", "emo", "post-rock"],
    "angry": ["hard techno", "heavy metal", "nu metal", "death metal", "thrash metal", "post-hardcore", "industrial metal", "darkwave", "aggrotech", "noise rock", "punk rock", "hardcore punk", "post-punk", "skate punk", "rap metal", "drill", "hardcore hip-hop", "dubstep", "breakcore"],
    "calm": ["ambient", "downtempo", "new age", "meditation", "drone", "bossa nova", "chill jazz", "classical", "baroque", "instrumental", "deep house", "chillstep", "lounge", "trip-hop", "soft techno", "soft rock", "indie folk", "slowcore", "dream pop"]
}

# fallback values
FALLBACK_ARTIST_ID = "4NHQUGzhtTLFvgF5SZesLK"
FALLBACK_TRACKS = ["3n3Ppam7vgaVa1iaRUc9Lp"]

class EmotionRecommender:
    def __init__(self, user_authenticated=False, user_token=None):
        """initialise the recommender system with spotifiy"""
        self.sp = get_spotify_client(user_authenticated, user_token)
        self.user_authenticated = user_authenticated

        if not self.sp:
            logger.error("Spotify client initialization failed.")

    
    def get_top_artists_tracks_genres(self):
        """get the users top artists, tracks, and genres."""
        if not self.user_authenticated:
            return [], [], [], []

        try:
            top_artists_response = self.sp.current_user_top_artists(limit=50, time_range='medium_term')
            artist_data = [(artist['name'], artist['id'], artist['genres']) for artist in top_artists_response.get('items', [])]
            artist_names = [artist[0] for artist in artist_data]
            artist_ids = [artist[1] for artist in artist_data]
            genres = list(set(genre for artist in artist_data for genre in artist[2]))

            top_tracks_response = self.sp.current_user_top_tracks(limit=50, time_range='medium_term')
            track_ids = [track['id'] for track in top_tracks_response.get('items', [])]

            return artist_names, artist_ids, track_ids, genres
        except Exception as e:
            logger.error(f"Error fetching users top artists/tracks/genres: {str(e)}")
            return [], [], [], []

    def recommend_songs(self, emotion):
        """generate song recomendations based on user preferences and mood genre mapping."""
        if not self.sp:
            return {"error": "Spotify authentication failed"}

        top_artists, top_artist_ids, top_tracks, user_genres = self.get_top_artists_tracks_genres()
        mood_genres = MOOD_GENRE_MAPPING.get(emotion, [])
        matched_genres = [genre for genre in user_genres if genre in mood_genres]

        valid_artist_ids = [artist_id for artist_id, genres in zip(top_artist_ids, user_genres) if any(g in mood_genres for g in genres)][:5]
        valid_tracks = top_tracks[:5] if top_tracks else FALLBACK_TRACKS
        valid_genres = matched_genres[:5] if matched_genres else mood_genres[:5]

        all_recommendations = []

        try:
            # get songs based on top artists
            for artist_id in valid_artist_ids:
                top_tracks_by_artist = self.sp.artist_top_tracks(artist_id)['tracks'][:5]
                all_recommendations.extend(top_tracks_by_artist)

            # fallback 1: Fetch songs based on genres
            if len(all_recommendations) < 30 and valid_genres:
                for genre in valid_genres:
                    search_results = self.sp.search(q=f'genre:"{genre}"', type="track", limit=10)
                    if search_results and "tracks" in search_results and "items" in search_results["tracks"]:
                        all_recommendations.extend(search_results["tracks"]["items"])
                        if len(all_recommendations) >= 30:
                            break

            # Last fallback: Use top tracks
            if len(all_recommendations) < 30 and valid_tracks:
                for track_id in valid_tracks:
                    track_info = self.sp.track(track_id)
                    if track_info:
                        all_recommendations.append(track_info)
                        if len(all_recommendations) >= 30:
                            break

            return format_song_response({"tracks": {"items": all_recommendations}})
        except Exception as e:
            logger.error(f"Error fetching recommended songs: {str(e)}", exc_info=True)
            return {"error": "Spotify API request failed"}
        

    def create_playlist(self, emotion, access_token):
        """Create a balanced Spotify playlist based on emotion."""
        if not self.sp:
            return {"error": "Spotify authentication failed"}

        try:
            # Get user's Spotify ID
            user_id = self.sp.current_user()["id"]
            playlist_name = f"{emotion.capitalize()} Vibes"
            
            # Create a private playlist
            playlist = self.sp.user_playlist_create(user=user_id, name=playlist_name, public=False)
            playlist_id = playlist["id"]
            
            # get song recommendations
            recommendation_response = self.recommend_songs(emotion)  
            song_recommendations = recommendation_response # Ensures that its a list
            
            if not song_recommendations:
                return {"error": "No recommendations found to create a playlist"}

            # Filter for diverse tracks - limit repeats
            unique_artists = {}
            balanced_tracks = []
            
            for track in song_recommendations:
                artist = track["artist"]
                if artist not in unique_artists:
                    unique_artists[artist] = 0  # track artist occurrences
                if unique_artists[artist] < 3:  # max 2 songs per artist
                    balanced_tracks.append(track)
                    unique_artists[artist] += 1
            
            # shuffle the songs to avoid clustering similar songs
            random.shuffle(balanced_tracks)
            
            # Ensure getting a variety of genres
            genre_diverse_tracks = []
            seen_genres = set()
            for track in balanced_tracks:
                if len(genre_diverse_tracks) >= 20:  # sets playlist size
                    break
                if track["artist"] in seen_genres:
                    continue
                genre_diverse_tracks.append(track)
                seen_genres.add(track["artist"])

            # convert to Spotify track URI
            track_uris = [track["url"].replace("https://open.spotify.com/track/", "spotify:track:") for track in genre_diverse_tracks]

            # Add songs to playlist
            if track_uris:
                self.sp.playlist_add_items(playlist_id, track_uris)

            return {
                "message": "Playlist created successfully!",
                "playlist_url": playlist["external_urls"]["spotify"]
            }
        
        except Exception as e:
            logger.error(f"Error creating playlist: {str(e)}", exc_info=True)
            return {"error": "Failed to create playlist"}