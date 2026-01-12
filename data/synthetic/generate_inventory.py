"""
STIHL Inventory Snapshot Generator
Generates ~150K daily inventory snapshots with stockout and overstock scenarios
"""

import csv
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

# Date range (same as sales)
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)

# Warehouses by region
WAREHOUSES = {
    "Southwest": ["WH-TX-01", "WH-TX-02", "WH-AZ-01"],
    "Southeast": ["WH-FL-01", "WH-GA-01", "WH-NC-01"],
    "Midwest": ["WH-OH-01", "WH-IL-01", "WH-MI-01"],
    "Northeast": ["WH-NY-01", "WH-PA-01"],
    "West": ["WH-CA-01", "WH-CA-02", "WH-WA-01"]
}

# Inventory parameters by category
CATEGORY_INVENTORY = {
    "Chainsaws": {"base_stock": 150, "reorder_point": 30, "lead_time_days": 14},
    "Trimmers": {"base_stock": 200, "reorder_point": 40, "lead_time_days": 10},
    "Blowers": {"base_stock": 180, "reorder_point": 35, "lead_time_days": 10},
    "Hedge Trimmers": {"base_stock": 100, "reorder_point": 20, "lead_time_days": 14},
    "Lawn Mowers": {"base_stock": 80, "reorder_point": 15, "lead_time_days": 21},
    "Multi-System": {"base_stock": 60, "reorder_point": 12, "lead_time_days": 14},
    "Accessories": {"base_stock": 500, "reorder_point": 100, "lead_time_days": 7}
}

# Anomalies to inject (matching sales anomalies)
INVENTORY_ANOMALIES = {
    "stockout_ms271_southwest": {
        "start_date": datetime(2024, 9, 1),
        "end_date": datetime(2024, 10, 15),
        "region": "Southwest",
        "product_id": "MS-271",
        "stock_level": 0.05  # 5% of normal stock
    },
    "overstock_fs91_northeast": {
        "start_date": datetime(2024, 10, 1),
        "end_date": datetime(2024, 12, 31),
        "region": "Northeast",
        "product_id": "FS-91",
        "stock_level": 3.0  # 300% of normal stock
    },
    "hurricane_depletion_texas": {
        "start_date": datetime(2024, 6, 15),
        "end_date": datetime(2024, 7, 15),
        "region": "Southwest",
        "product_id": None,  # All chainsaws
        "category": "Chainsaws",
        "stock_level": 0.2  # 20% of normal (depleted by spike)
    },
    "supply_disruption_blowers": {
        "start_date": datetime(2024, 8, 1),
        "end_date": datetime(2024, 9, 15),
        "region": None,  # All regions
        "product_id": None,
        "category": "Blowers",
        "stock_level": 0.3  # 30% of normal
    }
}


def load_products(products_file: Path) -> List[Dict]:
    """Load products from JSON file."""
    with open(products_file, 'r') as f:
        return json.load(f)


def get_anomaly_modifier(
    date: datetime,
    region: str,
    product_id: str,
    category: str
) -> float:
    """Check if inventory should be modified due to anomaly."""
    modifier = 1.0
    
    for anomaly_name, config in INVENTORY_ANOMALIES.items():
        if config["start_date"] <= date <= config["end_date"]:
            # Check region
            if config.get("region") and config["region"] != region:
                continue
            # Check product
            if config.get("product_id") and config["product_id"] != product_id:
                continue
            # Check category
            if config.get("category") and config["category"] != category:
                continue
            
            modifier = min(modifier, config["stock_level"])
    
    return modifier


def calculate_status(quantity_on_hand: int, reorder_point: int, days_of_supply: float) -> str:
    """Calculate inventory status."""
    if quantity_on_hand == 0:
        return "OUT_OF_STOCK"
    elif days_of_supply < 7:
        return "CRITICAL"
    elif days_of_supply < 14 or quantity_on_hand < reorder_point:
        return "LOW"
    elif days_of_supply > 90:
        return "OVERSTOCK"
    else:
        return "NORMAL"


