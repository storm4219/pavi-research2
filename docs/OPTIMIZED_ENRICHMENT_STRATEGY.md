# Optimized Enrichment Strategy (80/20 Analysis)
**Project:** PAvehicleinspections.com Data Enrichment
**Date:** November 14, 2025
**Focus:** Maximum value with minimum effort

---

## 🎯 The 20% That Delivers 80% of Value

### Analysis: Research Activity ROI

Based on researching 20 stations, here's what took minimal effort but delivered maximum value:

| Research Activity | Success Rate | Time per Station | Value to User | ROI Score |
|-------------------|--------------|------------------|---------------|-----------|
| **🟢 Google Business Hours** | 90% | 30 seconds | Critical | ⭐⭐⭐⭐⭐ 10/10 |
| **🟢 County → Emissions Lookup** | 100% | 0 seconds (automated) | Critical | ⭐⭐⭐⭐⭐ 10/10 |
| **🟢 Phone Validation** | 95% | 20 seconds | High | ⭐⭐⭐⭐⭐ 9/10 |
| **🟢 Website Discovery** | 70% | 1 minute | High | ⭐⭐⭐⭐ 8/10 |
| **🟢 Business Type** | 85% | 30 seconds | Medium | ⭐⭐⭐⭐ 7/10 |
| **🟢 Google Reviews (existing)** | 100% | 0 seconds | High | ⭐⭐⭐⭐⭐ 10/10 |
| **🟡 Certifications** | 55% | 2 minutes | Medium | ⭐⭐⭐ 5/10 |
| **🟡 Years in Business** | 60% | 2 minutes | Medium | ⭐⭐⭐ 5/10 |
| **🟡 Payment Methods** | 50% | 1 minute | Low | ⭐⭐ 4/10 |
| **🔴 Exact Pricing** | 20% | 3 minutes | Low | ⭐ 2/10 |
| **🔴 Wait Times** | 15% | 3 minutes | Low | ⭐ 2/10 |
| **🔴 Amenities Detail** | 40% | 2 minutes | Low | ⭐⭐ 3/10 |

### 🏆 THE WINNING 20% (Focus Here)

**5 High-ROI Activities** that take ~2-3 minutes per station:

1. **Google Business Hours** (30 sec) - 90% success, critical for "convenience"
2. **County → Emissions** (0 sec) - 100% automated, critical for "clarity"
3. **Phone Validation** (20 sec) - 95% success, prevents user frustration
4. **Website Discovery** (1 min) - 70% success, provides owner contact
5. **Business Type Identification** (30 sec) - 85% success, useful for trust signals

**Total Time:** ~2.5 minutes per station × 5,915 stations = **246 hours**
**Agent Cost at $0.50/station:** ~$2,957

**Value Delivered:**
- ✅ Addresses ICP pain points: convenience (hours), clarity (emissions), trust (validation)
- ✅ Enables owner outreach (validated contact info)
- ✅ Provides filtering capabilities (emissions, business type)
- ✅ High success rate (85%+ average)

### ❌ THE INEFFICIENT 80% (Skip or Defer)

**Activities to skip at scale:**
- Exact pricing research (20% success, 3 min each) → Let owners add when they claim
- Wait time estimation (15% success) → Too unreliable
- Detailed amenities (40% success) → Low user priority based on ICP

---

## 🏷️ Tag-Based Schema for Searchability

### Philosophy: Controlled Vocabularies

**Problem:** Free-text fields like "inspects motorcycles, cars, and trucks" aren't searchable
**Solution:** Standardized tag arrays that enable filtering

### Core Taggable Fields

#### 1. **Inspection Types** (Already boolean, convert to tags)

```json
{
  "inspection_types": [
    "cars",
    "motorcycles",
    "trailers",
    "medium_trucks",
    "heavy_trucks",
    "heavy_trailers",
    "enhanced_vehicles"
  ]
}
```

