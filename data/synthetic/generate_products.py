"""
STIHL Product Catalog Generator
Generates ~200 realistic STIHL products based on official product lineup
"""

import json
import random
from pathlib import Path

# Product categories and their configurations
PRODUCT_CATALOG = {
    "Chainsaws": {
        "prefix": "MS",
        "subcategories": {
            "Homeowner": {
                "models": [
                    {"number": "170", "name": "MS 170", "cc": 30.1, "weight": 8.6, "msrp": 199.99},
                    {"number": "180", "name": "MS 180 C-BE", "cc": 31.8, "weight": 9.0, "msrp": 279.99},
                    {"number": "194", "name": "MS 194 C-E", "cc": 31.8, "weight": 8.4, "msrp": 329.99},
                    {"number": "211", "name": "MS 211", "cc": 35.2, "weight": 9.5, "msrp": 349.99},
                    {"number": "250", "name": "MS 250", "cc": 45.4, "weight": 10.1, "msrp": 379.99},
                ],
                "power_type": "Gas"
            },
            "Farm & Ranch": {
                "models": [
                    {"number": "271", "name": "MS 271 Farm Boss", "cc": 50.2, "weight": 12.3, "msrp": 449.99},
                    {"number": "291", "name": "MS 291", "cc": 55.5, "weight": 12.8, "msrp": 499.99},
                    {"number": "311", "name": "MS 311", "cc": 59.0, "weight": 13.2, "msrp": 549.99},
                ],
                "power_type": "Gas"
            },
            "Professional": {
                "models": [
                    {"number": "362", "name": "MS 362 C-M", "cc": 59.0, "weight": 13.0, "msrp": 899.99},
                    {"number": "400", "name": "MS 400 C-M", "cc": 66.8, "weight": 13.4, "msrp": 1049.99},
                    {"number": "461", "name": "MS 461", "cc": 76.5, "weight": 14.6, "msrp": 1199.99},
                    {"number": "462", "name": "MS 462 C-M", "cc": 72.2, "weight": 13.2, "msrp": 1299.99},
                    {"number": "500i", "name": "MS 500i", "cc": 79.2, "weight": 13.9, "msrp": 1549.99},
                    {"number": "661", "name": "MS 661 C-M", "cc": 91.1, "weight": 16.5, "msrp": 1699.99},
                    {"number": "881", "name": "MS 881", "cc": 121.6, "weight": 22.0, "msrp": 2099.99},
                ],
                "power_type": "Gas"
            },
            "Battery": {
                "models": [
                    {"number": "MSA 120", "name": "MSA 120 C-B", "cc": None, "weight": 8.4, "msrp": 299.99, "voltage": 36},
                    {"number": "MSA 140", "name": "MSA 140 C-B", "cc": None, "weight": 8.8, "msrp": 349.99, "voltage": 36},
                    {"number": "MSA 160", "name": "MSA 160 C-B", "cc": None, "weight": 9.3, "msrp": 399.99, "voltage": 36},
                    {"number": "MSA 200", "name": "MSA 200 C-B", "cc": None, "weight": 9.9, "msrp": 449.99, "voltage": 36},
                    {"number": "MSA 220", "name": "MSA 220 C-B", "cc": None, "weight": 10.6, "msrp": 549.99, "voltage": 36},
                    {"number": "MSA 300", "name": "MSA 300 C-O", "cc": None, "weight": 11.2, "msrp": 799.99, "voltage": 36},
                ],
                "power_type": "Battery"
            }
        },
        "description_template": "{power_type} chainsaw ideal for {use_case}. Features {cc_text}, weighs {weight} lbs."
    },
    "Trimmers": {
        "prefix": "FS",
        "subcategories": {
            "Homeowner": {
                "models": [
                    {"number": "38", "name": "FS 38", "cc": 27.2, "weight": 9.3, "msrp": 149.99},
                    {"number": "40", "name": "FS 40 C-E", "cc": 27.2, "weight": 9.5, "msrp": 179.99},
                    {"number": "50", "name": "FS 50 C-E", "cc": 27.2, "weight": 9.7, "msrp": 199.99},
                    {"number": "56", "name": "FS 56 RC-E", "cc": 27.2, "weight": 10.1, "msrp": 229.99},
                ],
                "power_type": "Gas"
            },
            "Professional": {
                "models": [
                    {"number": "91", "name": "FS 91 R", "cc": 28.4, "weight": 11.1, "msrp": 379.99},
                    {"number": "111", "name": "FS 111 R", "cc": 31.4, "weight": 11.3, "msrp": 429.99},
                    {"number": "131", "name": "FS 131 R", "cc": 36.3, "weight": 12.0, "msrp": 479.99},
                    {"number": "240", "name": "FS 240", "cc": 37.7, "weight": 14.8, "msrp": 599.99},
                    {"number": "560", "name": "FS 560 C-EM", "cc": 57.1, "weight": 21.0, "msrp": 899.99},
                ],
                "power_type": "Gas"
            },
            "Battery": {
                "models": [
                    {"number": "FSA 45", "name": "FSA 45", "cc": None, "weight": 5.5, "msrp": 129.99, "voltage": 18},
                    {"number": "FSA 57", "name": "FSA 57", "cc": None, "weight": 6.2, "msrp": 179.99, "voltage": 36},
                    {"number": "FSA 90", "name": "FSA 90 R", "cc": None, "weight": 8.6, "msrp": 299.99, "voltage": 36},
                    {"number": "FSA 130", "name": "FSA 130 R", "cc": None, "weight": 9.0, "msrp": 399.99, "voltage": 36},
                    {"number": "FSA 135", "name": "FSA 135", "cc": None, "weight": 9.3, "msrp": 449.99, "voltage": 36},
                ],
                "power_type": "Battery"
            }
        },
        "description_template": "{power_type} string trimmer for {use_case}. Features {cc_text}, weighs {weight} lbs."
    },
    "Blowers": {
        "prefix": "BG",
        "subcategories": {
            "Handheld": {
                "models": [
                    {"number": "50", "name": "BG 50", "cc": 27.2, "weight": 7.9, "msrp": 149.99},
                    {"number": "56", "name": "BG 56 C-E", "cc": 27.2, "weight": 8.6, "msrp": 199.99},
                    {"number": "86", "name": "BG 86 C-E", "cc": 27.2, "weight": 9.0, "msrp": 279.99},
                ],
                "power_type": "Gas"
            },
            "Backpack": {
                "models": [
                    {"number": "BR 350", "name": "BR 350", "cc": 63.3, "weight": 22.9, "msrp": 379.99},
                    {"number": "BR 430", "name": "BR 430", "cc": 63.3, "weight": 23.4, "msrp": 429.99},
                    {"number": "BR 600", "name": "BR 600", "cc": 64.8, "weight": 21.6, "msrp": 549.99},
                    {"number": "BR 700", "name": "BR 700", "cc": 64.8, "weight": 23.4, "msrp": 599.99},
                    {"number": "BR 800", "name": "BR 800 C-E", "cc": 79.9, "weight": 25.8, "msrp": 699.99},
                ],
                "power_type": "Gas"
            },
            "Battery": {
                "models": [
                    {"number": "BGA 45", "name": "BGA 45", "cc": None, "weight": 4.5, "msrp": 129.99, "voltage": 18},
                    {"number": "BGA 57", "name": "BGA 57", "cc": None, "weight": 5.1, "msrp": 179.99, "voltage": 36},
                    {"number": "BGA 86", "name": "BGA 86", "cc": None, "weight": 7.3, "msrp": 299.99, "voltage": 36},
                    {"number": "BGA 100", "name": "BGA 100", "cc": None, "weight": 8.2, "msrp": 349.99, "voltage": 36},
                    {"number": "BGA 200", "name": "BGA 200", "cc": None, "weight": 9.0, "msrp": 449.99, "voltage": 36},
                ],
                "power_type": "Battery"
            }
        },
        "description_template": "{power_type} blower for {use_case}. Features {cc_text}, weighs {weight} lbs."
    },
    "Hedge Trimmers": {
        "prefix": "HS",
        "subcategories": {
            "Homeowner": {
                "models": [
                    {"number": "45", "name": "HS 45", "cc": 27.2, "weight": 10.8, "msrp": 299.99, "blade_length": 18},
                    {"number": "56", "name": "HS 56 C-E", "cc": 27.2, "weight": 11.0, "msrp": 379.99, "blade_length": 24},
                ],
                "power_type": "Gas"
            },
            "Professional": {
                "models": [
                    {"number": "82", "name": "HS 82 R", "cc": 22.7, "weight": 11.7, "msrp": 549.99, "blade_length": 24},
                    {"number": "87", "name": "HS 87 R", "cc": 22.7, "weight": 12.1, "msrp": 599.99, "blade_length": 30},
                ],
                "power_type": "Gas"
            },
            "Extended Reach": {
                "models": [
                    {"number": "HL 91", "name": "HL 91 K", "cc": 28.4, "weight": 13.9, "msrp": 599.99, "blade_length": 20},
                    {"number": "HL 92", "name": "HL 92 C-E", "cc": 28.4, "weight": 14.3, "msrp": 699.99, "blade_length": 20},
                    {"number": "HL 94", "name": "HL 94 C-E", "cc": 28.4, "weight": 14.1, "msrp": 749.99, "blade_length": 24},
                ],
                "power_type": "Gas"
            },
            "Battery": {
                "models": [
                    {"number": "HSA 45", "name": "HSA 45", "cc": None, "weight": 5.5, "msrp": 129.99, "voltage": 18, "blade_length": 20},
                    {"number": "HSA 56", "name": "HSA 56", "cc": None, "weight": 6.2, "msrp": 249.99, "voltage": 36, "blade_length": 18},
                    {"number": "HSA 66", "name": "HSA 66", "cc": None, "weight": 8.6, "msrp": 349.99, "voltage": 36, "blade_length": 20},
                    {"number": "HSA 86", "name": "HSA 86", "cc": None, "weight": 9.0, "msrp": 399.99, "voltage": 36, "blade_length": 24},
                    {"number": "HSA 94", "name": "HSA 94 R", "cc": None, "weight": 9.7, "msrp": 449.99, "voltage": 36, "blade_length": 24},
                ],
                "power_type": "Battery"
            }
        },
        "description_template": "{power_type} hedge trimmer for {use_case}. Features {blade_length}\" blade, weighs {weight} lbs."
    },
    "Lawn Mowers": {
        "prefix": "RM",
        "subcategories": {
            "Push": {
                "models": [
                    {"number": "RM 443", "name": "RM 443", "cc": 145, "weight": 62, "msrp": 399.99, "deck_size": 17},
                    {"number": "RM 545", "name": "RM 545 V", "cc": 163, "weight": 75, "msrp": 499.99, "deck_size": 21},
                ],
                "power_type": "Gas"
            },
            "Self-Propelled": {
                "models": [
                    {"number": "RM 655", "name": "RM 655 V", "cc": 173, "weight": 85, "msrp": 599.99, "deck_size": 21},
                    {"number": "RM 756", "name": "RM 756 GC", "cc": 173, "weight": 95, "msrp": 749.99, "deck_size": 22},
                ],
                "power_type": "Gas"
            },
            "Battery": {
                "models": [
                    {"number": "RMA 460", "name": "RMA 460", "cc": None, "weight": 55, "msrp": 449.99, "voltage": 36, "deck_size": 19},
                    {"number": "RMA 510", "name": "RMA 510 V", "cc": None, "weight": 65, "msrp": 549.99, "voltage": 36, "deck_size": 21},
                    {"number": "RMA 765", "name": "RMA 765 V", "cc": None, "weight": 75, "msrp": 899.99, "voltage": 36, "deck_size": 25},
                ],
                "power_type": "Battery"
            },
            "Robotic": {
                "models": [
                    {"number": "iMOW 5", "name": "iMOW RMI 422", "cc": None, "weight": 18, "msrp": 1299.99, "voltage": 28, "deck_size": 8},
                    {"number": "iMOW 6", "name": "iMOW RMI 522 C", "cc": None, "weight": 21, "msrp": 1699.99, "voltage": 28, "deck_size": 8},
                    {"number": "iMOW 7", "name": "iMOW RMI 632", "cc": None, "weight": 26, "msrp": 2499.99, "voltage": 28, "deck_size": 10},
                ],
                "power_type": "Battery"
            }
        },
        "description_template": "{power_type} lawn mower for {use_case}. Features {deck_size}\" deck, weighs {weight} lbs."
    },
    "Multi-System": {
        "prefix": "KM",
        "subcategories": {
            "KombiSystem": {
                "models": [
                    {"number": "56", "name": "KM 56 RC-E", "cc": 27.2, "weight": 9.3, "msrp": 289.99},
                    {"number": "91", "name": "KM 91 R", "cc": 28.4, "weight": 9.9, "msrp": 369.99},
                    {"number": "111", "name": "KM 111 R", "cc": 31.4, "weight": 10.4, "msrp": 419.99},
                    {"number": "131", "name": "KM 131 R", "cc": 36.3, "weight": 11.2, "msrp": 469.99},
                ],
                "power_type": "Gas"
            },
            "Battery KombiSystem": {
                "models": [
                    {"number": "KMA 80", "name": "KMA 80 R", "cc": None, "weight": 7.5, "msrp": 279.99, "voltage": 36},
                    {"number": "KMA 130", "name": "KMA 130 R", "cc": None, "weight": 8.6, "msrp": 379.99, "voltage": 36},
                    {"number": "KMA 135", "name": "KMA 135 R", "cc": None, "weight": 9.0, "msrp": 449.99, "voltage": 36},
                ],
                "power_type": "Battery"
            }
        },
        "description_template": "{power_type} KombiSystem powerhead for {use_case}. Compatible with all KombiSystem attachments. Weighs {weight} lbs."
    },
    "Accessories": {
        "prefix": "ACC",
        "subcategories": {
            "Chains": {
                "models": [
                    {"number": "26RS", "name": "26 RS Rapid Super Chain", "msrp": 29.99, "chain_type": "Full Chisel"},
                    {"number": "26RM", "name": "26 RM Rapid Micro Chain", "msrp": 27.99, "chain_type": "Semi Chisel"},
                    {"number": "33RS", "name": "33 RS Rapid Super Chain", "msrp": 34.99, "chain_type": "Full Chisel"},
                    {"number": "36RS", "name": "36 RS Rapid Super Chain", "msrp": 39.99, "chain_type": "Full Chisel"},
                ],
                "power_type": "Accessory"
            },
            "Guide Bars": {
                "models": [
                    {"number": "BAR-14", "name": "14\" Rollomatic E Guide Bar", "msrp": 49.99, "bar_length": 14},
                    {"number": "BAR-16", "name": "16\" Rollomatic E Guide Bar", "msrp": 54.99, "bar_length": 16},
                    {"number": "BAR-18", "name": "18\" Rollomatic E Guide Bar", "msrp": 59.99, "bar_length": 18},
                    {"number": "BAR-20", "name": "20\" Rollomatic E Guide Bar", "msrp": 64.99, "bar_length": 20},
                    {"number": "BAR-25", "name": "25\" Rollomatic ES Guide Bar", "msrp": 89.99, "bar_length": 25},
                ],
                "power_type": "Accessory"
            },
            "Batteries": {
                "models": [
                    {"number": "AK 10", "name": "AK 10 Battery", "msrp": 69.99, "voltage": 36, "ah": 1.4},
                    {"number": "AK 20", "name": "AK 20 Battery", "msrp": 99.99, "voltage": 36, "ah": 2.8},
                    {"number": "AK 30", "name": "AK 30 Battery", "msrp": 149.99, "voltage": 36, "ah": 4.8},
                    {"number": "AP 100", "name": "AP 100 Battery", "msrp": 149.99, "voltage": 36, "ah": 2.0},
                    {"number": "AP 200", "name": "AP 200 Battery", "msrp": 199.99, "voltage": 36, "ah": 4.0},
                    {"number": "AP 300", "name": "AP 300 Battery", "msrp": 279.99, "voltage": 36, "ah": 6.0},
                    {"number": "AP 500", "name": "AP 500 S Battery", "msrp": 399.99, "voltage": 36, "ah": 9.4},
                ],
                "power_type": "Accessory"
            },
            "Chargers": {
                "models": [
                    {"number": "AL 101", "name": "AL 101 Standard Charger", "msrp": 49.99, "charge_time": 210},
                    {"number": "AL 300", "name": "AL 300 Rapid Charger", "msrp": 79.99, "charge_time": 80},
                    {"number": "AL 500", "name": "AL 500 High-Speed Charger", "msrp": 199.99, "charge_time": 35},
                ],
                "power_type": "Accessory"
            },
            "PPE": {
                "models": [
                    {"number": "PPE-CHAPS", "name": "Function Protective Chaps", "msrp": 89.99},
                    {"number": "PPE-HELMET", "name": "Function Basic Helmet System", "msrp": 69.99},
                    {"number": "PPE-GLOVES", "name": "Function Grip Gloves", "msrp": 29.99},
                    {"number": "PPE-GLASSES", "name": "Clear Safety Glasses", "msrp": 14.99},
                    {"number": "PPE-BOOTS", "name": "ProMark Chainsaw Boots", "msrp": 249.99},
                ],
                "power_type": "Accessory"
            }
        },
        "description_template": "STIHL {name}. High-quality accessory for STIHL equipment."
    }
}

