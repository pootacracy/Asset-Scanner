import os
import csv

def traverse_directory(directory):
    """Traverse a directory and yield each entry."""
    for entry in os.listdir(directory):
        entry_path = os.path.join(directory, entry)
        if os.path.isdir(entry_path):
            yield entry_path

def main():
    #Y:\Models\Printable Library\AssetSorted
    # Get starting directory from user input or default
    start_dir = input("Enter the starting directory path: ")
    
    results = []
    
    for dir_path in traverse_directory(start_dir):
        # Check if any of "Images", "Supported", "Unsupported" are present as subdirectories
        for subdir_name in ["Images", "Supported", "Unsupported"]:
            subdir_path = os.path.join(dir_path, subdir_name)
            # Ensure the subdir exists and is a directory
            print(subdir_path)
            if os.path.isdir(subdir_path) and len(os.listdir(subdir_path)) > 0:
                parent_dir = dir_path
                results.append(parent_dir)
                break
    
    # Remove duplicates by using set
    unique_asset_paths = list(set(results))
    
    # Prepare the CSV header
    headers = ["Parent Directory"]
    
    if not unique_asset_paths:
        print("No asset paths found.")
    else:
        with open('asset_paths.csv', 'w', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for path in unique_asset_paths:
                writer.writerow([path])
        
        print(f"Asset paths saved to asset_paths.csv")
        print("Parent directories (asset paths) found:")
        for path in unique_asset_paths:
            print(path)

if __name__ == "__main__":
    main()