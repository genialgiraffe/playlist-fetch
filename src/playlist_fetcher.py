"""
Playlist Fetcher Module

Fetches playlists and tracks from Spotify, extracting minimal track details.
Handles pagination and edge cases.
"""

import re
from typing import List, Dict, Optional


def extract_release_year(release_date: Optional[str]) -> Optional[int]:
    """
    Extract release year from Spotify release_date field.
    
    Handles various date formats:
    - YYYY (e.g., "2023")
    - YYYY-MM-DD (e.g., "2023-05-15")
    - YYYY-MM (e.g., "2023-05")
    
    Args:
        release_date: Release date string from Spotify API
    
    Returns:
        int: Release year, or None if date is missing or invalid
    """
    if not release_date:
        return None
    
    # Extract year (first 4 digits)
    match = re.match(r'^(\d{4})', release_date)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    
    return None


def format_artists(artists: List[Dict]) -> str:
    """
    Format list of artist objects into a comma-separated string.
    
    Args:
        artists: List of artist dicts from Spotify API
    
    Returns:
        str: Comma-separated artist names
    """
    if not artists:
        return "Unknown Artist"
    
    return ", ".join(artist.get('name', 'Unknown') for artist in artists)


def extract_track_details(track_item: Dict) -> Optional[Dict]:
    """
    Extract minimal track details from Spotify track item.
    
    Args:
        track_item: Track item from Spotify playlist tracks response
    
    Returns:
        dict: Track details with name, artist, album, release_year
              Returns None if track is None (e.g., deleted track)
    """
    # Handle deleted tracks (track can be None)
    track = track_item.get('track')
    if not track:
        return None
    
    # Extract track name
    track_name = track.get('name', 'Unknown Track')
    
    # Extract artists
    artists = track.get('artists', [])
    artist = format_artists(artists)
    
    # Extract album info
    album = track.get('album', {})
    album_name = album.get('name', 'Unknown Album')
    
    # Extract release year
    release_date = album.get('release_date')
    release_year = extract_release_year(release_date)
    
    return {
        'name': track_name,
        'artist': artist,
        'album': album_name,
        'release_year': release_year
    }


def fetch_playlist_tracks(sp, playlist_id: str, verbose: bool = False) -> List[Dict]:
    """
    Fetch all tracks from a playlist, handling pagination.
    
    Args:
        sp: Authenticated Spotipy client
        playlist_id: Spotify playlist ID
        verbose: If True, print progress information
    
    Returns:
        list: List of track detail dictionaries
    """
    tracks = []
    offset = 0
    limit = 100  # Spotify API max per request
    
    if verbose:
        print(f"Fetching tracks from playlist {playlist_id}...")
    
    while True:
        try:
            # Fetch tracks with pagination
            results = sp.playlist_tracks(playlist_id, limit=limit, offset=offset)
            
            if not results or 'items' not in results:
                break
            
            items = results['items']
            if not items:
                break
            
            # Extract track details from each item
            for item in items:
                track_details = extract_track_details(item)
                if track_details:  # Skip deleted tracks
                    tracks.append(track_details)
            
            if verbose:
                print(f"  Fetched {len(tracks)} tracks so far...")
            
            # Check if there are more tracks
            if results.get('next'):
                offset += limit
            else:
                break
                
        except Exception as e:
            print(f"Error fetching tracks: {e}")
            break
    
    if verbose:
        print(f"Total tracks fetched: {len(tracks)}")
    
    return tracks


def get_user_playlists(sp, limit: int = 50) -> List[Dict]:
    """
    Get all playlists for the authenticated user.
    
    Args:
        sp: Authenticated Spotipy client
        limit: Maximum number of playlists to fetch per request
    
    Returns:
        list: List of playlist dictionaries with id, name, etc.
    """
    playlists = []
    offset = 0
    
    while True:
        try:
            results = sp.current_user_playlists(limit=limit, offset=offset)
            
            if not results or 'items' not in results:
                break
            
            items = results['items']
            if not items:
                break
            
            playlists.extend(items)
            
            # Check if there are more playlists
            if results.get('next'):
                offset += limit
            else:
                break
                
        except Exception as e:
            print(f"Error fetching playlists: {e}")
            break
    
    return playlists


def fetch_single_playlist(sp, playlist_name: Optional[str] = None, 
                         playlist_id: Optional[str] = None,
                         verbose: bool = False) -> Optional[Dict]:
    """
    Fetch a single playlist and its tracks.
    
    Can fetch by:
    - playlist_id: Direct playlist ID
    - playlist_name: Name of playlist (fetches first matching)
    - Neither: Fetches first playlist
    
    Args:
        sp: Authenticated Spotipy client
        playlist_name: Name of playlist to fetch (optional)
        playlist_id: Spotify playlist ID (optional, takes precedence)
        verbose: If True, print progress information
    
    Returns:
        dict: Playlist info with tracks, or None if not found
              Format: {
                  'id': playlist_id,
                  'name': playlist_name,
                  'tracks': [list of track dicts]
              }
    """
    # If playlist_id is provided, use it directly
    if playlist_id:
        if verbose:
            print(f"Fetching playlist by ID: {playlist_id}")
        try:
            playlist = sp.playlist(playlist_id)
            playlist_name = playlist.get('name', 'Unknown')
            tracks = fetch_playlist_tracks(sp, playlist_id, verbose)
            
            return {
                'id': playlist_id,
                'name': playlist_name,
                'tracks': tracks
            }
        except Exception as e:
            print(f"Error fetching playlist by ID: {e}")
            return None
    
    # Otherwise, get user playlists and find the one we want
    if verbose:
        print("Fetching user playlists...")
    
    playlists = get_user_playlists(sp)
    
    if not playlists:
        print("No playlists found for this user.")
        return None
    
    # Find the playlist
    target_playlist = None
    
    if playlist_name:
        # Search for playlist by name (case-insensitive)
        for p in playlists:
            if p.get('name', '').lower() == playlist_name.lower():
                target_playlist = p
                break
        
        if not target_playlist:
            print(f"Playlist '{playlist_name}' not found.")
            print(f"Available playlists: {[p.get('name') for p in playlists[:10]]}")
            return None
    else:
        # Default to first playlist
        target_playlist = playlists[0]
        if verbose:
            print(f"No playlist specified, using first playlist: {target_playlist.get('name')}")
    
    playlist_id = target_playlist.get('id')
    playlist_name = target_playlist.get('name', 'Unknown')
    
    if verbose:
        print(f"Fetching playlist: {playlist_name} (ID: {playlist_id})")
    
    # Fetch tracks
    tracks = fetch_playlist_tracks(sp, playlist_id, verbose)
    
    return {
        'id': playlist_id,
        'name': playlist_name,
        'tracks': tracks
    }

