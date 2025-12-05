#!/usr/bin/env python3
"""
List available playlists for the authenticated user.

Displays all playlists with their names, IDs, and track counts.
"""

import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.auth import get_spotify_client
from src.playlist_fetcher import get_user_playlists


def main():
    """List all available playlists."""
    print("=" * 60)
    print("Available Playlists")
    print("=" * 60)
    print()
    
    try:
        # Authenticate
        print("Authenticating with Spotify...")
        sp = get_spotify_client()
        print()
        
        # Fetch playlists
        print("Fetching playlists...")
        playlists = get_user_playlists(sp)
        
        if not playlists:
            print("No playlists found for this user.")
            return 0
        
        print()
        print("=" * 60)
        print(f"Found {len(playlists)} playlist(s):")
        print("=" * 60)
        print()
        
        # Display playlists
        for i, playlist in enumerate(playlists, 1):
            name = playlist.get('name', 'Unknown')
            playlist_id = playlist.get('id', 'N/A')
            track_count = playlist.get('tracks', {}).get('total', 'N/A')
            public = 'Public' if playlist.get('public', False) else 'Private'
            owner = playlist.get('owner', {}).get('display_name', 'Unknown')
            
            print(f"{i}. {name}")
            print(f"   ID: {playlist_id}")
            print(f"   Tracks: {track_count}")
            print(f"   Visibility: {public}")
            print(f"   Owner: {owner}")
            print()
        
        print("=" * 60)
        print("To fetch a playlist, use:")
        print("  python scripts/test_playlist_fetcher.py \"Playlist Name\"")
        print("  or")
        print("  python scripts/test_playlist_fetcher.py <playlist_id>")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

