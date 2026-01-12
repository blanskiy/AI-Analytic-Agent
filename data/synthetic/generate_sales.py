"""
STIHL Sales Transaction Generator
Generates ~500K realistic sales transactions with seasonal patterns and anomalies
"""

import csv
import json
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

# Date range
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)

# Seasonal weights by month
SEASONAL_WEIGHTS = {
    1: 0.6,   # January - slow
    2: 0.7,   # February
    3: 1.2,   # March - spring start
    4: 1.5,   # April - peak
    5: 1.5,   # May - peak
    6: 1.3,   # June
    7: 0.7,   # July - summer slow
    8: 0.7,   # August - summer slow
    9: 1.2,   # September - fall start
    10: 1.3,  # October
    11: 1.4,  # November - Black Friday
    12: 0.8   # December
}

# Regional weights
REGIONAL_WEIGHTS = {
    "Southwest": 0.25,
    "Southeast": 0.22,
    "Midwest": 0.20,
    "Northeast": 0.18,
    "West": 0.15
}

# Category popularity weights
CATEGORY_WEIGHTS = {
    "Chainsaws": 0.28,
    "Trimmers": 0.22,
    "Blowers": 0.20,
    "Hedge Trimmers": 0.10,
    "Lawn Mowers": 0.10,
    "Multi-System": 0.05,
    "Accessories": 0.05
}

# Customer types
CUSTOMER_TYPES = [
    ("Homeowner", 0.55),
    ("Professional", 0.30),
    ("Commercial", 0.15)
]

# Sales channels
SALES_CHANNELS = [
    ("In-Store", 0.70),
    ("Online", 0.20),
    ("Phone", 0.10)
]

# Anomalies to inject
ANOMALIES = {
    "hurricane_texas": {
        "start_date": datetime(2024, 6, 10),
        "end_date": datetime(2024, 6, 20),
        "region": "Southwest",
        "state": "TX",
        "category": "Chainsaws",
        "multiplier": 3.4  # 340% spike
    },
    "black_friday_2024": {
        "start_date": datetime(2024, 11, 25),
        "end_date": datetime(2024, 11, 30),
        "region": None,  # All regions
        "state": None,
        "category": None,  # All categories
        "multiplier": 3.0  # 300% spike
    },
    "black_friday_2025": {
        "start_date": datetime(2025, 11, 24),
        "end_date": datetime(2025, 11, 29),
        "region": None,
        "state": None,
        "category": None,
        "multiplier": 3.0
    },
    "supply_disruption": {
        "start_date": datetime(2024, 8, 1),
        "end_date": datetime(2024, 8, 31),
        "region": None,
        "state": None,
        "category": "Blowers",
        "multiplier": 0.4  # 60% drop
    }
}


def load_products(products_file: Path) -> List[Dict]:
    """Load products from JSON file."""
    with open(products_file, 'r') as f:
        return json.load(f)