**Search Example:** "Show me stations that do motorcycle inspections in Philadelphia"
```sql
SELECT * FROM stations
WHERE 'motorcycles' = ANY(inspection_types)
AND county = 'PHILADELPHIA';
```

**Tag Source:** PennDOT data (100% reliable)

---

#### 2. **Emissions Testing** (Standardized enum)

```json
{
  "emissions_status": "required" | "not_required" | "available",
  "emissions_types": [
    "obd2",           // OBD-II computer diagnostic
    "visual_check",   // Anti-tampering visual inspection
    "gas_cap_test",   // Fuel system pressure test
    "enhanced"        // Enhanced emissions (urban areas)
  ]
}
```

**Search Example:** "Stations with OBD-II testing in Lehigh County"
```sql
SELECT * FROM stations
WHERE 'obd2' = ANY(emissions_types)
AND county = 'LEHIGH';
```

**Tag Source:**
- `emissions_status`: County lookup (100% automated)
- `emissions_types`: Research or inference based on county (90% automated)

---

#### 3. **Service Categories** (Standardized tags)

```json
{
  "service_categories": [
    "inspection_only",      // Only does inspections
    "general_repair",       // Full-service auto repair
    "oil_change",          // Oil change services
    "tires",               // Tire sales and service
    "brakes",              // Brake specialists
    "exhaust",             // Muffler/exhaust work
    "alignment",           // Wheel alignment
    "body_shop",           // Collision/body repair
    "diagnostics",         // Engine diagnostics
    "transmission",        // Transmission service
    "ac_heating",          // A/C and heating repair
    "electrical",          // Electrical/alternator work
    "towing",              // Towing services
    "dealer_service",      // Car dealership service dept
    "fleet_service"        // Commercial fleet services
  ]
}
```

**Search Example:** "Stations that do tires and alignment near me"
```sql
SELECT * FROM stations
WHERE 'tires' = ANY(service_categories)
AND 'alignment' = ANY(service_categories)
AND ST_Distance(location, user_location) < 10; -- within 10 miles
```

**Tag Source:**
- Website/business description parsing (70% success)
- Business name inference ("Mike's Tire Shop" → add "tires")
- Owner-submitted when claiming

---

#### 4. **Certifications** (Standardized badges)

```json
{
  "certifications": [
    "ase_certified",        // ASE (Automotive Service Excellence)
    "aaa_approved",         // AAA Approved Auto Repair
    "napa_autocare",        // NAPA AutoCare Center
    "bbb_accredited",       // Better Business Bureau accredited
    "carfax_top_rated",     // CarFax Top Rated
    "master_technician",    // ASE Master Technician on staff
    "enhanced_inspection",  // PennDOT Enhanced Inspection certified
    "dealer_certified",     // Manufacturer-certified (e.g., Honda Certified)
    "emission_certified"    // EPA/state emissions certification
  ]
}
```

**Search Example:** "AAA approved stations with ASE certified mechanics"
```sql
SELECT * FROM stations
WHERE 'aaa_approved' = ANY(certifications)
AND 'ase_certified' = ANY(certifications);
```

**Tag Source:** Research from website/directories (55% success)

---

#### 5. **Business Attributes** (Trust signals)

```json
{
  "business_attributes": [
    "family_owned",         // Family-owned business
    "locally_owned",        // Local vs corporate chain
    "woman_owned",          // Woman-owned business
    "veteran_owned",        // Veteran-owned
    "multi_generational",   // Multi-generation family business
    "chain_location",       // Part of chain (Midas, Meineke, etc.)
    "dealership"           // Car dealership service department
  ]
}
```

**Search Example:** "Family-owned shops"
```sql
SELECT * FROM stations
WHERE 'family_owned' = ANY(business_attributes);
```

**Tag Source:** Research from website/about pages (60% success)

---

#### 6. **Specializations** (Vehicle expertise)

