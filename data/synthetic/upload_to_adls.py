"""
Upload Synthetic Data to Azure Data Lake Storage Gen2
Uploads generated files to the Bronze layer
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.storage.filedatalake import DataLakeServiceClient
from azure.core.exceptions import ResourceExistsError

# Load environment variables
load_dotenv()


def get_datalake_client() -> DataLakeServiceClient:
    """Create DataLake service client from environment variables."""
    connection_string = os.environ.get("ADLS_CONNECTION_STRING")
    
    if not connection_string:
        raise ValueError("ADLS_CONNECTION_STRING not found in environment variables")
    
    return DataLakeServiceClient.from_connection_string(connection_string)


def upload_file(
    file_system_client,
    local_path: Path,
    remote_path: str,
    overwrite: bool = True
) -> bool:
    """Upload a single file to ADLS."""
    try:
        # Get directory and file clients
        directory_name = str(Path(remote_path).parent)
        file_name = Path(remote_path).name
        
        directory_client = file_system_client.get_directory_client(directory_name)
        
        # Create directory if it doesn't exist
        try:
            directory_client.create_directory()
        except ResourceExistsError:
            pass
        
        file_client = directory_client.get_file_client(file_name)
        
        # Upload file
        with open(local_path, 'rb') as f:
            file_contents = f.read()
            file_client.upload_data(file_contents, overwrite=overwrite)
        
        return True
    
    except Exception as e:
        print(f"❌ Error uploading {local_path.name}: {e}")
        return False


def main():
    """Upload all synthetic data to ADLS Bronze layer."""
    print("☁️  Uploading Synthetic Data to Azure Data Lake Storage")
    print("="*60)
    
    # Configuration
    container_name = os.environ.get("ADLS_CONTAINER", "stihl-analytics-data")
    bronze_path = "bronze"
    
    # Get DataLake client
    try:
        service_client = get_datalake_client()
        file_system_client = service_client.get_file_system_client(container_name)
        print(f"✅ Connected to container: {container_name}")
    except Exception as e:
        print(f"❌ Failed to connect to ADLS: {e}")
        print("\nMake sure you have set ADLS_CONNECTION_STRING in your .env file")
        return
    
    # Files to upload
    script_dir = Path(__file__).parent
    
    upload_mappings = [
        # Products
        ("products.json", f"{bronze_path}/products_raw/products.json"),
        # Dealers
        ("dealers.csv", f"{bronze_path}/dealers_raw/dealers.csv"),
    ]
    
    # Add all sales CSV files
    for sales_file in sorted(script_dir.glob("sales_*.csv")):
        upload_mappings.append(
            (sales_file.name, f"{bronze_path}/sales_raw/{sales_file.name}")
        )
    
    # Add all inventory CSV files
    for inv_file in sorted(script_dir.glob("inventory_*.csv")):
        upload_mappings.append(
            (inv_file.name, f"{bronze_path}/inventory_raw/{inv_file.name}")
        )
    
    print(f"\nUploading {len(upload_mappings)} files to {bronze_path}/...")
    print()
    
    success_count = 0
    total_size = 0
    
    for local_name, remote_path in upload_mappings:
        local_path = script_dir / local_name
        
        if not local_path.exists():
            print(f"⚠️  Skipping {local_name} (not found)")
            continue
        
        file_size = local_path.stat().st_size
        size_str = f"{file_size/1024/1024:.1f}MB" if file_size > 1024*1024 else f"{file_size/1024:.0f}KB"
        
        print(f"   Uploading {local_name} ({size_str})...", end=" ")
        
        if upload_file(file_system_client, local_path, remote_path):
            print("✅")
            success_count += 1
            total_size += file_size
        else:
            print("❌")
    
    # Summary
    print()
    print("="*60)
    print(f"✅ Uploaded {success_count}/{len(upload_mappings)} files")
    print(f"📊 Total size: {total_size/1024/1024:.1f} MB")
    print()
    print("Files are now available at:")
    print(f"   abfss://{container_name}@{os.environ.get('ADLS_ACCOUNT_NAME', 'adlsstihlanalytics')}.dfs.core.windows.net/{bronze_path}/")
    
    print()
    print("Next steps:")
    print("   1. Open Databricks workspace")
    print("   2. Run Bronze ingestion notebook")
    print("   3. Transform to Silver/Gold layers")


if __name__ == "__main__":
    main()
