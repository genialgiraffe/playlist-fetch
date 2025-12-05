#!/usr/bin/env python3
"""
Find tracks matching a theme across all playlist JSON files.

Searches track names, artist names, and album names for keywords and synonyms,
then ranks results by relevance score.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set

# Add src directory to path for imports
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

# Import directly from module to avoid loading package __init__
from theme_matcher import (
    load_tracks_from_json_files,
    find_matching_tracks,
    expand_keywords_with_synonyms
)


def load_synonyms(synonym_file: str) -> Dict[str, List[str]]:
    """
    Load synonym mappings from a JSON file.
    
    Args:
        synonym_file: Path to JSON file with synonym mappings
    
    Returns:
        Dictionary mapping keywords (lowercase) to lists of synonyms
    """
    synonym_path = Path(synonym_file)
    
    if not synonym_path.exists():
        return {}
    
    try:
        with open(synonym_path, 'r', encoding='utf-8') as f:
            synonyms_raw = json.load(f)
        
        # Normalize keys to lowercase
        synonyms = {}
        for key, values in synonyms_raw.items():
            key_lower = key.lower()
            synonyms[key_lower] = [v.lower() for v in values] if isinstance(values, list) else []
        
        return synonyms
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in synonym file '{synonym_file}': {e}", file=sys.stderr)
        return {}
    except Exception as e:
        print(f"Error: Could not load synonym file '{synonym_file}': {e}", file=sys.stderr)
        return {}


def format_match_details(match_details: Dict) -> str:
    """
    Format match details as a readable string.
    
    Args:
        match_details: Match details dictionary from score_track
    
    Returns:
        Formatted string describing matches
    """
    parts = []
    
    locations = match_details.get('locations', {})
    full_words = set(match_details.get('full_word_matches', []))
    
    for field in ['name', 'artist', 'album']:
        if field in locations:
            matched_keywords = locations[field]
            match_types = []
            for kw in matched_keywords:
                if kw in full_words:
                    match_types.append(f"{kw}*")  # * indicates full word match
                else:
                    match_types.append(kw)
            parts.append(f"{field}: {', '.join(match_types)}")
    
    return "; ".join(parts) if parts else "No matches"


def print_results(matching_tracks: List, verbose: bool = False):
    """
    Print matching tracks in a formatted table.
    
    Args:
        matching_tracks: List of (track, match_details) tuples
        verbose: If True, show detailed match information
    """
    if not matching_tracks:
        print("No matching tracks found.")
        return
    
    print(f"\nFound {len(matching_tracks)} matching track(s):\n")
    
    # Print header
    if verbose:
        print(f"{'Score':<6} {'Track':<50} {'Artist':<40} {'Album':<40} {'Playlist':<30}")
        print("-" * 170)
    else:
        print(f"{'Score':<6} {'Track':<50} {'Artist':<40} {'Playlist':<30}")
        print("-" * 130)
    
    # Print tracks
    for track, match_details in matching_tracks:
        score = match_details['score']
        track_name = track.get('name', 'Unknown')[:49]
        artist = track.get('artist', 'Unknown')[:39]
        album = track.get('album', 'Unknown')[:39] if verbose else ''
        playlist = track.get('playlist', 'Unknown')[:29]
        
        if verbose:
            print(f"{score:<6} {track_name:<50} {artist:<40} {album:<40} {playlist:<30}")
            match_info = format_match_details(match_details)
            print(f"      └─ {match_info}")
        else:
            print(f"{score:<6} {track_name:<50} {artist:<40} {playlist:<30}")
    
    print()


def export_results_json(matching_tracks: List, output_file: str):
    """
    Export matching tracks to a JSON file.
    
    Args:
        matching_tracks: List of (track, match_details) tuples
        output_file: Path to output JSON file
    """
    results = []
    
    for track, match_details in matching_tracks:
        result = {
            'track': track,
            'score': match_details['score'],
            'matched_keywords': match_details['matches'],
            'match_locations': match_details['locations'],
            'full_word_matches': match_details['full_word_matches']
        }
        results.append(result)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Results exported to: {output_file}")


def main():
    """Main entry point for the theme track finder."""
    parser = argparse.ArgumentParser(
        description='Find tracks matching a theme across all playlist JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s skeleton-key
  %(prog)s skeleton-key --synonyms themes/custom-synonyms.json
  %(prog)s skeleton-key --data-dir scripts/data --verbose
  %(prog)s skeleton-key --min-score 5 --export results.json
        """
    )
    
    parser.add_argument(
        'theme',
        help='Theme name (used to find synonym file: themes/{theme}.json)'
    )
    
    parser.add_argument(
        '--synonyms', '-s',
        type=str,
        help='Path to synonym JSON file (default: themes/{theme}.json)'
    )
    
    parser.add_argument(
        '--data-dir', '-d',
        default='scripts/data',
        help='Directory containing playlist JSON files (default: scripts/data)'
    )
    
    parser.add_argument(
        '--min-score',
        type=int,
        default=0,
        help='Minimum score threshold (default: 0)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed match information'
    )
    
    parser.add_argument(
        '--export',
        type=str,
        help='Export results to JSON file'
    )
    
    args = parser.parse_args()
    
    # Determine synonym file path
    if args.synonyms:
        synonym_file = args.synonyms
    else:
        # Default to themes/{theme}.json
        synonym_file = f"themes/{args.theme}.json"
    
    # Load synonyms
    synonyms = load_synonyms(synonym_file)
    
    # Extract base keywords from theme name (split by hyphens, underscores, spaces)
    theme_keywords = re.split(r'[-_\s]+', args.theme)
    theme_keywords = [kw.lower() for kw in theme_keywords if kw]
    
    # Also include the full theme name as a keyword
    theme_keywords.append(args.theme.lower())
    
    print(f"Theme: {args.theme}")
    print(f"Keywords: {', '.join(theme_keywords)}")
    
    if synonyms:
        # Expand keywords with synonyms
        expanded = expand_keywords_with_synonyms(theme_keywords, synonyms)
        print(f"Expanded keywords (with synonyms): {', '.join(sorted(expanded))}")
    else:
        print(f"Note: No synonym file found at '{synonym_file}' (using keywords only)")
    
    print(f"\nLoading tracks from: {args.data_dir}")
    
    # Load tracks
    tracks = load_tracks_from_json_files(args.data_dir)
    
    if not tracks:
        print(f"Error: No tracks found in '{args.data_dir}'", file=sys.stderr)
        return 1
    
    print(f"Loaded {len(tracks)} track(s) from playlist files")
    
    # Find matching tracks
    print(f"\nSearching for matches (min score: {args.min_score})...")
    matching_tracks = find_matching_tracks(
        tracks,
        set(theme_keywords),
        synonyms if synonyms else None,
        min_score=args.min_score
    )
    
    # Print summary
    playlists_searched = len(set(track.get('playlist', '') for track, _ in matching_tracks))
    print(f"\nSummary:")
    print(f"  - Tracks searched: {len(tracks)}")
    print(f"  - Matching tracks: {len(matching_tracks)}")
    print(f"  - Playlists with matches: {playlists_searched}")
    
    # Print or export results
    if args.export:
        export_results_json(matching_tracks, args.export)
    else:
        print_results(matching_tracks, verbose=args.verbose)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

