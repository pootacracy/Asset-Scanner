import os
import csv
from glob import glob
import uuid

def count_files(directory):
    """Count all files in the given directory and its subdirectories."""
    total = 0
    for entry in os.listdir(directory):
        entry_path = os.path.join(directory, entry)
        if os.path.isfile(entry_path):
            total += 1
        elif os.path.isdir(entry_path):
            total += count_files(entry_path)
    return total

def find_metadata(asset_directory_path, starting_path):
    """figure out the Asset Path, Asset Name, Creator, and Asset Type"""
    # Generate a unique ID for the asset
    asset_id = str(uuid.uuid4())
    
    # Get the relative asset path
    asset_path = os.path.relpath(asset_directory_path, starting_path)
    # Get the parent directory name
    asset_name = os.path.basename(asset_directory_path)
    # Get the creator from the beginning of the asset path
    creator = asset_path.split(os.sep)[0]
    # Determine the asset type from the asset path
    asset_types = ["Envirs", "Chars", "DM Swag", "Statue", "Bust", "Bases", "Effects", "Vehicles", "Accessories", "Props","Cards","Maps","Rules","Adventures"]
    asset_type = next((atype for atype in asset_types if atype in asset_path), "Unknown")
    
    # Check for "Supported" and "Unsupported" directories
    supported = "Supported" in os.listdir(asset_directory_path)
    unsupported = "Unsupported" in os.listdir(asset_directory_path)
    
    # Set asset_images_path to the "Images" directory if it isn't empty
    asset_images_path = os.path.join(asset_directory_path, "Images")
    if not os.path.isdir(asset_images_path) or not os.listdir(asset_images_path):
        asset_images_path = ""
    
    # Print the asset path if asset_type is "Unknown"
    if asset_type == "Unknown":
        print(f"Unknown asset type for path: {asset_path}")
    
    return [asset_id, asset_path, asset_name, creator, asset_type, asset_images_path, supported, unsupported]

results = []
starting_path = input("Enter the starting directory path: ")
# Example starting path: Y:\Models\Printable Library\AssetSorted
# Walk through each directory and check for subdirectories of interest
for root, dirs, files in os.walk(starting_path):
    for d in dirs:
        dir_name = os.path.basename(os.path.join(root, d))
        if dir_name in ["Supported", "Unsupported"]:
            subdirectory = os.path.join(root, d)
            file_count = count_files(subdirectory)
            if file_count > 0:
                results.append(f"{root}")

# Remove duplicates from the result list
results = list(set(results))
#print(results)
headers = ["Asset Directory", "Asset ID",  "Asset Path", "Asset Name", "Creator","Asset Type", "Asset Images Path", "Supported", "Unsupported"]
# Save results to a CSV file
with open('asset_paths.csv', 'w', encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(headers)
    for path in results:
        asset_metadata = find_metadata(path, starting_path)
        #print(asset_metadata)
        writer.writerow([path] + asset_metadata)
        
print(f"Asset paths saved to asset_paths.csv")
#print("Parent directories (asset paths) found:")
#for path in results:
#    print(path)

#print("Results saved to result.csv")