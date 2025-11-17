# PA Vehicle Inspections Data Enrichment Plan v2.0
**Date:** November 16, 2025
**Total Stations:** 12,627
**Database:** Supabase (PostgreSQL)
**Status:** Ready for API cost testing

---

## 🎯 Executive Summary

This is a complete reimagining of the data enrichment strategy, starting from scratch with clean baseline data. We're enriching **12,627 Pennsylvania inspection stations** using a multi-phase approach that prioritizes cost efficiency and data accuracy.

**Key Changes from Previous Approach:**
- ✅ Clean source data (12,627 stations vs flawed 5,000+)
- ✅ Address-first matching (not name-based "match scores")
- ✅ Cost-optimized Google Places API strategy
- ✅ Test-first approach (validate costs on 13 samples before full run)
- ✅ Supabase/PostgreSQL database design

**Estimated Total Cost:** ~$500-700 (to be confirmed by test)

---

## 📊 Current Baseline Data (CSV)

**Source:** `PA Inspection Data - Cleaned and Filtered (11.15.25) - All Stations.csv`

**Fields Available:**
- County Name
- Station Name
- OIS # (Official Inspection Station number - unique ID)
- Station Address
- Phone Number
- Inspects Passenger Cars and Light trucks (boolean)
- Inspects Medium Trucks (boolean)
- Inspects Heavy Trucks (boolean)
- Inspects Motorcycles (boolean)
- Inspects Light Trailers Less Than 10,000 lbs or less (boolean)
- Inspects Heavy Trailers over 10,000 lbs (boolean)

**Data Quality:**
- ✅ Complete coverage (12,627 stations)
- ✅ All stations have: name, address, county, OIS #
- ✅ Most have phone numbers
- ✅ Inspection types are clearly defined
- ⚠️ No hours, ratings, websites, or other enrichment data

---

## 🏗️ Enrichment Architecture

### Phase 1: Automated Baseline Enhancement
**Coverage:** 100% (12,627 stations)
**Cost:** $0
**Time:** 2-3 hours (automated)

#### 1.1 Geographic Enrichment
- **Geocode all addresses** to latitude/longitude
- Use Google Geocoding API: $0.005 per address = ~$63
- Alternative: Bulk geocoding services (Nominatim, etc.) - slower but free
- Enables "near me" searches and distance calculations

#### 1.2 Emissions Requirements (County Lookup)
Pennsylvania requires emissions testing in 25 counties:

**Enhanced Emissions (5 counties):**
- Allegheny, Bucks, Chester, Delaware, Montgomery

**Basic Emissions (20 counties):**
- Armstrong, Beaver, Berks, Blair, Butler, Cambria, Carbon, Centre, Columbia, Cumberland, Dauphin, Lackawanna, Lancaster, Lebanon, Lehigh, Luzerne, Lycoming, Mercer, Northampton, Washington, Westmoreland, York

**Automated Fields:**
```javascript
{
  emissions_required: boolean,
  emissions_type: "enhanced" | "basic" | "none",
  emissions_tests: ["obd2", "visual_check", "gas_cap_test"]
}
```

#### 1.3 Inspection Types Conversion
Convert CSV booleans to searchable arrays:

```javascript
{
  inspection_types: [
    "passenger_cars",      // if Inspects Passenger Cars = TRUE
    "medium_trucks",       // if Inspects Medium Trucks = TRUE
    "heavy_trucks",        // if Inspects Heavy Trucks = TRUE
    "motorcycles",         // if Inspects Motorcycles = TRUE
    "light_trailers",      // if Inspects Light Trailers = TRUE
    "heavy_trailers"       // if Inspects Heavy Trailers = TRUE
  ]
}
```

#### 1.4 Business Type Inference
Initial categorization from business name:

```javascript
// Chain detection
chains = ["jiffy lube", "midas", "meineke", "pep boys", "firestone",
          "goodyear", "valvoline", "monro", "aamco", "mavis"]

// Dealership detection
dealership_brands = ["ford", "chevrolet", "toyota", "honda", "nissan",
                     "hyundai", "kia", "subaru", "mazda", "volkswagen",
                     "bmw", "mercedes", "audi", "lexus", "acura"]

// Specialty detection
if "harley" or "motorcycle" in name:
  business_type = "motorcycle_specialist"
else if chain in name:
  business_type = "chain"
else if dealership_brand in name:
  business_type = "dealership"
else:
  business_type = "independent"
```

**Output:** All 12,627 stations have basic enrichment fields

---

### Phase 2: Google Places API Enrichment
**Coverage:** Target 90%+ (11,364+ stations)
**Estimated Cost:** ~$500-700
**Time:** 4-6 hours (automated batch processing)

#### 2.1 Matching Strategy: Address-First Algorithm

**Three-Tier Matching Logic:**

**Tier 1: Address Exact Match (85%+ similarity)**
```
Query: "{Station Name}, {Full Address}, Pennsylvania"
API: Places API (New) - Text Search

Normalize both addresses:
- Remove punctuation
- Standardize abbreviations (ST/STREET, AVE/AVENUE, RD/ROAD)
- Extract street address only (before city/state/zip)
- Calculate similarity score

IF similarity >= 85%:
  MATCH (method: "address_exact")
```

**Tier 2: Address + ZIP Match (70%+ similarity + same ZIP)**
```
IF address similarity >= 70% AND csv_zip == google_zip:
  MATCH (method: "address_zip")
  confidence_boost = true
```

**Tier 3: Name + ZIP Match (80%+ name similarity + same ZIP)**
```
IF name similarity >= 80% AND csv_zip == google_zip:
  MATCH (method: "name_zip")
  confidence = 0.9 * name_similarity
```

**No Match:**
```
IF no match found:
  FLAG for manual review
  Attempt web search for alternate business name
  Check if station is permanently closed
```

**Expected Match Rate:** 85-90% (10,733-11,364 stations)

#### 2.2 Data Fields to Extract

**API: Places API (New) - Place Details**

**Field Groups & Costs:**
- Basic fields (FREE): `id`, `location`, `displayName`, `formattedAddress`
- Contact fields ($0.003): `phoneNumber`, `websiteUri`, `googleMapsUri`
- Atmosphere fields ($0.005): `rating`, `userRatingCount`, `reviews`
- Opening hours ($0.003): `currentOpeningHours`, `regularOpeningHours`

**Total cost per station:** $0.032 (Text Search) + $0.011 (Place Details) = **$0.043**

**Fields Extracted:**
```javascript
{
  // Identity & Contact
  google_place_id: "ChIJ...",
  google_name: "194 Imports Inc",
  google_address: "680 Hanover Pike, Littlestown, PA 17340",
  google_phone: "(717) 359-7752",
  website: "https://194imports.com",
  google_maps_url: "https://goo.gl/maps/...",

  // Hours
  opening_hours: {
    monday: {open: "08:00", close: "17:00"},
    tuesday: {open: "08:00", close: "17:00"},
    wednesday: {open: "08:00", close: "17:00"},
    thursday: {open: "08:00", close: "17:00"},
    friday: {open: "08:00", close: "17:00"},
    saturday: {open: "08:00", close: "12:00"},
    sunday: "closed"
  },
  hours_display: "Mon-Fri 8AM-5PM, Sat 8AM-12PM, Sun Closed",

  // Trust Signals
  rating: 4.5,
  user_ratings_total: 127,
  review_snippet: "Great service, honest mechanics...",

  // Status
  business_status: "OPERATIONAL",  // or "CLOSED_PERMANENTLY", "CLOSED_TEMPORARILY"

  // Categories
  google_types: ["car_repair", "car_dealer"],

  // Accessibility
  wheelchair_accessible: true,

  // Match metadata
  match_confidence: 0.95,
  match_method: "address_exact"
}
```

#### 2.3 Derived Fields (Computed from Hours)

