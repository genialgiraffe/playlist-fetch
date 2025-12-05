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
from .json_export import (
    export_playlist_to_json,
    export_playlists,
    sanitize_playlist_name,
    playlist_json_exists,
    get_playlist_json_path
)

__all__ = [
    'get_spotify_client',
    'load_spotify_credentials',
    'fetch_single_playlist',
    'fetch_playlist_tracks',
    'get_user_playlists',
    'extract_track_details',
    'extract_release_year',
    'export_playlist_to_json',
    'export_playlists',
    'sanitize_playlist_name',
    'playlist_json_exists',
    'get_playlist_json_path'
]

