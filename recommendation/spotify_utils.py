def format_playlist_response(playlist_data):
    """formating the playlist response for correct API output."""
    if not playlist_data or "playlists" not in playlist_data:
        return {"error": "Invalid Spotify API response"}

    items = playlist_data.get("playlists", {}).get("items", [])
    if not items:
        return {"error": "No playlists found"}

    return [
        {
            "name": item["name"],
            "url": item["external_urls"]["spotify"]
        }
        for item in items[:5] if item is not None  
    ]


def format_song_response(song_data):
    """formatting the song response for correct API output."""
    items = song_data.get("tracks", {}).get("items", [])
    if not items:
        return [{"message": "No songs found"}]
    
    return [
        {
            "title": item["name"],
            "artist": ", ".join([artist["name"] for artist in item["artists"]]),
            "url": item["external_urls"]["spotify"]
        }
        for item in items
    ]
