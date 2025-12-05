"""
Source package for playlist-fetch application.
"""

from .auth import get_spotify_client, load_spotify_credentials
from .playlist_fetcher import (
    fetch_single_playlist,
    fetch_playlist_tracks,
    get_user_playlists,
    extract_track_details,
    extract_release_year
)

__all__ = [
    'get_spotify_client',
    'load_spotify_credentials',
    'fetch_single_playlist',
    'fetch_playlist_tracks',
    'get_user_playlists',
    'extract_track_details',
    'extract_release_year'
]

