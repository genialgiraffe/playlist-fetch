"""
Theme Matcher Module

Core matching and scoring logic for finding tracks that match a theme
using keyword and synonym matching.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional


def load_tracks_from_json_files(data_dir: str) -> List[Dict]:
    """
    Load all tracks from JSON files in the data directory.
    
    Adds a 'playlist' field to each track indicating which playlist it came from.
    
    Args:
        data_dir: Directory containing JSON playlist files
    
    Returns:
        List of track dictionaries with 'name', 'artist', 'album', 'release_year', 'playlist'
    """
    tracks = []
    data_path = Path(data_dir)
    
    if not data_path.exists():
        return tracks
    
    json_files = list(data_path.glob('*.json'))
    
    for json_file in json_files:
        try:
            # Extract playlist name from filename
            playlist_name = json_file.stem
            
            with open(json_file, 'r', encoding='utf-8') as f:
                playlist_tracks = json.load(f)
                if isinstance(playlist_tracks, list):
                    # Add playlist name to each track
                    for track in playlist_tracks:
                        track_copy = track.copy()
                        track_copy['playlist'] = playlist_name
                        tracks.append(track_copy)
        except json.JSONDecodeError:
            # Skip malformed JSON files
            continue
        except Exception:
            # Skip files with other errors
            continue
    
    return tracks


def expand_keywords_with_synonyms(keywords: List[str], synonyms: Dict[str, List[str]]) -> Set[str]:
    """
    Expand a list of keywords with their synonyms.
    
    Args:
        keywords: List of base keywords
        synonyms: Dictionary mapping keywords to lists of synonyms
    
    Returns:
        Set of all keywords and synonyms (normalized to lowercase)
    """
    expanded = set()
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        expanded.add(keyword_lower)
        
        # Add synonyms if they exist
        if keyword_lower in synonyms:
            for synonym in synonyms[keyword_lower]:
                expanded.add(synonym.lower())
    
    return expanded


def find_matches_in_text(text: str, keywords: Set[str]) -> List[Tuple[str, bool]]:
    """
    Find all keyword matches in a text string.
    
    Args:
        text: Text to search in
        keywords: Set of keywords to search for (lowercase)
    
    Returns:
        List of tuples: (matched_keyword, is_full_word_match)
    """
    if not text:
        return []
    
    text_lower = text.lower()
    matches = []
    
    for keyword in keywords:
        # Check for full word match (word boundary)
        word_boundary_pattern = r'\b' + re.escape(keyword) + r'\b'
        if re.search(word_boundary_pattern, text_lower, re.IGNORECASE):
            matches.append((keyword, True))
        # Check for substring match
        elif keyword in text_lower:
            matches.append((keyword, False))
    
    return matches


def score_track(track: Dict, keywords: Set[str], 
                location_multipliers: Dict[str, int] = None) -> Tuple[int, Dict]:
    """
    Score a track based on keyword matches.
    
    Args:
        track: Track dictionary with 'name', 'artist', 'album' fields
        keywords: Set of keywords to match (lowercase)
        location_multipliers: Dictionary mapping field names to multipliers
                             (default: name=3, artist=2, album=1)
    
    Returns:
        Tuple of (total_score, match_details_dict)
        match_details contains:
        - 'matches': List of matched keywords
        - 'locations': Dict mapping field names to lists of matched keywords
        - 'full_word_matches': Set of keywords that matched as full words
    """
    if location_multipliers is None:
        location_multipliers = {'name': 3, 'artist': 2, 'album': 1}
    
    total_score = 0
    matched_keywords = set()
    location_matches = {'name': [], 'artist': [], 'album': []}
    full_word_matches = set()
    
    # Search in each field
    for field_name, multiplier in location_multipliers.items():
        field_value = track.get(field_name, '')
        if not field_value:
            continue
        
        matches = find_matches_in_text(str(field_value), keywords)
        
        for keyword, is_full_word in matches:
            matched_keywords.add(keyword)
            location_matches[field_name].append(keyword)
            
            if is_full_word:
                full_word_matches.add(keyword)
                # Full word match: +2 points
                total_score += 2 * multiplier
            else:
                # Substring match: +1 point
                total_score += 1 * multiplier
    
    match_details = {
        'matches': sorted(matched_keywords),
        'locations': {k: v for k, v in location_matches.items() if v},
        'full_word_matches': sorted(full_word_matches),
        'score': total_score
    }
    
    return total_score, match_details


def find_matching_tracks(tracks: List[Dict], keywords: Set[str],
                         synonyms: Dict[str, List[str]] = None,
                         min_score: int = 0) -> List[Tuple[Dict, Dict]]:
    """
    Find all tracks that match the given keywords.
    
    Args:
        tracks: List of track dictionaries
        keywords: Set of base keywords to search for
        synonyms: Optional dictionary mapping keywords to synonyms
        min_score: Minimum score threshold (default: 0, returns all matches)
    
    Returns:
        List of tuples: (track_dict, match_details_dict)
        Sorted by score (descending), then alphabetically by track name
    """
    # Expand keywords with synonyms
    if synonyms:
        expanded_keywords = expand_keywords_with_synonyms(list(keywords), synonyms)
    else:
        expanded_keywords = {k.lower() for k in keywords}
    
    matching_tracks = []
    
    for track in tracks:
        score, match_details = score_track(track, expanded_keywords)
        
        if score >= min_score:
            matching_tracks.append((track, match_details))
    
    # Sort by score (descending), then by track name (ascending)
    matching_tracks.sort(key=lambda x: (-x[1]['score'], x[0].get('name', '').lower()))
    
    return matching_tracks

