#!/usr/bin/env python3
"""
Google Places API Enrichment Test Script
Tests enrichment on 13 sample stations to calculate real API costs

Requirements:
    pip install googlemaps requests python-dotenv

Setup:
    1. Get Google Places API key from: https://console.cloud.google.com/
    2. Enable "Places API (New)" in your Google Cloud project
    3. Set environment variable: export GOOGLE_PLACES_API_KEY="your-key-here"
       OR create .env file with: GOOGLE_PLACES_API_KEY=your-key-here
"""

import csv
import json
import os
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')
PLACES_API_BASE_URL = 'https://places.googleapis.com/v1'

# Cost tracking (per Google's pricing as of Nov 2024)
COSTS = {
    'text_search': 0.032,      # Text Search (New)
    'place_details_basic': 0.00,  # Basic fields are free
    'place_details_contact': 0.003,  # Contact fields
    'place_details_atmosphere': 0.005,  # Atmosphere fields (rating, reviews)
}


@dataclass
class EnrichmentResult:
    """Stores enrichment results for a station"""
    # Original data
    csv_name: str
    csv_address: str
    csv_phone: str
    csv_county: str

    # Matching results
    matched: bool
    confidence_score: float
    match_method: str

    # Google Places data
    google_place_id: Optional[str] = None
    google_name: Optional[str] = None
    google_address: Optional[str] = None
    google_phone: Optional[str] = None
    website: Optional[str] = None
    google_maps_url: Optional[str] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    business_status: Optional[str] = None
    types: Optional[List[str]] = None
    opening_hours: Optional[Dict] = None
    wheelchair_accessible: Optional[bool] = None

    # Cost tracking
    api_calls_made: int = 0
    total_cost: float = 0.0

    # Error tracking
    error: Optional[str] = None


class AddressMatcher:
    """Handles address normalization and matching logic"""

    @staticmethod
    def normalize_address(address: str) -> str:
        """Normalize address for comparison"""
        # Convert to uppercase
        addr = address.upper()

        # Remove extra whitespace
        addr = ' '.join(addr.split())

        # Standardize abbreviations
        replacements = {
            ' STREET': ' ST',
            ' AVENUE': ' AVE',
            ' ROAD': ' RD',
            ' DRIVE': ' DR',
            ' BOULEVARD': ' BLVD',
            ' LANE': ' LN',
            ' COURT': ' CT',
            ' CIRCLE': ' CIR',
            ' HIGHWAY': ' HWY',
            ' PIKE': ' PIKE',  # Keep pike as is
            ' NORTH': ' N',
            ' SOUTH': ' S',
            ' EAST': ' E',
            ' WEST': ' W',
            ' NORTHEAST': ' NE',
            ' NORTHWEST': ' NW',
            ' SOUTHEAST': ' SE',
            ' SOUTHWEST': ' SW',
        }

        for old, new in replacements.items():
            addr = addr.replace(old, new)

        # Remove punctuation except spaces and hyphens
        addr = re.sub(r'[^\w\s\-]', '', addr)

        # Extract just the street address (before city/state/zip)
        # Format is usually: "123 MAIN ST , CITY PA 12345-6789"
        parts = addr.split(',')
        if parts:
            street = parts[0].strip()
            return street

        return addr

    @staticmethod
    def calculate_similarity(addr1: str, addr2: str) -> float:
        """Calculate similarity score between two addresses (0.0 to 1.0)"""
        norm1 = AddressMatcher.normalize_address(addr1)
        norm2 = AddressMatcher.normalize_address(addr2)

        return SequenceMatcher(None, norm1, norm2).ratio()

    @staticmethod
    def extract_zip(address: str) -> Optional[str]:
        """Extract ZIP code from address"""
        match = re.search(r'\b(\d{5})(?:-\d{4})?\b', address)
        return match.group(1) if match else None

    @staticmethod
    def is_match(csv_address: str, google_address: str,
                 csv_name: str = None, google_name: str = None,
                 threshold: float = 0.85) -> Tuple[bool, float, str]:
        """
        Determine if addresses match using address-first logic

        Returns: (is_match, confidence_score, match_method)
        """
        # Primary: Address similarity
        addr_similarity = AddressMatcher.calculate_similarity(csv_address, google_address)

        if addr_similarity >= threshold:
            return (True, addr_similarity, 'address_exact')

        # Secondary: Address + ZIP match
        if addr_similarity >= 0.7:
            csv_zip = AddressMatcher.extract_zip(csv_address)
            google_zip = AddressMatcher.extract_zip(google_address)

            if csv_zip and google_zip and csv_zip == google_zip:
                # Addresses are similar and ZIP matches - likely a match
                confidence = (addr_similarity + 1.0) / 2  # Boost confidence
                return (True, confidence, 'address_zip')

        # Tertiary: Name + ZIP (for cases where address format differs)
        if csv_name and google_name:
            name_similarity = SequenceMatcher(None,
                                            csv_name.upper(),
                                            google_name.upper()).ratio()

            if name_similarity >= 0.8:
                csv_zip = AddressMatcher.extract_zip(csv_address)
                google_zip = AddressMatcher.extract_zip(google_address)

                if csv_zip and google_zip and csv_zip == google_zip:
                    confidence = name_similarity * 0.9  # Slightly lower confidence
                    return (True, confidence, 'name_zip')

        # No match
        return (False, addr_similarity, 'no_match')