```javascript
{
  has_weekend_hours: true,        // If Saturday or Sunday hours exist
  has_evening_hours: false,       // If open past 6pm any day
  open_late_weekday: false,       // If open past 7pm Mon-Fri
  appointment_only: false,        // Inferred from reviews/types
}
```

#### 2.4 Batch Processing Strategy

```python
# Process in batches to manage rate limits and monitor progress
batch_size = 100  # Adjust based on rate limits

for batch in chunks(all_stations, batch_size):
    results = process_batch(batch)
    save_to_supabase(results)

    # Progress tracking
    log_progress(completed, total, match_rate, avg_cost)

    # Error handling
    if error_rate > 10%:
        pause_and_review()
```

**Rate Limits:**
- Google Places API: 1,000 requests per day (free tier)
- Paid tier: Contact Google for higher limits
- Processing time: ~6 hours for 12,627 stations (with rate limiting)

---

### Phase 3: Strategic Web Search Enrichment
**Coverage:** Selective (top stations + unmatched)
**Cost:** Time-based (manual/semi-automated)
**Priority:** After Phase 2 completion

#### 3.1 Certification Hunting (Top 1,000 Stations by Review Count)

**Target Certifications:**
- AAA Approved Auto Repair
- ASE Certified (Automotive Service Excellence)
- BBB Accredited
- NAPA AutoCare Center
- Manufacturer certifications (for dealerships)

**Search Strategy:**
```
For each top station:
  1. Check AAA.com approved shop directory
  2. Search: "{station_name} ASE certified Pennsylvania"
  3. Check BBB.org business profile
  4. Visit station website for certification badges

  Time estimate: 2-3 minutes per station
  Total time: 30-50 hours (can be distributed/parallelized)
```

#### 3.2 Gap Filling (Unmatched Stations ~10-15%)

For stations that didn't match Google Places:

```
1. Web search for business name + city
2. Check if business is permanently closed
3. Look for alternate business names
   - "DBA" (doing business as) variations
   - Rebranding
   - Ownership changes
4. Check Facebook Business, Yelp, Yellow Pages
5. Attempt manual Google Maps search

If found:
  - Update business name
  - Re-run matching
  - Flag for verification

If not found:
  - Mark as "unverified"
  - Flag for user-submitted corrections
```

#### 3.3 Specialization Detection

For unique/specialty stations:
- Motorcycle-only shops → brand specializations (Harley, BMW, etc.)
- Heavy truck stations → diesel certifications, fleet services
- European car dealers → luxury brand specializations
- Performance shops → racing, custom work

**Source:** Business websites, reviews, Google types

---

## 🗄️ Supabase Database Schema

### Core Tables

