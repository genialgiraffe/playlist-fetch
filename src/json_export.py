"""
JSON Export Module

Exports playlists to JSON files with sanitized filenames.
"""

import os
import json
import re
from typing import List, Dict, Optional, Union
from pathlib import Path


def sanitize_playlist_name(name: str) -> str:
    """
    Sanitize playlist name for use as a filename.
    
    Removes or replaces invalid filename characters.
    
    Args:
        name: Playlist name
    
    Returns:
        str: Sanitized filename-safe string
    """
    # Remove or replace invalid characters
    # Keep alphanumeric, spaces, hyphens, underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
    
    # Replace multiple spaces/hyphens with single
    sanitized = re.sub(r'[\s-]+', '-', sanitized)
    
    # Remove leading/trailing hyphens and spaces
    sanitized = sanitized.strip('- ')
    
    # Limit length (max 200 chars for filename)
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    # If empty after sanitization, use a default
    if not sanitized:
        sanitized = "playlist"
    
    return sanitized


def get_playlist_json_path(playlist_name: str, output_dir: str = 'data') -> str:
    """
    Get the expected JSON file path for a playlist.
    
    Args:
        playlist_name: Name of the playlist
        output_dir: Directory where JSON files are saved
    
    Returns:
        str: Expected filepath for the playlist JSON file
    """
    sanitized_name = sanitize_playlist_name(playlist_name)
    filename = f"{sanitized_name}.json"
    return os.path.join(output_dir, filename)


def playlist_json_exists(playlist_name: str, output_dir: str = 'data') -> bool:
    """
    Check if a JSON file already exists for a playlist.
    
    Args:
        playlist_name: Name of the playlist
        output_dir: Directory where JSON files are saved
    
    Returns:
        bool: True if JSON file exists, False otherwise
    """
    filepath = get_playlist_json_path(playlist_name, output_dir)
    return os.path.exists(filepath)


def export_playlist_to_json(playlist: Dict, output_dir: str = 'data', 
                            skip_existing: bool = True,
                            verbose: bool = False) -> Optional[str]:
    """
    Export a single playlist to a JSON file.
    
    Args:
        playlist: Playlist dict with 'name', 'id', and 'tracks'
        output_dir: Directory to save JSON files (default: 'data')
        skip_existing: If True, skip if file already exists (default: True)
        verbose: If True, print progress information
    
    Returns:
        str: Path to the created JSON file, or None if skipped
    """
    playlist_name = playlist.get('name', 'Unknown')
    
    # Check if file already exists
    if skip_existing:
        filepath = get_playlist_json_path(playlist_name, output_dir)
        if os.path.exists(filepath):
            if verbose:
                print(f"  ⊘ Skipped (file already exists): {filepath}")
            return None
    
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Sanitize playlist name for filename
    sanitized_name = sanitize_playlist_name(playlist_name)
    filename = f"{sanitized_name}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Handle filename collisions by appending number
    counter = 1
    original_filepath = filepath
    while os.path.exists(filepath):
        base_name = sanitized_name
        filename = f"{base_name}_{counter}.json"
        filepath = os.path.join(output_dir, filename)
        counter += 1
    
    # Extract just the tracks array (minimal format)
    tracks = playlist.get('tracks', [])
    
    # Write JSON file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tracks, f, indent=2, ensure_ascii=False)
    
    if verbose:
        print(f"  ✓ Exported {len(tracks)} tracks to: {filepath}")
    
    return filepath


def export_playlists(playlists: List[Dict], output_dir: str = 'data',
                    max_playlists: Optional[int] = None,
                    skip_existing: bool = True,
                    verbose: bool = False) -> List[str]:
    """
    Export multiple playlists to JSON files.
    
    Args:
        playlists: List of playlist dicts with 'name', 'id', and 'tracks'
        output_dir: Directory to save JSON files (default: 'data')
        max_playlists: Maximum number of playlists to export (None = all)
        skip_existing: If True, skip playlists that already have JSON files (default: True)
        verbose: If True, print progress information
    
    Returns:
        list: List of paths to created JSON files
    """
    # Limit number of playlists if specified
    if max_playlists is not None and max_playlists > 0:
        playlists = playlists[:max_playlists]
        if verbose:
            print(f"Processing {len(playlists)} playlist(s) (limited to {max_playlists})")
    else:
        if verbose:
            print(f"Processing {len(playlists)} playlist(s)")
    
    if verbose:
        print(f"Output directory: {output_dir}")
        print()
    
    exported_files = []
    
    for i, playlist in enumerate(playlists, 1):
        playlist_name = playlist.get('name', 'Unknown')
        track_count = len(playlist.get('tracks', []))
        
        if verbose:
            print(f"[{i}/{len(playlists)}] Exporting: {playlist_name} ({track_count} tracks)")
        
        try:
            filepath = export_playlist_to_json(playlist, output_dir, skip_existing, verbose)
            if filepath:  # Only add if not skipped
                exported_files.append(filepath)
        except Exception as e:
            print(f"  ✗ Error exporting {playlist_name}: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
    
    if verbose:
        print()
        print(f"✓ Exported {len(exported_files)} playlist(s) to {output_dir}/")
    
    return exported_files