```json
{
  "specializations": [
    "import_vehicles",      // Foreign/import specialist
    "domestic_vehicles",    // American vehicles
    "european_vehicles",    // European brands (BMW, Mercedes, etc.)
    "asian_vehicles",       // Asian brands (Honda, Toyota, etc.)
    "diesel_vehicles",      // Diesel engine specialist
    "hybrid_electric",      // Hybrid and electric vehicles
    "classic_cars",         // Classic/antique vehicles
    "commercial_trucks",    // Heavy duty commercial
    "motorcycles",          // Motorcycle specialist
    "rvs_campers",         // RV and camper service
    "performance_tuning",   // Performance/racing modifications
    "luxury_vehicles"       // High-end luxury brands
  ]
}
```

**Search Example:** "Diesel truck specialists in Western PA"
```sql
SELECT * FROM stations
WHERE 'diesel_vehicles' = ANY(specializations)
AND 'commercial_trucks' = ANY(specializations)
AND county IN ('ALLEGHENY', 'WESTMORELAND', 'WASHINGTON');
```

**Tag Source:** Business name/description parsing (50% success)

---

#### 7. **Amenities** (Customer convenience)

```json
{
  "amenities": [
    "waiting_room",         // Customer waiting area
    "wifi",                 // Free WiFi
    "coffee",               // Complimentary coffee/beverages
    "shuttle_service",      // Free local shuttle
    "loaner_vehicles",      // Loaner car available
    "after_hours_dropoff",  // Early bird drop-off
    "online_booking",       // Online appointment scheduling
    "same_day_service",     // Same-day inspection available
    "weekend_hours",        // Saturday/Sunday hours
    "evening_hours",        // Open past 6pm
    "spanish_speaking",     // Spanish language support
    "wheelchair_accessible", // ADA accessible
    "covered_parking"       // Covered waiting area
  ]
}
```

**Search Example:** "Stations with Saturday hours and online booking"
```sql
SELECT * FROM stations
WHERE 'weekend_hours' = ANY(amenities)
AND 'online_booking' = ANY(amenities);
```

**Tag Source:**
- `weekend_hours`: Derived from hours_of_operation (100% automated if hours known)
- `online_booking`: Website research (30% success)
- Others: Low priority, owner-submitted

---

#### 8. **Payment Methods** (Standardized)

```json
{
  "payment_methods": [
    "cash",
    "check",
    "visa",
    "mastercard",
    "amex",
    "discover",
    "debit_cards",
    "apple_pay",
    "google_pay",
    "financing_available",
    "fleet_accounts"
  ]
}
```

**Search Example:** "Stations that accept Apple Pay"
```sql
SELECT * FROM stations
WHERE 'apple_pay' = ANY(payment_methods);
```

**Tag Source:** Research (50% success), but LOW PRIORITY for initial enrichment

---

## 📊 Optimized Database Schema

### Core Tables

