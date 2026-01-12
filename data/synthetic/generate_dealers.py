"""
STIHL Dealer Network Generator
Generates ~100 realistic dealers across 5 US regions
"""

import csv
import random
from pathlib import Path
from datetime import datetime

# Regional configuration
REGIONS = {
    "Southwest": {
        "states": ["TX", "AZ", "NM", "OK"],
        "weight": 0.25,  # 25% of dealers
        "cities": {
            "TX": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth", "El Paso", "Lubbock", "Amarillo"],
            "AZ": ["Phoenix", "Tucson", "Mesa", "Scottsdale", "Flagstaff"],
            "NM": ["Albuquerque", "Santa Fe", "Las Cruces"],
            "OK": ["Oklahoma City", "Tulsa", "Norman"]
        }
    },
    "Southeast": {
        "states": ["FL", "GA", "NC", "SC", "AL"],
        "weight": 0.22,  # 22% of dealers
        "cities": {
            "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee", "Fort Lauderdale"],
            "GA": ["Atlanta", "Savannah", "Augusta", "Athens"],
            "NC": ["Charlotte", "Raleigh", "Asheville", "Greensboro"],
            "SC": ["Charleston", "Columbia", "Greenville"],
            "AL": ["Birmingham", "Mobile", "Montgomery", "Huntsville"]
        }
    },
    "Midwest": {
        "states": ["OH", "IN", "IL", "MI", "WI"],
        "weight": 0.20,  # 20% of dealers
        "cities": {
            "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"],
            "IN": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend"],
            "IL": ["Chicago", "Springfield", "Peoria", "Rockford"],
            "MI": ["Detroit", "Grand Rapids", "Ann Arbor", "Lansing"],
            "WI": ["Milwaukee", "Madison", "Green Bay", "Appleton"]
        }
    },
    "Northeast": {
        "states": ["NY", "PA", "NJ", "MA", "CT"],
        "weight": 0.18,  # 18% of dealers
        "cities": {
            "NY": ["New York", "Buffalo", "Rochester", "Albany", "Syracuse"],
            "PA": ["Philadelphia", "Pittsburgh", "Harrisburg", "Allentown"],
            "NJ": ["Newark", "Jersey City", "Trenton", "Princeton"],
            "MA": ["Boston", "Worcester", "Springfield", "Cambridge"],
            "CT": ["Hartford", "New Haven", "Stamford", "Bridgeport"]
        }
    },
    "West": {
        "states": ["CA", "WA", "OR", "CO"],
        "weight": 0.15,  # 15% of dealers
        "cities": {
            "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "Fresno", "Oakland"],
            "WA": ["Seattle", "Spokane", "Tacoma", "Olympia"],
            "OR": ["Portland", "Eugene", "Salem", "Bend"],
            "CO": ["Denver", "Colorado Springs", "Boulder", "Fort Collins"]
        }
    }
}

# Dealer name patterns
DEALER_NAME_PATTERNS = [
    "{city} Power Equipment",
    "{city} Outdoor Power",
    "{city} Equipment Sales",
    "{state} Power Equipment",
    "{city} Lawn & Garden",
    "{name}'s Equipment",
    "{name}'s Power Equipment",
    "{city} Small Engine",
    "Pro Equipment {city}",
    "{city} Chainsaw & More",
    "{state} Equipment Co.",
    "{city} Rental & Sales",
    "All Seasons {city}",
    "{city} Hardware & Power",
    "Premier Equipment {city}"
]

# Common last names for dealer owners
OWNER_NAMES = [
    "Johnson", "Smith", "Williams", "Brown", "Anderson", "Miller", "Davis", 
    "Wilson", "Taylor", "Thomas", "Jackson", "Martin", "Garcia", "Martinez",
    "Robinson", "Clark", "Lewis", "Walker", "Hall", "Young", "Allen", "King",
    "Wright", "Scott", "Green", "Baker", "Adams", "Nelson", "Hill", "Campbell"
]

# Dealer types with weights
DEALER_TYPES = [
    ("Authorized Dealer", 0.70),
    ("Premium Dealer", 0.20),
    ("Service Center", 0.10)
]


def generate_dealer_name(city: str, state: str) -> str:
    """Generate a unique dealer name."""
    pattern = random.choice(DEALER_NAME_PATTERNS)
    name = random.choice(OWNER_NAMES)
    return pattern.format(city=city, state=state, name=name)


def select_dealer_type() -> str:
    """Select a dealer type based on weights."""
    rand = random.random()
    cumulative = 0
    for dealer_type, weight in DEALER_TYPES:
        cumulative += weight
        if rand <= cumulative:
            return dealer_type
    return "Authorized Dealer"


def generate_dealers(total_dealers: int = 100) -> list:
    """Generate dealer records."""
    dealers = []
    dealer_names_used = set()
    
    # Calculate dealers per region
    region_counts = {}
    remaining = total_dealers
    
    for region, config in REGIONS.items():
        if region == list(REGIONS.keys())[-1]:
            # Last region gets the remainder
            region_counts[region] = remaining
        else:
            count = int(total_dealers * config["weight"])
            region_counts[region] = count
            remaining -= count
    
    dealer_id = 1
    
    for region, config in REGIONS.items():
        count = region_counts[region]
        states = config["states"]
        cities_by_state = config["cities"]
        
        for _ in range(count):
            # Select state and city
            state = random.choice(states)
            city = random.choice(cities_by_state[state])
            
            # Generate unique dealer name
            attempts = 0
            while attempts < 10:
                name = generate_dealer_name(city, state)
                if name not in dealer_names_used:
                    dealer_names_used.add(name)
                    break
                attempts += 1
            
            # Generate dealer record
            dealer = {
                "dealer_id": f"DLR-{state}-{str(dealer_id).zfill(3)}",
                "dealer_name": name,
                "city": city,
                "state": state,
                "region": region,
                "dealer_type": select_dealer_type(),
                "year_established": random.randint(1985, 2020),
                "is_active": True
            }
            
            dealers.append(dealer)
            dealer_id += 1
    
    return dealers


def save_to_csv(dealers: list, output_file: Path):
    """Save dealers to CSV file."""
    fieldnames = [
        "dealer_id", "dealer_name", "city", "state", 
        "region", "dealer_type", "year_established", "is_active"
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dealers)


def main():
    """Generate and save dealers."""
    print("🏪 Generating STIHL Dealer Network...")
    
    dealers = generate_dealers(100)
    
    # Create output directory
    output_dir = Path(__file__).parent
    output_file = output_dir / "dealers.csv"
    
    # Save to CSV
    save_to_csv(dealers, output_file)
    
    # Print summary
    print(f"\n✅ Generated {len(dealers)} dealers")
    print("\nRegional breakdown:")
    
    regions = {}
    for d in dealers:
        region = d["region"]
        regions[region] = regions.get(region, 0) + 1
    
    for region, count in sorted(regions.items(), key=lambda x: -x[1]):
        print(f"   • {region}: {count} ({count}%)")
    
    print("\nDealer type breakdown:")
    types = {}
    for d in dealers:
        dtype = d["dealer_type"]
        types[dtype] = types.get(dtype, 0) + 1
    
    for dtype, count in sorted(types.items(), key=lambda x: -x[1]):
        print(f"   • {dtype}: {count}")
    
    print(f"\n📁 Saved to: {output_file}")
    
    return dealers


if __name__ == "__main__":
    main()
