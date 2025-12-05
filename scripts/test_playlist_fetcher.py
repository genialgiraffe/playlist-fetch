#!/usr/bin/env python3
"""
Test script for playlist fetcher module.

Tests fetching a single playlist and displays the results.
"""

import sys
import os
import json

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.auth import get_spotify_client
from src.playlist_fetcher import fetch_single_playlist


def main():
    """Test playlist fetcher."""
    print("=" * 60)
    print("Playlist Fetcher Test")
    print("=" * 60)
    print()
    
    # Parse command line arguments
    playlist_name = None
    playlist_id = None
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        # Check if it looks like a Spotify ID (alphanumeric, 22 chars)
        if len(arg) == 22 and arg.replace('-', '').replace('_', '').isalnum():
            playlist_id = arg
        else:
            playlist_name = arg
    
    try:
        # Authenticate
        print("Authenticating with Spotify...")
        sp = get_spotify_client()
        print()
        
        # Fetch playlist
        print("Fetching playlist...")
        playlist = fetch_single_playlist(
            sp,
            playlist_name=playlist_name,
            playlist_id=playlist_id,
            verbose=True
        )
        
        if not playlist:
            print("Failed to fetch playlist.")
            return 1
        
        print()
        print("=" * 60)
        print(f"Playlist: {playlist['name']}")
        print(f"ID: {playlist['id']}")
        print(f"Total Tracks: {len(playlist['tracks'])}")
        print("=" * 60)
        print()
        
        # Display first few tracks
        print("First 5 tracks:")
        print("-" * 60)
        for i, track in enumerate(playlist['tracks'][:5], 1):
            year_str = f" ({track['release_year']})" if track['release_year'] else ""
            print(f"{i}. {track['name']} - {track['artist']}{year_str}")
            print(f"   Album: {track['album']}")
        
        if len(playlist['tracks']) > 5:
            print(f"\n... and {len(playlist['tracks']) - 5} more tracks")
        
        print()
        print("=" * 60)
        print("Playlist fetcher is working correctly! ✓")
        print("=" * 60)
        
        # Optionally save to JSON for inspection
        output_file = f"test_playlist_{playlist['id']}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(playlist, f, indent=2, ensure_ascii=False)
        print(f"\nPlaylist data saved to: {output_file}")
        
        return 0
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    print("Usage: python test_playlist_fetcher.py [playlist_name_or_id]")
    print("  If no argument provided, fetches first playlist")
    print("  If argument is a 22-char ID, fetches by ID")
    print("  Otherwise, searches for playlist by name")
    print()
    sys.exit(main())