def load_dealers(dealers_file: Path) -> List[Dict]:
    """Load dealers from CSV file."""
    dealers = []
    with open(dealers_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dealers.append(row)
    return dealers


def select_by_weight(options: list) -> str:
    """Select an option based on weights."""
    rand = random.random()
    cumulative = 0
    for option, weight in options:
        cumulative += weight
        if rand <= cumulative:
            return option
    return options[0][0]


def get_anomaly_multiplier(date: datetime, region: str, state: str, category: str) -> float:
    """Check if date/region/category falls in an anomaly period."""
    multiplier = 1.0
    
    for anomaly_name, config in ANOMALIES.items():
        if config["start_date"] <= date <= config["end_date"]:
            # Check region match
            if config["region"] and config["region"] != region:
                continue
            # Check state match
            if config["state"] and config["state"] != state:
                continue
            # Check category match
            if config["category"] and config["category"] != category:
                continue
            
            # Apply multiplier
            multiplier *= config["multiplier"]
    
    return multiplier


def generate_transactions(
    products: List[Dict],
    dealers: List[Dict],
    target_count: int = 500000
) -> List[Dict]:
    """Generate sales transactions."""
    
    transactions = []
    
    # Group products by category
    products_by_category = {}
    for p in products:
        cat = p["category"]
        if cat not in products_by_category:
            products_by_category[cat] = []
        products_by_category[cat].append(p)
    
    # Group dealers by region
    dealers_by_region = {}
    for d in dealers:
        region = d["region"]
        if region not in dealers_by_region:
            dealers_by_region[region] = []
        dealers_by_region[region].append(d)
    
    # Calculate total days
    total_days = (END_DATE - START_DATE).days + 1
    
    # Base transactions per day (before seasonal adjustment)
    # We'll aim for approximately target_count total
    avg_per_day = target_count / total_days
    
    current_date = START_DATE
    transaction_count = 0
    
    print(f"Generating transactions from {START_DATE.date()} to {END_DATE.date()}...")
    
    while current_date <= END_DATE:
        # Get seasonal weight
        month = current_date.month
        seasonal_weight = SEASONAL_WEIGHTS[month]
        
        # Calculate daily transaction count (with some randomness)
        daily_base = avg_per_day * seasonal_weight
        daily_count = int(random.gauss(daily_base, daily_base * 0.1))
        daily_count = max(100, daily_count)  # Minimum 100 per day
        
        for _ in range(daily_count):
            # Select region
            region = select_by_weight(list(REGIONAL_WEIGHTS.items()))
            
            # Select dealer from region
            dealer = random.choice(dealers_by_region[region])
            
            # Select category
            category = select_by_weight(list(CATEGORY_WEIGHTS.items()))
            
            # Select product from category
            if category not in products_by_category or not products_by_category[category]:
                continue
            product = random.choice(products_by_category[category])
            
            # Check for anomaly
            anomaly_mult = get_anomaly_multiplier(
                current_date, region, dealer["state"], category
            )
            
            # Skip some transactions during supply disruption
            if anomaly_mult < 1.0 and random.random() > anomaly_mult:
                continue
            
            # Generate extra transactions during spikes
            repeat_count = 1
            if anomaly_mult > 1.0:
                repeat_count = int(anomaly_mult)
            
            for _ in range(repeat_count):
                # Quantity (usually 1-3, sometimes more for accessories)
                if category == "Accessories":
                    quantity = random.choices([1, 2, 3, 4, 5], weights=[0.3, 0.3, 0.2, 0.1, 0.1])[0]
                else:
                    quantity = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
                
                # Discount (0-15%, professionals get more)
                customer_type = select_by_weight(CUSTOMER_TYPES)
                if customer_type == "Professional":
                    discount_pct = random.choice([0, 5, 10, 12, 15])
                elif customer_type == "Commercial":
                    discount_pct = random.choice([5, 10, 15])
                else:
                    discount_pct = random.choice([0, 0, 0, 5, 10])
                
                # Calculate amounts
                unit_price = product["msrp"]
                discount_amount = unit_price * (discount_pct / 100)
                discounted_price = unit_price - discount_amount
                total_amount = round(discounted_price * quantity, 2)
                
                # Create transaction
                transaction = {
                    "transaction_id": str(uuid.uuid4()),
                    "transaction_date": current_date.strftime("%Y-%m-%d"),
                    "product_id": product["product_id"],
                    "product_name": product["product_name"],
                    "category": category,
                    "dealer_id": dealer["dealer_id"],
                    "dealer_name": dealer["dealer_name"],
                    "region": region,
                    "state": dealer["state"],
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "discount_pct": discount_pct,
                    "total_amount": total_amount,
                    "customer_type": customer_type,
                    "channel": select_by_weight(SALES_CHANNELS)
                }
                
                transactions.append(transaction)
                transaction_count += 1
        
        # Progress update every month
        if current_date.day == 1:
            print(f"   {current_date.strftime('%Y-%m')}: {transaction_count:,} transactions generated")
        
        current_date += timedelta(days=1)
    
    return transactions


def save_to_csv(transactions: List[Dict], output_dir: Path, chunk_size: int = 100000):
    """Save transactions to CSV files (chunked for large datasets)."""
    fieldnames = [
        "transaction_id", "transaction_date", "product_id", "product_name",
        "category", "dealer_id", "dealer_name", "region", "state",
        "quantity", "unit_price", "discount_pct", "total_amount",
        "customer_type", "channel"
    ]
    
    # Save in chunks
    total = len(transactions)
    file_count = 0
    
    for i in range(0, total, chunk_size):
        chunk = transactions[i:i + chunk_size]
        file_count += 1
        
        output_file = output_dir / f"sales_{file_count:03d}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(chunk)
        
        print(f"   Saved {output_file.name} ({len(chunk):,} records)")
    
    return file_count


def main():
    """Generate and save sales transactions."""
    print("💰 Generating STIHL Sales Transactions...")
    print(f"   Target: ~500,000 transactions")
    print(f"   Period: {START_DATE.date()} to {END_DATE.date()}")
    print()
    
    # Paths
    script_dir = Path(__file__).parent
    products_file = script_dir / "products.json"
    dealers_file = script_dir / "dealers.csv"
    
    # Check dependencies
    if not products_file.exists():
        print("❌ products.json not found. Run generate_products.py first.")
        return
    if not dealers_file.exists():
        print("❌ dealers.csv not found. Run generate_dealers.py first.")
        return
    
    # Load data
    print("Loading products and dealers...")
    products = load_products(products_file)
    dealers = load_dealers(dealers_file)
    print(f"   Loaded {len(products)} products, {len(dealers)} dealers")
    print()
    
    # Generate transactions
    transactions = generate_transactions(products, dealers, target_count=500000)
    
    print()
    print(f"✅ Generated {len(transactions):,} transactions")
    
    # Analyze anomalies
    print("\nAnomaly verification:")
    
    # Hurricane Texas check
    hurricane_sales = [t for t in transactions 
                      if t["transaction_date"] >= "2024-06-10" 
                      and t["transaction_date"] <= "2024-06-20"
                      and t["state"] == "TX"
                      and t["category"] == "Chainsaws"]
    normal_tx_sales = [t for t in transactions
                      if t["transaction_date"] >= "2024-05-10"
                      and t["transaction_date"] <= "2024-05-20"
                      and t["state"] == "TX"
                      and t["category"] == "Chainsaws"]
    if normal_tx_sales:
        ratio = len(hurricane_sales) / len(normal_tx_sales)
        print(f"   • Hurricane Texas: {len(hurricane_sales)} vs {len(normal_tx_sales)} normal ({ratio:.1f}x spike)")
    
    # Black Friday check
    bf_sales = [t for t in transactions
               if t["transaction_date"] >= "2024-11-25"
               and t["transaction_date"] <= "2024-11-30"]
    normal_nov_sales = [t for t in transactions
                       if t["transaction_date"] >= "2024-11-01"
                       and t["transaction_date"] <= "2024-11-06"]
    if normal_nov_sales:
        ratio = len(bf_sales) / len(normal_nov_sales)
        print(f"   • Black Friday 2024: {len(bf_sales)} vs {len(normal_nov_sales)} normal ({ratio:.1f}x spike)")
    
    # Supply disruption check
    aug_blowers = [t for t in transactions
                  if t["transaction_date"] >= "2024-08-01"
                  and t["transaction_date"] <= "2024-08-31"
                  and t["category"] == "Blowers"]
    jul_blowers = [t for t in transactions
                  if t["transaction_date"] >= "2024-07-01"
                  and t["transaction_date"] <= "2024-07-31"
                  and t["category"] == "Blowers"]
    if jul_blowers:
        ratio = len(aug_blowers) / len(jul_blowers)
        print(f"   • Supply disruption: {len(aug_blowers)} Aug vs {len(jul_blowers)} Jul ({ratio:.1f}x - expected ~0.4x)")
    
    # Save to CSV
    print("\nSaving to CSV files...")
    file_count = save_to_csv(transactions, script_dir)
    
    print(f"\n📁 Saved {file_count} CSV files to: {script_dir}")
    
    # Summary statistics
    print("\n📊 Summary Statistics:")
    total_revenue = sum(t["total_amount"] for t in transactions)
    total_units = sum(t["quantity"] for t in transactions)
    print(f"   • Total Revenue: ${total_revenue:,.2f}")
    print(f"   • Total Units: {total_units:,}")
    print(f"   • Avg Transaction: ${total_revenue/len(transactions):,.2f}")
    
    return transactions


if __name__ == "__main__":
    main()