# Use cases by product line
USE_CASES = {
    "Homeowner": "light-duty residential tasks",
    "Farm & Ranch": "cutting firewood, felling medium trees, and farm maintenance",
    "Professional": "heavy-duty commercial and professional use",
    "Battery": "quiet, emission-free operation",
    "Handheld": "quick cleanups and light-duty blowing",
    "Backpack": "extended professional use and large property maintenance",
    "Push": "small to medium lawns",
    "Self-Propelled": "medium to large lawns with ease",
    "Robotic": "automated lawn care with minimal effort",
    "Extended Reach": "tall hedges and hard-to-reach areas",
    "KombiSystem": "versatile multi-tool applications",
    "Battery KombiSystem": "quiet, emission-free multi-tool operation"
}


def generate_product_id(category: str, model: dict, index: int) -> str:
    """Generate a unique product ID."""
    prefix = PRODUCT_CATALOG[category]["prefix"]
    number = model.get("number", str(index).zfill(3))
    return f"{prefix}-{number}"


def calculate_cost(msrp: float) -> float:
    """Calculate product cost (typically 50-65% of MSRP)."""
    margin = random.uniform(0.50, 0.65)
    return round(msrp * margin, 2)


def generate_description(category: str, subcategory: str, model: dict, power_type: str) -> str:
    """Generate a product description."""
    template = PRODUCT_CATALOG[category].get("description_template", "STIHL {name}.")
    
    use_case = USE_CASES.get(subcategory, "general outdoor power equipment needs")
    
    cc_text = f"{model['cc']} cc engine" if model.get('cc') else f"{model.get('voltage', 36)}V battery power"
    
    return template.format(
        power_type=power_type,
        name=model['name'],
        use_case=use_case,
        cc_text=cc_text,
        weight=model.get('weight', 'N/A'),
        blade_length=model.get('blade_length', 'N/A'),
        deck_size=model.get('deck_size', 'N/A')
    )