```sql
-- Main stations table
CREATE TABLE stations (
  id SERIAL PRIMARY KEY,

  -- Core Identity (from PennDOT)
  name VARCHAR(255) NOT NULL,
  ois_number VARCHAR(50) UNIQUE NOT NULL,
  county VARCHAR(50) NOT NULL,
  city VARCHAR(100),
  zip_code VARCHAR(10),

  -- Location
  address TEXT,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  location GEOGRAPHY(POINT), -- PostGIS for geo searches

  -- Contact (HIGH PRIORITY - enriched)
  phone VARCHAR(20),
  phone_verified BOOLEAN DEFAULT FALSE,
  website TEXT,
  website_verified BOOLEAN DEFAULT FALSE,

  -- Hours (HIGH PRIORITY - enriched)
  hours_json JSONB, -- Structured hours data
  hours_display VARCHAR(255), -- Human-readable

  -- Ratings (Already have)
  google_rating DECIMAL(2,1),
  google_reviews_count INTEGER,
  google_place_id VARCHAR(255),

  -- Timestamps
  data_verified_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Tag tables (normalized for efficient searching)
CREATE TABLE inspection_type_tags (
  id SERIAL PRIMARY KEY,
  tag_name VARCHAR(50) UNIQUE NOT NULL, -- 'cars', 'motorcycles', etc.
  display_name VARCHAR(100), -- 'Passenger Cars', 'Motorcycles'
  description TEXT
);

CREATE TABLE station_inspection_types (
  station_id INTEGER REFERENCES stations(id) ON DELETE CASCADE,
  tag_id INTEGER REFERENCES inspection_type_tags(id),
  PRIMARY KEY (station_id, tag_id)
);

-- Same pattern for other tag types
CREATE TABLE service_category_tags (
  id SERIAL PRIMARY KEY,
  tag_name VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  icon VARCHAR(50), -- For UI display
  priority INTEGER DEFAULT 0 -- For sorting
);

CREATE TABLE station_service_categories (
  station_id INTEGER REFERENCES stations(id) ON DELETE CASCADE,
  tag_id INTEGER REFERENCES service_category_tags(id),
  PRIMARY KEY (station_id, tag_id)
);

CREATE TABLE certification_tags (
  id SERIAL PRIMARY KEY,
  tag_name VARCHAR(50) UNIQUE NOT NULL,
  display_name VARCHAR(100),
  logo_url TEXT,
  verification_required BOOLEAN DEFAULT FALSE
);

CREATE TABLE station_certifications (
  station_id INTEGER REFERENCES stations(id) ON DELETE CASCADE,
  tag_id INTEGER REFERENCES certification_tags(id),
  verified BOOLEAN DEFAULT FALSE,
  verified_at TIMESTAMP,
  PRIMARY KEY (station_id, tag_id)
);

-- Emissions data (HIGH PRIORITY - automated)
CREATE TABLE emissions_requirements (
  county VARCHAR(50) PRIMARY KEY,
  required BOOLEAN NOT NULL,
  enhanced_area BOOLEAN DEFAULT FALSE,
  testing_types VARCHAR[] -- array: ['obd2', 'visual_check', 'gas_cap_test']
);

-- Denormalized view for fast searches
CREATE MATERIALIZED VIEW stations_searchable AS
SELECT
  s.id,
  s.name,
  s.ois_number,
  s.county,
  s.city,
  s.zip_code,
  s.location,
  s.phone,
  s.website,
  s.hours_display,
  s.google_rating,
  s.google_reviews_count,

  -- Aggregated tags as arrays for fast filtering
  ARRAY_AGG(DISTINCT it.tag_name) FILTER (WHERE it.tag_name IS NOT NULL) as inspection_types,
  ARRAY_AGG(DISTINCT sc.tag_name) FILTER (WHERE sc.tag_name IS NOT NULL) as service_categories,
  ARRAY_AGG(DISTINCT ct.tag_name) FILTER (WHERE ct.tag_name IS NOT NULL) as certifications,

  -- Emissions from lookup
  er.required as emissions_required,
  er.testing_types as emissions_types,

  -- Full text search vector
  to_tsvector('english',
    s.name || ' ' ||
    COALESCE(s.city, '') || ' ' ||
    COALESCE(array_to_string(ARRAY_AGG(DISTINCT sc.display_name), ' '), '')
  ) as search_vector

FROM stations s
LEFT JOIN station_inspection_types sit ON s.id = sit.station_id
LEFT JOIN inspection_type_tags it ON sit.tag_id = it.id
LEFT JOIN station_service_categories ssc ON s.id = ssc.station_id
LEFT JOIN service_category_tags sc ON ssc.tag_id = sc.id
LEFT JOIN station_certifications stc ON s.id = stc.station_id
LEFT JOIN certification_tags ct ON stc.tag_id = ct.id
LEFT JOIN emissions_requirements er ON s.county = er.county
GROUP BY s.id, er.required, er.testing_types;

-- Index for fast searches
CREATE INDEX idx_stations_location ON stations USING GIST(location);
CREATE INDEX idx_stations_county ON stations(county);
CREATE INDEX idx_stations_inspection_types ON station_inspection_types(tag_id);
CREATE INDEX idx_stations_search_vector ON stations_searchable USING GIN(search_vector);
```