```sql
-- Main stations table
CREATE TABLE stations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Core identity (from CSV)
  ois_number VARCHAR(50) UNIQUE NOT NULL,
  county VARCHAR(50) NOT NULL,
  station_name VARCHAR(255) NOT NULL,
  address TEXT NOT NULL,
  phone_csv VARCHAR(20),

  -- Geographic (Phase 1)
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  geog GEOGRAPHY(POINT),  -- For PostGIS spatial queries

  -- Emissions (Phase 1 - automated)
  emissions_required BOOLEAN,
  emissions_type VARCHAR(20),  -- 'enhanced', 'basic', 'none'

  -- Inspection types (Phase 1 - from CSV booleans)
  inspects_passenger_cars BOOLEAN,
  inspects_medium_trucks BOOLEAN,
  inspects_heavy_trucks BOOLEAN,
  inspects_motorcycles BOOLEAN,
  inspects_light_trailers BOOLEAN,
  inspects_heavy_trailers BOOLEAN,
  inspection_types TEXT[],  -- Searchable array

  -- Business classification (Phase 1 - inferred)
  business_type VARCHAR(50),  -- 'chain', 'dealership', 'independent', etc.

  -- Google Places enrichment (Phase 2)
  google_place_id VARCHAR(255) UNIQUE,
  google_matched BOOLEAN DEFAULT FALSE,
  google_match_confidence DECIMAL(3,2),
  google_match_method VARCHAR(50),
  google_name VARCHAR(255),
  google_address TEXT,
  google_phone VARCHAR(20),
  website TEXT,
  google_maps_url TEXT,

  -- Hours (Phase 2)
  hours_json JSONB,  -- Structured hours data
  hours_display VARCHAR(255),  -- Human-readable
  has_weekend_hours BOOLEAN,
  has_evening_hours BOOLEAN,

  -- Trust signals (Phase 2)
  rating DECIMAL(2,1),
  user_ratings_total INTEGER,
  review_snippet TEXT,
  business_status VARCHAR(50),  -- 'OPERATIONAL', 'CLOSED_PERMANENTLY', etc.

  -- Categories (Phase 2)
  google_types TEXT[],
  wheelchair_accessible BOOLEAN,

  -- Certifications (Phase 3 - selective)
  certifications TEXT[],  -- Array of certification tags
  specializations TEXT[],

  -- Data quality tracking
  enrichment_status VARCHAR(50),  -- 'complete', 'partial', 'pending', 'failed'
  enrichment_date TIMESTAMP,
  data_quality_score DECIMAL(3,2),  -- 0.0 to 1.0
  needs_manual_review BOOLEAN DEFAULT FALSE,
  review_reason TEXT,

  -- Timestamps
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_stations_county ON stations(county);
CREATE INDEX idx_stations_geog ON stations USING GIST(geog);
CREATE INDEX idx_stations_inspection_types ON stations USING GIN(inspection_types);
CREATE INDEX idx_stations_google_types ON stations USING GIN(google_types);
CREATE INDEX idx_stations_rating ON stations(rating);
CREATE INDEX idx_stations_ois ON stations(ois_number);

-- Full-text search
CREATE INDEX idx_stations_search ON stations USING GIN(
  to_tsvector('english',
    station_name || ' ' ||
    COALESCE(google_name, '') || ' ' ||
    COALESCE(address, '')
  )
);
```

### Supporting Tables

```sql
-- Tag tables for normalized categories

CREATE TABLE certification_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag_name VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  description TEXT,
  logo_url TEXT,
  verification_required BOOLEAN DEFAULT FALSE
);

CREATE TABLE specialization_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag_name VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  icon VARCHAR(50),
  category VARCHAR(50)  -- 'vehicle_type', 'service_type', etc.
);

CREATE TABLE service_category_tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag_name VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  icon VARCHAR(50)
);

-- Emissions requirements lookup
CREATE TABLE emissions_requirements (
  county VARCHAR(50) PRIMARY KEY,
  required BOOLEAN NOT NULL,
  emissions_type VARCHAR(20),  -- 'enhanced' or 'basic'
  testing_methods TEXT[]
);

-- Insert emissions data
INSERT INTO emissions_requirements (county, required, emissions_type, testing_methods) VALUES
  ('ALLEGHENY', TRUE, 'enhanced', ARRAY['obd2', 'visual_check', 'gas_cap_test']),
  ('BUCKS', TRUE, 'enhanced', ARRAY['obd2', 'visual_check', 'gas_cap_test']),
  ('CHESTER', TRUE, 'enhanced', ARRAY['obd2', 'visual_check', 'gas_cap_test']),
  ('DELAWARE', TRUE, 'enhanced', ARRAY['obd2', 'visual_check', 'gas_cap_test']),
  ('MONTGOMERY', TRUE, 'enhanced', ARRAY['obd2', 'visual_check', 'gas_cap_test']),
  -- ... (add all 25 emissions counties)
  ('ADAMS', FALSE, 'none', ARRAY['visual_check']);

-- Enrichment audit log
CREATE TABLE enrichment_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  station_id UUID REFERENCES stations(id),
  enrichment_phase VARCHAR(50),
  status VARCHAR(50),
  api_calls_made INTEGER,
  cost_incurred DECIMAL(10,4),
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Manual review queue
CREATE TABLE review_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  station_id UUID REFERENCES stations(id),
  reason VARCHAR(100),
  priority INTEGER DEFAULT 0,
  assigned_to VARCHAR(100),
  resolved BOOLEAN DEFAULT FALSE,
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP
);
```