def generate_features(category: str, model: dict, power_type: str) -> list:
    """Generate feature list for a product."""
    features = []
    
    if power_type == "Gas":
        features.extend([
            "Easy2Start™ system",
            "Anti-vibration technology",
            "Long-life air filtration"
        ])
    elif power_type == "Battery":
        features.extend([
            "Zero emissions",
            "Low noise operation", 
            "Quick-release battery"
        ])
    
    if category == "Chainsaws":
        features.extend(["Side-access chain tensioner", "IntelliCarb™ compensating carburetor"])
    elif category == "Trimmers":
        features.extend(["AutoCut® trimmer head", "Loop handle or bike handle option"])
    elif category == "Blowers":
        features.extend(["Variable speed trigger", "Ergonomic design"])
    elif category == "Hedge Trimmers":
        features.extend(["Laser-cut blades", "Integrated cut protection"])
    elif category == "Lawn Mowers":
        features.extend(["Height adjustment", "Mulching capability"])
    
    return features[:5]  # Limit to 5 features


def generate_products() -> list:
    """Generate all products."""
    products = []
    
    for category, cat_data in PRODUCT_CATALOG.items():
        for subcategory, sub_data in cat_data["subcategories"].items():
            power_type = sub_data.get("power_type", "Gas")
            
            for idx, model in enumerate(sub_data["models"]):
                product = {
                    "product_id": generate_product_id(category, model, idx),
                    "product_name": model["name"],
                    "category": category,
                    "subcategory": subcategory,
                    "product_line": subcategory,
                    "power_type": power_type,
                    "engine_cc": model.get("cc"),
                    "voltage": model.get("voltage"),
                    "weight_lbs": model.get("weight"),
                    "msrp": model["msrp"],
                    "cost": calculate_cost(model["msrp"]),
                    "description": generate_description(category, subcategory, model, power_type),
                    "features": generate_features(category, model, power_type),
                    "is_active": True
                }
                
                # Add category-specific fields
                if "blade_length" in model:
                    product["blade_length_inches"] = model["blade_length"]
                if "deck_size" in model:
                    product["deck_size_inches"] = model["deck_size"]
                if "bar_length" in model:
                    product["bar_length_inches"] = model["bar_length"]
                if "chain_type" in model:
                    product["chain_type"] = model["chain_type"]
                if "ah" in model:
                    product["amp_hours"] = model["ah"]
                if "charge_time" in model:
                    product["charge_time_minutes"] = model["charge_time"]
                
                products.append(product)
    
    return products


def main():
    """Generate and save products."""
    print("🔧 Generating STIHL Product Catalog...")
    
    products = generate_products()
    
    # Create output directory
    output_dir = Path(__file__).parent
    output_file = output_dir / "products.json"
    
    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(products, f, indent=2)
    
    # Print summary
    print(f"\n✅ Generated {len(products)} products")
    print("\nCategory breakdown:")
    
    categories = {}
    for p in products:
        cat = p["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"   • {cat}: {count}")
    
    print(f"\n📁 Saved to: {output_file}")
    
    return products


if __name__ == "__main__":
    main()