---

## 🚀 Implementation Plan (80/20 Approach)

### Phase 1: Automated Enrichment (Week 1)
**Effort:** 8 hours of development
**Cost:** $0 (automated)
**Coverage:** 5,915 stations (100%)

```python
# 1. Emissions testing tags (100% automated)
EMISSIONS_REQUIRED_COUNTIES = [
    "ALLEGHENY", "ARMSTRONG", "BEAVER", "BERKS", "BLAIR",
    # ... full list
]

def enrich_emissions(station):
    county = station['county'].strip().upper()

    if county in EMISSIONS_REQUIRED_COUNTIES:
        station['emissions_status'] = 'required'
        # Most counties use OBD-II + visual
        station['emissions_types'] = ['obd2', 'visual_check', 'gas_cap_test']
    else:
        station['emissions_status'] = 'not_required'
        station['emissions_types'] = ['visual_check']  # Safety still checks emissions equipment

    return station

# 2. Inspection type tags (100% from PennDOT booleans)
def convert_inspection_types(station):
    tags = []
    if station['inspects_cars']: tags.append('cars')
    if station['inspects_motorcycles']: tags.append('motorcycles')
    if station['inspects_trailers']: tags.append('trailers')
    if station['inspects_medium_trucks']: tags.append('medium_trucks')
    if station['inspects_heavy_trucks']: tags.append('heavy_trucks')
    if station['inspects_heavy_trailers']: tags.append('heavy_trailers')
    if station['enhanced']: tags.append('enhanced_vehicles')

    station['inspection_types'] = tags
    return station

# 3. Business type inference (85% from name/Google data)
def infer_business_type(station):
    name_lower = station['name'].lower()

    # Chain detection
    chains = ['jiffy lube', 'midas', 'meineke', 'pep boys', 'firestone',
              'goodyear', 'valvoline', 'monro', 'aamco']
    if any(chain in name_lower for chain in chains):
        station['business_attributes'] = ['chain_location']
        return station

    # Dealership detection
    dealership_keywords = ['ford', 'chevrolet', 'toyota', 'honda', 'nissan',
                           'hyundai', 'kia', 'subaru', 'mazda', 'volkswagen',
                           'bmw', 'mercedes', 'audi', 'lexus', 'acura']
    if any(keyword in name_lower for keyword in dealership_keywords):
        station['business_attributes'] = ['dealership']
        return station

    # Default to independent/locally owned
    station['business_attributes'] = ['locally_owned']
    return station

# Run automated enrichment on all 5,915 stations
for station in all_stations:
    station = enrich_emissions(station)
    station = convert_inspection_types(station)
    station = infer_business_type(station)
```

**Output:** All 5,915 stations now have:
- ✅ `emissions_status` and `emissions_types` tags
- ✅ `inspection_types` array
- ✅ Basic `business_attributes` tags

---

### Phase 2: High-ROI Agent Enrichment (Weeks 2-6)
**Effort:** 246 hours (agent processing)
**Cost:** ~$2,957 (5,915 stations @ $0.50 each)
**Coverage:** 5,915 stations (100%)

**Focus on 5 high-value activities:**