### Materialized Views for Fast Searches

```sql
-- Searchable view with all enrichment data
CREATE MATERIALIZED VIEW stations_searchable AS
SELECT
  s.id,
  s.ois_number,
  s.station_name,
  s.google_name,
  s.address,
  s.county,
  s.geog,
  s.phone_csv,
  s.google_phone,
  s.website,
  s.hours_display,
  s.rating,
  s.user_ratings_total,
  s.inspection_types,
  s.google_types,
  s.certifications,
  s.specializations,
  s.has_weekend_hours,
  s.has_evening_hours,
  s.business_status,

  -- Join emissions data
  e.required as emissions_required,
  e.emissions_type,

  -- Computed fields
  CASE
    WHEN s.rating IS NULL THEN 0.0
    ELSE s.data_quality_score
  END as quality_score,

  -- Full-text search vector
  to_tsvector('english',
    s.station_name || ' ' ||
    COALESCE(s.google_name, '') || ' ' ||
    COALESCE(s.address, '') || ' ' ||
    s.county
  ) as search_vector

FROM stations s
LEFT JOIN emissions_requirements e ON s.county = e.county
WHERE s.business_status != 'CLOSED_PERMANENTLY' OR s.business_status IS NULL;

-- Index for fast full-text search
CREATE INDEX idx_stations_searchable_fts ON stations_searchable USING GIN(search_vector);

-- Refresh strategy (run nightly)
CREATE OR REPLACE FUNCTION refresh_stations_searchable()
RETURNS void AS $$
BEGIN
  REFRESH MATERIALIZED VIEW CONCURRENTLY stations_searchable;
END;
$$ LANGUAGE plpgsql;
```

---

## 💰 Cost Breakdown & Timeline

### Phase 1: Automated Enrichment
| Task | Coverage | Cost | Time |
|------|----------|------|------|
| CSV Import | 12,627 | $0 | 30 min |
| Emissions Lookup | 12,627 | $0 | 5 min |
| Inspection Types Conversion | 12,627 | $0 | 5 min |
| Business Type Inference | 12,627 | $0 | 10 min |
| Geocoding (Google) | 12,627 | ~$63 | 2 hours |
| **Phase 1 Total** | **12,627** | **~$63** | **3 hours** |

### Phase 2: Google Places Enrichment
| Task | Coverage | Cost per Station | Total Cost |
|------|----------|------------------|------------|
| Text Search | 12,627 | $0.032 | $404 |
| Place Details | 12,627 | $0.011 | $139 |
| **Phase 2 Total** | **12,627** | **$0.043** | **~$543** |

**Expected Match Rate:** 85-90% (10,733-11,364 stations matched)

### Phase 3: Web Search Enrichment (Optional/Selective)
| Task | Coverage | Cost | Time |
|------|----------|------|------|
| Certification hunting (top 1,000) | 1,000 | $0 | 30-50 hours |
| Gap filling (unmatched ~15%) | 1,894 | $0 | 20-30 hours |
| **Phase 3 Total** | **~2,894** | **$0** | **50-80 hours** |

### Grand Total
| | Cost | Time |
|---|------|------|
| **API Costs** | **~$606** | **~6 hours** (automated) |
| **Manual Work** | **$0** | **50-80 hours** (optional, can be deferred) |

**Note:** Actual costs will be confirmed by running the test on 13 sample stations first.

---

## 🚀 Implementation Roadmap

### Week 1: Testing & Validation
- [ ] Set up Google Places API key
- [ ] Run test enrichment on 13 sample stations
- [ ] Validate matching algorithm accuracy
- [ ] Calculate actual per-station cost
- [ ] Review and approve budget
- [ ] Adjust matching thresholds if needed

### Week 2: Phase 1 Automated Enrichment
- [ ] Set up Supabase database
- [ ] Create all tables and indexes
- [ ] Import CSV data to stations table
- [ ] Run emissions lookup enrichment
- [ ] Convert inspection type booleans to arrays
- [ ] Infer business types from names
- [ ] Geocode all addresses
- [ ] Validate data quality (spot check 100 random stations)