def generate_inventory_snapshots(
    products: List[Dict],
    sample_frequency: int = 7  # Generate every N days to limit data size
) -> List[Dict]:
    """Generate inventory snapshots."""
    
    snapshots = []
    
    # Get unique product categories
    product_categories = {p["product_id"]: p["category"] for p in products}
    
    # We'll sample a subset of products per warehouse to keep data manageable
    # Select ~30 key products for detailed tracking
    key_products = []
    
    # Ensure we include anomaly products
    key_product_ids = {"MS-271", "FS-91"}  # Anomaly products
    
    # Add top products from each category
    products_by_cat = {}
    for p in products:
        cat = p["category"]
        if cat not in products_by_cat:
            products_by_cat[cat] = []
        products_by_cat[cat].append(p)
    
    for cat, cat_products in products_by_cat.items():
        # Take top 5 by price (usually most popular)
        sorted_products = sorted(cat_products, key=lambda x: x["msrp"], reverse=True)[:5]
        for p in sorted_products:
            key_product_ids.add(p["product_id"])
    
    key_products = [p for p in products if p["product_id"] in key_product_ids]
    print(f"   Tracking {len(key_products)} key products across warehouses")
    
    # Generate snapshots
    current_date = START_DATE
    snapshot_count = 0
    
    # Initialize inventory levels per warehouse/product
    inventory_state = {}
    
    for region, warehouses in WAREHOUSES.items():
        for warehouse in warehouses:
            inventory_state[warehouse] = {}
            for product in key_products:
                category = product["category"]
                base_config = CATEGORY_INVENTORY.get(category, CATEGORY_INVENTORY["Accessories"])
                
                # Add some randomness to initial stock
                initial_stock = int(base_config["base_stock"] * random.uniform(0.8, 1.2))
                
                inventory_state[warehouse][product["product_id"]] = {
                    "quantity": initial_stock,
                    "category": category,
                    "reorder_point": base_config["reorder_point"],
                    "avg_daily_sales": initial_stock / 30  # Rough estimate
                }
    
    print(f"Generating inventory snapshots from {START_DATE.date()} to {END_DATE.date()}...")
    
    while current_date <= END_DATE:
        # Only generate snapshots on sample days
        if (current_date - START_DATE).days % sample_frequency == 0:
            
            for region, warehouses in WAREHOUSES.items():
                for warehouse in warehouses:
                    for product in key_products:
                        product_id = product["product_id"]
                        category = product["category"]
                        
                        # Get current state
                        state = inventory_state[warehouse][product_id]
                        
                        # Check for anomaly modifier
                        anomaly_mod = get_anomaly_modifier(
                            current_date, region, product_id, category
                        )
                        
                        # Simulate inventory changes
                        # Daily sales (with seasonal variation)
                        month = current_date.month
                        seasonal_mult = {
                            1: 0.6, 2: 0.7, 3: 1.2, 4: 1.5, 5: 1.5, 6: 1.3,
                            7: 0.7, 8: 0.7, 9: 1.2, 10: 1.3, 11: 1.4, 12: 0.8
                        }.get(month, 1.0)
                        
                        daily_sales = state["avg_daily_sales"] * seasonal_mult * sample_frequency
                        daily_sales = int(random.gauss(daily_sales, daily_sales * 0.3))
                        daily_sales = max(0, daily_sales)
                        
                        # Replenishment (if below reorder point and not in anomaly)
                        replenishment = 0
                        if state["quantity"] < state["reorder_point"] and anomaly_mod >= 0.8:
                            # Reorder quantity
                            base_config = CATEGORY_INVENTORY.get(category, CATEGORY_INVENTORY["Accessories"])
                            replenishment = base_config["base_stock"]
                        
                        # Update quantity
                        new_quantity = state["quantity"] - daily_sales + replenishment
                        
                        # Apply anomaly modifier
                        if anomaly_mod < 1.0:
                            new_quantity = int(new_quantity * anomaly_mod)
                        elif anomaly_mod > 1.0:
                            new_quantity = int(new_quantity * anomaly_mod)
                        
                        new_quantity = max(0, new_quantity)
                        
                        # Calculate derived fields
                        avg_daily = max(1, state["avg_daily_sales"] * seasonal_mult)
                        days_of_supply = new_quantity / avg_daily if avg_daily > 0 else 999
                        
                        # Reserved quantity (5-15% of on-hand)
                        reserved = int(new_quantity * random.uniform(0.05, 0.15))
                        available = new_quantity - reserved
                        
                        # Determine status
                        status = calculate_status(
                            new_quantity, 
                            state["reorder_point"],
                            days_of_supply
                        )
                        
                        # Create snapshot
                        snapshot = {
                            "snapshot_date": current_date.strftime("%Y-%m-%d"),
                            "product_id": product_id,
                            "product_name": product["product_name"],
                            "category": category,
                            "warehouse_id": warehouse,
                            "region": region,
                            "quantity_on_hand": new_quantity,
                            "quantity_available": available,
                            "quantity_reserved": reserved,
                            "reorder_point": state["reorder_point"],
                            "days_of_supply": round(days_of_supply, 1),
                            "status": status
                        }
                        
                        snapshots.append(snapshot)
                        snapshot_count += 1
                        
                        # Update state for next iteration
                        state["quantity"] = new_quantity
            
            # Progress update
            if current_date.day <= sample_frequency:
                print(f"   {current_date.strftime('%Y-%m')}: {snapshot_count:,} snapshots generated")
        
        current_date += timedelta(days=1)
    
    return snapshots