```python
# Agent prompt template (2-3 minutes per station)
ENRICHMENT_PROMPT = """
Research {business_name} at {address}, {city}, PA {zip}
Phone: {phone}
Google Place ID: {google_place_id}

Your task: Find the following information (spend max 3 minutes):

1. HOURS OF OPERATION (30 sec - HIGH PRIORITY)
   - Check Google Business Profile first
   - Format: Mon-Fri 8:00-17:00, Sat 8:00-12:00, Sun closed
   - Return structured JSON: {{"mon": "8:00-17:00", ...}}

2. PHONE VALIDATION (20 sec - HIGH PRIORITY)
   - Verify phone number {phone} is correct
   - Find alternate/updated number if wrong
   - Return: {{"phone": "(123) 456-7890", "verified": true}}

3. WEBSITE (1 min - HIGH PRIORITY)
   - Find official website if not already known: {website}
   - Verify URL is active (not 404)
   - Return: {{"website": "https://...", "verified": true}}

4. BUSINESS TYPE (30 sec - MEDIUM PRIORITY)
   - Determine: family_owned, chain, dealership, or independent
   - Look for "family owned" on website/about page
   - Return: {{"business_attributes": ["family_owned"]}}

5. QUICK SERVICE SCAN (30 sec - MEDIUM PRIORITY)
   - From business name or website, identify 3-5 primary services
   - Match to tags: general_repair, tires, brakes, exhaust, oil_change, body_shop, etc.
   - Return: {{"service_categories": ["general_repair", "tires", "brakes"]}}

SKIP (not worth the time):
- ❌ Exact pricing
- ❌ Wait times
- ❌ Detailed amenities

Return JSON only.
"""

# Process in batches
async def enrich_batch(stations_batch):
    tasks = [agent_research(station, ENRICHMENT_PROMPT) for station in stations_batch]
    return await asyncio.gather(*tasks)

# Run 100 stations at a time
batch_size = 100
for i in range(0, len(all_stations), batch_size):
    batch = all_stations[i:i+batch_size]
    enriched = await enrich_batch(batch)
    save_to_database(enriched)
    print(f"Completed {i+batch_size}/{len(all_stations)} stations")
```

**Expected Success Rates:**
- Hours: 90% (5,324 stations)
- Phone validated: 95% (5,619 stations)
- Website found: 70% (4,141 stations)
- Business type: 85% (5,028 stations)
- Service categories: 70% (4,141 stations)

---

### Phase 3: Owner Self-Service (Ongoing)
**Effort:** Build claiming workflow (40 hours dev)
**Cost:** $0 ongoing (owner-submitted)
**Coverage:** Grows over time

**Owner Dashboard:**
```javascript
// When owner claims listing, they can add:
{
  "certifications": ["ase_certified", "aaa_approved"], // Select from dropdown
  "specializations": ["european_vehicles", "diesel_vehicles"],
  "amenities": ["wifi", "shuttle_service", "online_booking"],
  "payment_methods": ["visa", "mastercard", "cash", "financing_available"],
  "additional_services": ["towing", "body_shop"],
  "pricing_notes": "State inspection: $39.99, Emissions: $49.99",
  "description": "Family-owned since 1985..."
}
```

**Verification:**
- Certifications require proof upload (ASE certificate, AAA letter, etc.)
- Admin approves before going live
- Verified claims get "Owner Verified" badge

---

## 💰 Cost & Timeline Summary

### Total Investment

| Phase | Timeline | Cost | Coverage | Value |
|-------|----------|------|----------|-------|
| **Phase 1: Automated** | Week 1 | $0 | 100% (5,915) | ⭐⭐⭐⭐⭐ |
| **Phase 2: Agent Research** | Weeks 2-6 | $2,957 | 100% (5,915) | ⭐⭐⭐⭐⭐ |
| **Phase 3: Owner Self-Service** | Week 7+ | $0 ongoing | Growing | ⭐⭐⭐⭐ |
| **TOTAL** | 7-8 weeks | **$2,957** | **100%** | **🎯 Maximum ROI** |

### ROI Breakdown

**Investment:** $2,957
**Deliverables:**
- ✅ 100% coverage of emissions testing clarity
- ✅ 90% coverage of hours of operation (5,324 stations)
- ✅ 95% phone validation (5,619 stations)
- ✅ 70% website discovery (4,141 stations)
- ✅ Searchable tags for all key user filters

