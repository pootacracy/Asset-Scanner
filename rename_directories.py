import os

def rename_directories(starting_path):
    for root, dirs, files in os.walk(starting_path):
        for d in dirs:
            if '_' in d:
                old_dir_path = os.path.join(root, d)
                new_dir_name = d.replace('_', ' ')
                if new_dir_name.startswith(' '):
                    new_dir_name = new_dir_name.lstrip()  # Remove leading spaces
                new_dir_path = os.path.join(root, new_dir_name)
                try:
                    os.rename(old_dir_path, new_dir_path)
                    print(f"Renamed: {old_dir_path} -> {new_dir_path}")
                except FileExistsError:
                    print(f"Error: The directory '{new_dir_path}' already exists. Original directory: {old_dir_path}")

if __name__ == "__main__":
    starting_path = input("Enter the starting directory path: ")
    rename_directories(starting_path)
    print("Operation completed.")
