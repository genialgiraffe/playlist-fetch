"""
Spotify Authentication Module

Handles OAuth authentication with Spotify using Spotipy.
Automatically handles token refresh and credential management.
"""

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv


def load_spotify_credentials():
    """
    Load Spotify credentials from .env file.
    
    Returns:
        tuple: (CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
    
    Raises:
        ValueError: If required credentials are missing
    """
    load_dotenv()
    
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    redirect_uri = os.getenv('REDIRECT_URI')
    
    if not client_id:
        raise ValueError("CLIENT_ID not found in .env file")
    if not client_secret:
        raise ValueError("CLIENT_SECRET not found in .env file")
    if not redirect_uri:
        raise ValueError("REDIRECT_URI not found in .env file")
    
    return client_id, client_secret, redirect_uri


def get_spotify_client(scope='playlist-read-private'):
    """
    Authenticate with Spotify and return an authenticated Spotipy client.
    
    Spotipy automatically handles:
    - OAuth flow (opens browser for user authorization)
    - Token caching (stores tokens in .cache file)
    - Token refresh (automatically refreshes expired tokens)
    
    Args:
        scope (str): Spotify API scope. Default is 'playlist-read-private'
                    which allows reading user's private playlists.
    
    Returns:
        spotipy.Spotify: Authenticated Spotify client
    
    Raises:
        ValueError: If credentials are missing
        spotipy.exceptions.SpotifyException: If authentication fails
    """
    client_id, client_secret, redirect_uri = load_spotify_credentials()
    
    # SpotifyOAuth handles the OAuth flow automatically
    # It will:
    # 1. Open a browser for user authorization (first time)
    # 2. Cache tokens in .cache-{username} file
    # 3. Automatically refresh tokens when they expire
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        cache_path='.cache'  # Cache tokens for automatic refresh
    )
    
    # Create and return authenticated Spotify client
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Verify authentication by getting current user
    try:
        user = sp.current_user()
        print(f"Authenticated as: {user['display_name']} ({user['id']})")
    except Exception as e:
        raise spotipy.exceptions.SpotifyException(f"Authentication verification failed: {e}")
    
    return sp

