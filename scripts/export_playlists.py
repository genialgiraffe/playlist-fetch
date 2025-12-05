#!/usr/bin/env python3
"""
Export playlists to JSON files.

Fetches playlists from Spotify and exports them as JSON files
in the specified output directory.
"""

import sys
import os
import argparse

# Add parent directory to path to import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.auth import get_spotify_client
from src.playlist_fetcher import get_user_playlists, fetch_playlist_tracks
from src.json_export import export_playlists, playlist_json_exists


def main():
    """Export playlists to JSON files."""
    parser = argparse.ArgumentParser(
        description='Export Spotify playlists to JSON files'
    )
    parser.add_argument(
        '-o', '--output',
        default='data',
        help='Output directory for JSON files (default: data)'
    )
    parser.add_argument(
        '-m', '--max',
        type=int,
        default=None,
        help='Maximum number of playlists to export (default: all)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Spotify Playlist JSON Exporter")
    print("=" * 60)
    print()
    
    try:
        # Authenticate
        if args.verbose:
            print("Authenticating with Spotify...")
        sp = get_spotify_client()
        if args.verbose:
            print()
        
        # Fetch playlists
        if args.verbose:
            print("Fetching user playlists...")
        playlists_data = get_user_playlists(sp)
        
        if not playlists_data:
            print("No playlists found for this user.")
            return 0
        
        # Limit playlists if specified
        if args.max is not None and args.max > 0:
            playlists_data = playlists_data[:args.max]
            print(f"Processing {len(playlists_data)} playlist(s) (limited to {args.max})")
        else:
            print(f"Found {len(playlists_data)} playlist(s)")
        
        print()
        
        # Fetch tracks for each playlist and prepare for export
        playlists_with_tracks = []
        skipped_count = 0
        
        for i, playlist in enumerate(playlists_data, 1):
            playlist_name = playlist.get('name', 'Unknown')
            playlist_id = playlist.get('id')
            
            # Check if JSON file already exists
            if playlist_json_exists(playlist_name, args.output):
                if args.verbose:
                    print(f"[{i}/{len(playlists_data)}] Skipping {playlist_name} (file already exists)")
                else:
                    print(f"[{i}/{len(playlists_data)}] {playlist_name}... ⊘ (skipped)")
                skipped_count += 1
                continue
            
            if args.verbose:
                print(f"[{i}/{len(playlists_data)}] Fetching tracks for: {playlist_name}")
            else:
                print(f"[{i}/{len(playlists_data)}] {playlist_name}...", end=' ', flush=True)
            
            try:
                tracks = fetch_playlist_tracks(sp, playlist_id, verbose=args.verbose)
                
                playlists_with_tracks.append({
                    'id': playlist_id,
                    'name': playlist_name,
                    'tracks': tracks
                })
                
                if not args.verbose:
                    print(f"✓ ({len(tracks)} tracks)")
                    
            except Exception as e:
                print(f"✗ Error: {e}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
        
        print()
        
        # Show summary of skipped playlists
        if skipped_count > 0:
            print(f"Skipped {skipped_count} playlist(s) (files already exist)")
            print("  (Delete the JSON file to refresh a playlist)")
            print()
        
        # Export to JSON
        if playlists_with_tracks:
            print("Exporting to JSON files...")
            print()
            exported_files = export_playlists(
                playlists_with_tracks,
                output_dir=args.output,
                max_playlists=None,  # Already limited above
                skip_existing=True,  # Skip if exists (shouldn't happen, but safety check)
                verbose=args.verbose
            )
            
            print()
            print("=" * 60)
            print(f"✓ Successfully exported {len(exported_files)} playlist(s)")
            if skipped_count > 0:
                print(f"⊘ Skipped {skipped_count} playlist(s) (already exist)")
            print(f"  Output directory: {args.output}/")
            print("=" * 60)
        else:
            if skipped_count > 0:
                print("All playlists already exist. No new exports.")
            else:
                print("No playlists to export.")
            return 0 if skipped_count > 0 else 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\nExport cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

