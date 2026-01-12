"""
STIHL Analytics Agent - Synthetic Data Generator
Runs all data generation scripts in sequence
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime


def run_script(script_name: str) -> bool:
    """Run a Python script and return success status."""
    script_path = Path(__file__).parent / script_name
    
    print(f"\n{'='*60}")
    print(f"Running: {script_name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            cwd=str(script_path.parent)
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_name}: {e}")
        return False


def main():
    """Run all data generation scripts."""
    start_time = datetime.now()
    
    print("="*60)
    print("   STIHL Analytics Agent - Synthetic Data Generation")
    print("="*60)
    print(f"\nStarted at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis will generate:")
    print("   • ~200 products (products.json)")
    print("   • ~100 dealers (dealers.csv)")
    print("   • ~500K sales transactions (sales_*.csv)")
    print("   • ~150K inventory snapshots (inventory_*.csv)")
    
    # Run scripts in order
    scripts = [
        "generate_products.py",
        "generate_dealers.py",
        "generate_sales.py",
        "generate_inventory.py"
    ]
    
    success_count = 0
    
    for script in scripts:
        if run_script(script):
            success_count += 1
        else:
            print(f"\n⚠️  Stopping due to error in {script}")
            break
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("   SUMMARY")
    print("="*60)
    print(f"\nCompleted: {success_count}/{len(scripts)} scripts")
    print(f"Duration: {duration}")
    
    if success_count == len(scripts):
        print("\n✅ All synthetic data generated successfully!")
        print("\nGenerated files:")
        
        output_dir = Path(__file__).parent
        files = list(output_dir.glob("*.json")) + list(output_dir.glob("*.csv"))
        
        total_size = 0
        for f in sorted(files):
            size = f.stat().st_size
            total_size += size
            size_str = f"{size/1024/1024:.1f} MB" if size > 1024*1024 else f"{size/1024:.1f} KB"
            print(f"   • {f.name}: {size_str}")
        
        print(f"\nTotal size: {total_size/1024/1024:.1f} MB")
        
        print("\n" + "="*60)
        print("   NEXT STEPS")
        print("="*60)
        print("\n1. Upload to Azure Data Lake Storage (Bronze layer):")
        print("   python upload_to_adls.py")
        print("\n2. Or manually upload via Azure Portal/Storage Explorer")
        print("   Container: stihl-analytics-data")
        print("   Path: bronze/")
    else:
        print("\n❌ Data generation incomplete. Check errors above.")


if __name__ == "__main__":
    main()
