#!/usr/bin/env python3
"""
Verification script for Spotify authentication module.

This script tests that the authentication module is working correctly
by attempting to authenticate with Spotify and display user information.
"""

import sys
import os

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.auth import get_spotify_client


def main():
    """Verify authentication module is working."""
    print("=" * 60)
    print("Spotify Authentication Verification")
    print("=" * 60)
    print()
    
    try:
        print("Attempting to authenticate with Spotify...")
        print("(This may open a browser window for authorization)")
        print()
        
        # Get authenticated client
        sp = get_spotify_client()
        
        # Get and display user information
        user = sp.current_user()
        print()
        print("✓ Authentication successful!")
        print()
        print("User Information:")
        print(f"  Name: {user.get('display_name', 'N/A')}")
        print(f"  ID: {user.get('id', 'N/A')}")
        print(f"  Email: {user.get('email', 'N/A')}")
        print(f"  Country: {user.get('country', 'N/A')}")
        print(f"  Followers: {user.get('followers', {}).get('total', 'N/A')}")
        print()
        
        # Test API access by getting user's playlists count
        playlists = sp.current_user_playlists(limit=1)
        total_playlists = playlists.get('total', 0)
        print(f"✓ API access verified! You have {total_playlists} playlist(s).")
        print()
        print("=" * 60)
        print("Authentication module is working correctly! ✓")
        print("=" * 60)
        
        return 0
        
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print()
        print("Please ensure you have created a .env file with:")
        print("  - CLIENT_ID")
        print("  - CLIENT_SECRET")
        print("  - REDIRECT_URI")
        print()
        print("See .env.example for reference.")
        return 1
        
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print()
        print("Please check:")
        print("  1. Your .env file has correct credentials")
        print("  2. Your Spotify app redirect URI matches REDIRECT_URI")
        print("  3. You have an active internet connection")
        return 1


if __name__ == '__main__':
    sys.exit(main())

