import os
import csv

def main():
    # Define the path to starting directory
    start_dir = input("Enter the starting directory path: ")
    
    # List to store unique parent directories with valid subdirectories
    results = []
    
    # Get all entries in the starting directory (files and directories)
    entry_list = os.listdir(start_dir)
    
    for entry in entry_list:
        # Skip directories that are not files
        if os.path.isdir(os.path.join(start_dir, entry)):
            # Check each subdirectory for "Images", "Supported", or "Unsupported"
            subdir_name = entry
            
            # List to store paths of child directories with images
            child_directories = []
            
            # Get all entries in the subdirectory
            child_entry_list = os.listdir(os.path.join(start_dir, subdir_name))
            
            # Check each child entry
            for child_entry in child_entry_list:
                if os.path.isdir(os.path.join(os.path.join(start_dir, subdir_name), child_entry)):
                    child_directories.append(child_entry)
            
            # Add parent directories without duplicates
            unique_dirs = set()
            for dir in child_directories:
                dir_path = os.path.join(start_dir, subdir_name, dir)
                if dir not in unique_dirs and os.path.isdir(dir_path):
                    results.append(dir)
                    unique_dirs.add(dir)
    
    # Save to CSV file if there are results
    if len(results) > 0:
        with open('result.csv', 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(["Parent Directory"])
            for result in results:
                writer.writerow([result])
        
        print(f"Results saved to result.csv")
    else:
        print("No directories found with Images, Supported, or Unsupported subdirectories.")

if __name__ == "__main__":
    main()