**User Impact:**
- Can search "motorcycle inspections in Philadelphia" → instant results
- Can search "Saturday hours + emissions testing" → filtered list
- Can search "family-owned + ASE certified" → trust signals
- Addresses all 3 core ICP pain points: trust, convenience, clarity

**SEO Impact:**
- Structured data for hours → better local pack ranking
- Rich snippets with tags (motorcycles, weekend hours, etc.)
- Unique content vs competitors (no one else has this detail)

**Conversion Impact:**
- Estimated 15-25% lift from richer listings
- Users find exactly what they need faster
- Lower bounce rates, higher engagement

---

## 🎬 Next Steps

### Week 1: Automated Enrichment
1. ✅ Review this strategy
2. ⬜ Create emissions lookup table (EMISSIONS_REQUIRED_COUNTIES)
3. ⬜ Write automated enrichment scripts (emissions, inspection types, business type)
4. ⬜ Run on all 5,915 stations
5. ⬜ QA 100 random stations for accuracy

### Week 2: Agent Setup
1. ⬜ Finalize agent prompt template
2. ⬜ Set up batch processing (100 stations at a time)
3. ⬜ Create quality validation rules
4. ⬜ Run pilot on 500 stations (1 county)
5. ⬜ Review results and adjust prompt

### Weeks 3-6: Full Enrichment
1. ⬜ Process all 5,915 stations in batches
2. ⬜ Monitor success rates per field
3. ⬜ Flag low-quality enrichment for manual review
4. ⬜ Build searchable tag system in database
5. ⬜ Update frontend to support tag-based filtering

### Week 7+: Owner Platform
1. ⬜ Build owner claiming workflow
2. ⬜ Create admin verification dashboard
3. ⬜ Launch beta with 50 owners
4. ⬜ Iterate based on feedback

---

## 🔍 Example User Searches Enabled

With this tag-based approach, users can now search:

```sql
-- Search 1: "Motorcycle inspections open on Saturday in Philadelphia"
SELECT * FROM stations_searchable
WHERE 'motorcycles' = ANY(inspection_types)
AND 'weekend_hours' = ANY(amenities)
AND county = 'PHILADELPHIA';

-- Search 2: "Family-owned shops that do emissions testing near me"
SELECT * FROM stations_searchable
WHERE 'family_owned' = ANY(business_attributes)
AND emissions_required = TRUE
AND ST_DWithin(location, ST_MakePoint(-75.1652, 39.9526)::geography, 8000); -- 5 miles

-- Search 3: "ASE certified, AAA approved shops with tires and brakes"
SELECT * FROM stations_searchable
WHERE 'ase_certified' = ANY(certifications)
AND 'aaa_approved' = ANY(certifications)
AND 'tires' = ANY(service_categories)
AND 'brakes' = ANY(service_categories);

-- Search 4: "Diesel truck specialists in Western PA"
SELECT * FROM stations_searchable
WHERE 'diesel_vehicles' = ANY(specializations)
AND 'commercial_trucks' = ANY(inspection_types)
AND county IN ('ALLEGHENY', 'WESTMORELAND', 'WASHINGTON', 'BEAVER');
```

---

## ✅ Success Metrics

After enrichment, measure:

1. **Data Completeness**
   - % stations with hours: Target 90%+
   - % stations with verified phone: Target 95%+
   - % stations with website: Target 70%+
   - % stations with service tags: Target 70%+

2. **Search Usage**
   - % searches using tag filters (target 40%+)
   - Most popular tag combinations
   - Zero-result searches (should decrease)

3. **User Behavior**
   - Click-through rate on enriched vs basic listings (expect 2-3x lift)
   - Bounce rate (expect 15-25% decrease)
   - Time on site (expect increase)

4. **Owner Engagement**
   - % claimed listings (target 20% in year 1)
   - % owners adding additional tags
   - Owner satisfaction with data accuracy

---

**This 80/20 approach delivers maximum value ($2,957) with complete coverage (5,915 stations) while building a foundation for owner-contributed enrichment over time.**