def save_to_csv(snapshots: List[Dict], output_dir: Path, chunk_size: int = 50000):
    """Save inventory snapshots to CSV files."""
    fieldnames = [
        "snapshot_date", "product_id", "product_name", "category",
        "warehouse_id", "region", "quantity_on_hand", "quantity_available",
        "quantity_reserved", "reorder_point", "days_of_supply", "status"
    ]
    
    total = len(snapshots)
    file_count = 0
    
    for i in range(0, total, chunk_size):
        chunk = snapshots[i:i + chunk_size]
        file_count += 1
        
        output_file = output_dir / f"inventory_{file_count:03d}.csv"
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(chunk)
        
        print(f"   Saved {output_file.name} ({len(chunk):,} records)")
    
    return file_count


def main():
    """Generate and save inventory snapshots."""
    print("📦 Generating STIHL Inventory Snapshots...")
    print(f"   Target: ~150,000 snapshots")
    print(f"   Period: {START_DATE.date()} to {END_DATE.date()}")
    print()
    
    # Paths
    script_dir = Path(__file__).parent
    products_file = script_dir / "products.json"
    
    # Check dependencies
    if not products_file.exists():
        print("❌ products.json not found. Run generate_products.py first.")
        return
    
    # Load products
    print("Loading products...")
    products = load_products(products_file)
    print(f"   Loaded {len(products)} products")
    print()
    
    # Generate snapshots
    snapshots = generate_inventory_snapshots(products, sample_frequency=3)
    
    print()
    print(f"✅ Generated {len(snapshots):,} inventory snapshots")
    
    # Analyze anomalies
    print("\nAnomaly verification:")
    
    # MS-271 stockout in Southwest
    ms271_sw = [s for s in snapshots 
                if s["product_id"] == "MS-271" 
                and s["region"] == "Southwest"
                and s["snapshot_date"] >= "2024-09-01"
                and s["snapshot_date"] <= "2024-10-15"]
    stockout_count = len([s for s in ms271_sw if s["status"] in ["OUT_OF_STOCK", "CRITICAL"]])
    print(f"   • MS-271 Southwest stockout: {stockout_count}/{len(ms271_sw)} snapshots critical/OOS")
    
    # FS-91 overstock in Northeast
    fs91_ne = [s for s in snapshots
               if s["product_id"] == "FS-91"
               and s["region"] == "Northeast"
               and s["snapshot_date"] >= "2024-10-01"]
    overstock_count = len([s for s in fs91_ne if s["status"] == "OVERSTOCK"])
    print(f"   • FS-91 Northeast overstock: {overstock_count}/{len(fs91_ne)} snapshots overstocked")
    
    # Status distribution
    print("\nStatus distribution:")
    status_counts = {}
    for s in snapshots:
        status = s["status"]
        status_counts[status] = status_counts.get(status, 0) + 1
    
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        pct = count / len(snapshots) * 100
        print(f"   • {status}: {count:,} ({pct:.1f}%)")
    
    # Save to CSV
    print("\nSaving to CSV files...")
    file_count = save_to_csv(snapshots, script_dir)
    
    print(f"\n📁 Saved {file_count} CSV files to: {script_dir}")
    
    return snapshots


if __name__ == "__main__":
    main()
