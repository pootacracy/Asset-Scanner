import csv
import os

def update_asset_images_path(csv_file_path):
    updated_rows = []
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames
        for row in reader:
            if not row["Asset Images Path"]:
                row["Asset Images Path"] = os.path.join(row["Asset Directory"], "Images")
            updated_rows.append(row)
    
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

if __name__ == "__main__":
    csv_file_path = 'asset_paths.csv'  # Update this path if necessary
    update_asset_images_path(csv_file_path)
    print(f"Updated 'Asset Images Path' in {csv_file_path}")