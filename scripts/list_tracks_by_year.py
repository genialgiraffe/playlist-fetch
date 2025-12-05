#!/usr/bin/env python3
"""
List tracks from a specific year across all playlist JSON files.

Scans JSON files in the data directory and lists all tracks
released in the specified year.
"""

import sys
import os
import json
import argparse
from pathlib import Path
from collections import defaultdict


def extract_playlist_name_from_filename(filename: str) -> str:
    """
    Extract playlist name from JSON filename.
    
    Removes .json extension and returns the playlist name.
    
    Args:
        filename: JSON filename (e.g., "My-Playlist.json")
    
    Returns:
        str: Playlist name (e.g., "My-Playlist")
    """
    # Remove .json extension
    name = filename.replace('.json', '')
    return name


def load_tracks_from_json_files(data_dir: str) -> list:
    """
    Load all tracks from JSON files in the data directory.
    
    Tracks which playlist each track comes from by adding a 'playlist' field.
    
    Args:
        data_dir: Directory containing JSON playlist files
    
    Returns:
        list: List of track dictionaries with 'name', 'artist', 'album', 'release_year', 'playlist'
    """
    tracks = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        print(f"Error: Directory '{data_dir}' does not exist.")
        return tracks
    
    json_files = list(data_path.glob('*.json'))
    
    if not json_files:
        print(f"No JSON files found in '{data_dir}'")
        return tracks
    
    for json_file in json_files:
        try:
            playlist_name = extract_playlist_name_from_filename(json_file.name)
            with open(json_file, 'r', encoding='utf-8') as f:
                playlist_tracks = json.load(f)
                if isinstance(playlist_tracks, list):
                    # Add playlist name to each track
                    for track in playlist_tracks:
                        track_copy = track.copy()
                        track_copy['playlist'] = playlist_name
                        tracks.append(track_copy)
        except json.JSONDecodeError as e:
            print(f"Warning: Error reading {json_file.name}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Error processing {json_file.name}: {e}", file=sys.stderr)
    
    return tracks


def filter_tracks_by_year(tracks: list, year: int) -> list:
    """
    Filter tracks by release year.
    
    Args:
        tracks: List of track dictionaries
        year: Year to filter by
    
    Returns:
        list: Filtered tracks from the specified year
    """
    return [
        track for track in tracks
        if track.get('release_year') == year
    ]


def deduplicate_tracks(tracks: list) -> list:
    """
    Remove duplicate tracks based on name and artist combination.
    Merges playlist names when the same track appears in multiple playlists.
    
    Args:
        tracks: List of track dictionaries with 'playlist' field
    
    Returns:
        list: List of unique tracks with merged playlist names
    """
    track_dict = {}  # key: (name, artist) -> track with merged playlists
    
    for track in tracks:
        name = track.get('name', 'Unknown Track').lower().strip()
        artist = track.get('artist', 'Unknown Artist').lower().strip()
        track_key = (name, artist)
        playlist = track.get('playlist', 'Unknown')
        
        if track_key in track_dict:
            # Track already seen, merge playlist names
            existing_track = track_dict[track_key]
            existing_playlists = existing_track.get('playlists', [existing_track.get('playlist', 'Unknown')])
            
            # Add new playlist if not already in list
            if playlist not in existing_playlists:
                existing_playlists.append(playlist)
            
            # Update the playlists field (sorted for consistency)
            existing_playlists.sort()
            existing_track['playlists'] = existing_playlists
        else:
            # First occurrence of this track
            track_copy = track.copy()
            track_copy['playlists'] = [playlist]
            # Remove the single 'playlist' field, use 'playlists' instead
            if 'playlist' in track_copy:
                del track_copy['playlist']
            track_dict[track_key] = track_copy
    
    return list(track_dict.values())


def format_track(track: dict) -> str:
    """
    Format a track as "Track Name - Artist (Playlist1, Playlist2)".
    
    Args:
        track: Track dictionary with 'playlists' field
    
    Returns:
        str: Formatted track string with playlist names
    """
    name = track.get('name', 'Unknown Track')
    artist = track.get('artist', 'Unknown Artist')
    
    # Get playlist names (handle both 'playlists' list and single 'playlist')
    playlists = track.get('playlists', [])
    if not playlists:
        # Fallback to single playlist field if playlists not set
        playlist = track.get('playlist', 'Unknown')
        if playlist:
            playlists = [playlist]
    
    # Format playlist names
    if playlists:
        playlist_str = ', '.join(playlists)
        return f"{name} - {artist} ({playlist_str})"
    else:
        return f"{name} - {artist}"


def main():
    """List tracks from a specific year."""
    parser = argparse.ArgumentParser(
        description='List tracks from a specific year across all playlist JSON files'
    )
    parser.add_argument(
        'year',
        type=int,
        help='Year to filter tracks by (e.g., 2023)'
    )
    parser.add_argument(
        '-d', '--data-dir',
        default='data',
        help='Directory containing JSON playlist files (default: data)'
    )
    parser.add_argument(
        '--sort',
        choices=['name', 'artist', 'album'],
        default='name',
        help='Sort tracks by field (default: name)'
    )
    parser.add_argument(
        '--group-by-playlist',
        action='store_true',
        help='Group tracks by source playlist'
    )
    
    args = parser.parse_args()
    
    # Load tracks from JSON files
    tracks = load_tracks_from_json_files(args.data_dir)
    
    if not tracks:
        return 1
    
    # Filter by year
    year_tracks = filter_tracks_by_year(tracks, args.year)
    
    if not year_tracks:
        print(f"No tracks found from year {args.year}")
        return 0
    
    # Remove duplicates
    original_count = len(year_tracks)
    year_tracks = deduplicate_tracks(year_tracks)
    duplicates_removed = original_count - len(year_tracks)
    
    # Sort tracks
    if args.sort == 'name':
        year_tracks.sort(key=lambda t: t.get('name', '').lower())
    elif args.sort == 'artist':
        year_tracks.sort(key=lambda t: t.get('artist', '').lower())
    elif args.sort == 'album':
        year_tracks.sort(key=lambda t: t.get('album', '').lower())
    
    # Output tracks
    if args.group_by_playlist:
        # This would require tracking which playlist each track came from
        # For now, just output all tracks
        print(f"Tracks from {args.year} (grouped by playlist not yet implemented):")
        print()
    
    # Print tracks one per line
    for track in year_tracks:
        print(format_track(track))
    
    # Print summary
    summary = f"Total: {len(year_tracks)} unique track(s) from {args.year}"
    if duplicates_removed > 0:
        summary += f" ({duplicates_removed} duplicate(s) removed)"
    print(f"\n{summary}", file=sys.stderr)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

