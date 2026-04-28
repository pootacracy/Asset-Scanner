import os
import shutil

def scan_empty_directories(starting_path):
    matching_directories = []

    for root, dirs, files in os.walk(starting_path):
        for d in dirs:
            dir_path = os.path.join(root, d)
            dir_files = os.listdir(dir_path)
            if not dir_files or (len(dir_files) == 1 and dir_files[0] == "config.orynt3d"):
                matching_directories.append(dir_path)

    return matching_directories

def delete_directories(directories):
    for directory in directories:
        print(f"Contents of {directory}:")
        for item in os.listdir(directory):
            print(f"  {item}")
        shutil.rmtree(directory)
        print(f"Deleted: {directory}")

if __name__ == "__main__":
    starting_path = input("Enter the starting directory path: ")
    results = scan_empty_directories(starting_path)
    delete_directories(results)
    print("Operation completed.")