### Week 3-4: Phase 2 Google Places Enrichment
- [ ] Set up batch processing script
- [ ] Process first 1,000 stations (pilot)
- [ ] Review pilot results and adjust
- [ ] Process remaining 11,627 stations in batches
- [ ] Monitor match rates and costs
- [ ] Handle errors and retries
- [ ] Build review queue for unmatched stations

### Week 5-6: Phase 2 Validation & Optimization
- [ ] Validate enriched data (sample 200 stations)
- [ ] Fix common matching errors
- [ ] Re-process failed matches
- [ ] Compute data quality scores
- [ ] Build materialized views
- [ ] Optimize database indexes

### Week 7+: Phase 3 Selective Enrichment (Optional)
- [ ] Export top 1,000 stations by review count
- [ ] Hunt for certifications (AAA, ASE, BBB)
- [ ] Research unmatched stations
- [ ] Update database with findings
- [ ] Build owner claim workflow (for future enrichment)

---

## 📊 Success Metrics

### Data Completeness Targets

| Field | Target | Method |
|-------|--------|--------|
| Emissions clarity | 100% | Automated county lookup |
| Inspection types | 100% | CSV data conversion |
| Latitude/Longitude | 95%+ | Google Geocoding |
| Google Place match | 85-90% | Places API Text Search |
| Business hours | 75-80% | Place Details API |
| Phone (validated) | 80-85% | Place Details API |
| Website | 55-65% | Place Details API |
| Rating/reviews | 75-80% | Place Details API |
| Certifications | 30-40% | Manual web search (top stations) |

### User Impact Metrics

After enrichment, users will be able to:
- ✅ Search by location (near me, zip, county) with distance
- ✅ Filter by inspection type (cars, motorcycles, trucks, trailers)
- ✅ Filter by emissions requirement (required vs not required)
- ✅ See business hours before visiting
- ✅ See ratings and reviews for trust signals
- ✅ Find weekend/evening hours
- ✅ Visit websites or get directions via Google Maps
- ✅ Call verified phone numbers

---

## 🎯 Next Steps

**Immediate Actions:**

1. **Get Google Places API Key**
   - Create project at console.cloud.google.com
   - Enable "Places API (New)"
   - Generate API key
   - Set billing limits ($700 max)

2. **Run Cost Test**
   ```bash
   pip install -r requirements.txt
   export GOOGLE_PLACES_API_KEY="your-key"
   python3 test_google_places_enrichment.py
   ```

3. **Review Test Results**
   - Check match accuracy
   - Validate cost projections
   - Adjust matching thresholds if needed

4. **Approve Budget**
   - Review projected total cost
   - Confirm Phase 1, 2, 3 priorities
   - Set timeline expectations

5. **Begin Implementation**
   - Set up Supabase database
   - Run Phase 1 automated enrichment
   - Launch Phase 2 batch processing

---

## ❓ Open Questions

1. **Geocoding Choice:**
   - Google Geocoding API (~$63) - faster, more reliable
   - Free service (Nominatim, etc.) - slower, less reliable
   - **Recommendation:** Use Google for consistency

2. **Phase 3 Priority:**
   - Should we do certification hunting for top 1,000 stations immediately?
   - Or defer to post-launch and build owner claim workflow first?
   - **Recommendation:** Defer to Phase 4, focus on Google enrichment first

3. **Unmatched Stations Handling:**
   - Manual web search for all ~1,800 unmatched stations?
   - Or mark as "unverified" and crowdsource corrections?
   - **Recommendation:** Manual search for top 200 by county population, rest marked unverified

4. **Review Snippet Strategy:**
   - Pull top 1-3 reviews per station for snippets?
   - Cost: Additional API calls (~$0.005 per station = $63)
   - **Recommendation:** Skip for MVP, pull reviews on-demand for listing detail pages

---

**This plan is ready to execute once API cost testing is complete and approved!**