class GooglePlacesEnricher:
    """Handles Google Places API calls and enrichment"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.total_cost = 0.0
        self.api_call_count = 0

    def text_search(self, query: str) -> Tuple[Optional[Dict], float]:
        """
        Search for a place using Text Search (New)
        Returns: (result_dict, cost)
        """
        url = f"{PLACES_API_BASE_URL}/places:searchText"

        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.id,places.displayName,places.formattedAddress,places.location'
        }

        payload = {
            'textQuery': query,
            'languageCode': 'en'
        }

        try:
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            cost = COSTS['text_search']
            self.total_cost += cost
            self.api_call_count += 1

            # Return first result if available
            if data.get('places') and len(data['places']) > 0:
                return (data['places'][0], cost)

            return (None, cost)

        except Exception as e:
            print(f"Error in text_search: {e}")
            return (None, COSTS['text_search'])

    def get_place_details(self, place_id: str) -> Tuple[Optional[Dict], float]:
        """
        Get detailed information about a place
        Returns: (details_dict, cost)
        """
        url = f"{PLACES_API_BASE_URL}/places/{place_id}"

        # Field mask for all fields we want
        fields = [
            'id',
            'displayName',
            'formattedAddress',
            'nationalPhoneNumber',
            'internationalPhoneNumber',
            'websiteUri',
            'googleMapsUri',
            'rating',
            'userRatingCount',
            'businessStatus',
            'types',
            'currentOpeningHours',
            'accessibilityOptions'
        ]

        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': ','.join(fields)
        }

        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Calculate cost based on field groups
            cost = (COSTS['place_details_basic'] +
                   COSTS['place_details_contact'] +
                   COSTS['place_details_atmosphere'])

            self.total_cost += cost
            self.api_call_count += 1

            return (data, cost)

        except Exception as e:
            print(f"Error in get_place_details: {e}")
            # Still count the cost even if it fails
            cost = (COSTS['place_details_basic'] +
                   COSTS['place_details_contact'] +
                   COSTS['place_details_atmosphere'])
            return (None, cost)

    def enrich_station(self, station: Dict) -> EnrichmentResult:
        """
        Full enrichment workflow for a single station
        """
        result = EnrichmentResult(
            csv_name=station['Station Name'],
            csv_address=station['Station Address'],
            csv_phone=station['Phone Number'],
            csv_county=station['County Name'],
            matched=False,
            confidence_score=0.0,
            match_method='not_attempted'
        )

        try:
            # Step 1: Text Search
            query = f"{station['Station Name']}, {station['Station Address']}, Pennsylvania"
            print(f"\n  Searching: {query}")

            search_result, search_cost = self.text_search(query)
            result.api_calls_made += 1
            result.total_cost += search_cost

            if not search_result:
                result.error = "No results found in Text Search"
                print(f"  ❌ No results found")
                return result

            # Step 2: Validate match
            google_address = search_result.get('formattedAddress', '')
            google_name = search_result.get('displayName', {}).get('text', '')

            print(f"  Found: {google_name}")
            print(f"    Google Address: {google_address}")
            print(f"    CSV Address:    {result.csv_address}")

            is_match, confidence, method = AddressMatcher.is_match(
                result.csv_address,
                google_address,
                result.csv_name,
                google_name
            )

            result.matched = is_match
            result.confidence_score = confidence
            result.match_method = method

            print(f"  Match: {is_match} (confidence: {confidence:.2f}, method: {method})")

            if not is_match:
                result.error = f"Address mismatch (similarity: {confidence:.2f})"
                return result

            # Step 3: Get Place Details
            place_id = search_result.get('id', '').replace('places/', '')

            details, details_cost = self.get_place_details(place_id)
            result.api_calls_made += 1
            result.total_cost += details_cost

            if details:
                # Extract all enrichment data
                result.google_place_id = place_id
                result.google_name = details.get('displayName', {}).get('text')
                result.google_address = details.get('formattedAddress')
                result.google_phone = details.get('nationalPhoneNumber') or details.get('internationalPhoneNumber')
                result.website = details.get('websiteUri')
                result.google_maps_url = details.get('googleMapsUri')
                result.rating = details.get('rating')
                result.user_ratings_total = details.get('userRatingCount')
                result.business_status = details.get('businessStatus')
                result.types = details.get('types', [])

                # Parse opening hours
                if 'currentOpeningHours' in details:
                    result.opening_hours = details['currentOpeningHours']

                # Accessibility
                accessibility = details.get('accessibilityOptions', {})
                result.wheelchair_accessible = accessibility.get('wheelchairAccessibleEntrance')

                print(f"  ✅ Enriched successfully!")
                print(f"     Rating: {result.rating} ({result.user_ratings_total} reviews)")
                print(f"     Phone: {result.google_phone}")
                print(f"     Website: {result.website}")

            return result

        except Exception as e:
            result.error = f"Exception: {str(e)}"
            print(f"  ❌ Error: {e}")
            return result


def run_test_enrichment(sample_file: str, output_file: str):
    """Run enrichment test on sample stations"""

    # Validate API key
    if not GOOGLE_PLACES_API_KEY:
        print("❌ ERROR: GOOGLE_PLACES_API_KEY not found!")
        print("\nPlease set your API key:")
        print("  export GOOGLE_PLACES_API_KEY='your-key-here'")
        print("\nOr create a .env file with:")
        print("  GOOGLE_PLACES_API_KEY=your-key-here")
        return

    print(f"✅ Google Places API key found")
    print(f"📊 Loading sample stations from: {sample_file}\n")

    # Load sample stations
    with open(sample_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        stations = list(reader)

    print(f"Testing enrichment on {len(stations)} stations...\n")
    print("=" * 80)

    # Initialize enricher
    enricher = GooglePlacesEnricher(GOOGLE_PLACES_API_KEY)

    # Enrich each station
    results = []
    for i, station in enumerate(stations, 1):
        print(f"\n[{i}/{len(stations)}] {station['Station Name']}")
        print(f"  County: {station['County Name']}")

        result = enricher.enrich_station(station)
        results.append(result)

    # Summary statistics
    print("\n" + "=" * 80)
    print("📊 ENRICHMENT SUMMARY")
    print("=" * 80)

    matched_count = sum(1 for r in results if r.matched)
    avg_confidence = sum(r.confidence_score for r in results if r.matched) / max(matched_count, 1)

    total_api_calls = sum(r.api_calls_made for r in results)
    total_cost = sum(r.total_cost for r in results)
    avg_cost_per_station = total_cost / len(results)

    print(f"\nMatching Results:")
    print(f"  ✅ Matched: {matched_count}/{len(results)} ({matched_count/len(results)*100:.1f}%)")
    print(f"  ❌ Unmatched: {len(results) - matched_count}")
    print(f"  📊 Average confidence: {avg_confidence:.2f}")

    # Match methods breakdown
    methods = {}
    for r in results:
        if r.matched:
            methods[r.match_method] = methods.get(r.match_method, 0) + 1

    print(f"\nMatch Methods:")
    for method, count in methods.items():
        print(f"  - {method}: {count}")

    print(f"\nAPI Usage:")
    print(f"  Total API calls: {total_api_calls}")
    print(f"  Total cost: ${total_cost:.4f}")
    print(f"  Average cost per station: ${avg_cost_per_station:.4f}")

    print(f"\n💰 PROJECTED COSTS FOR 12,627 STATIONS:")
    projected_cost = avg_cost_per_station * 12627
    print(f"  Estimated total: ${projected_cost:.2f}")
    print(f"  (Based on {len(results)} sample stations)")

    # Data completeness
    print(f"\nData Completeness (for matched stations):")
    if matched_count > 0:
        phone_count = sum(1 for r in results if r.matched and r.google_phone)
        website_count = sum(1 for r in results if r.matched and r.website)
        hours_count = sum(1 for r in results if r.matched and r.opening_hours)
        rating_count = sum(1 for r in results if r.matched and r.rating)

        print(f"  Phone: {phone_count}/{matched_count} ({phone_count/matched_count*100:.1f}%)")
        print(f"  Website: {website_count}/{matched_count} ({website_count/matched_count*100:.1f}%)")
        print(f"  Hours: {hours_count}/{matched_count} ({hours_count/matched_count*100:.1f}%)")
        print(f"  Rating: {rating_count}/{matched_count} ({rating_count/matched_count*100:.1f}%)")

    # Save results
    print(f"\n💾 Saving detailed results to: {output_file}")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump([asdict(r) for r in results], f, indent=2)

    print("\n✅ Test complete!")
    print(f"\nNext steps:")
    print(f"  1. Review results in {output_file}")
    print(f"  2. Check unmatched stations and adjust matching logic if needed")
    print(f"  3. Approve projected cost of ${projected_cost:.2f} for full enrichment")
    print(f"  4. Run full enrichment on all 12,627 stations")


if __name__ == '__main__':
    run_test_enrichment(
        sample_file='test_sample_13_stations.csv',
        output_file='test_enrichment_results.json'
    )
