import os
import shutil

def move_images_to_folder(starting_path):
    image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
    
    for root, dirs, files in os.walk(starting_path):
        for d in dirs:
            if d in ["Unsupported", "Supported"]:
                #dir_path = os.path.join(root, d)
                dir_path=root
                image_files = [f for f in os.listdir(dir_path) if f.lower().endswith(image_extensions)]
                #print(f"checked ", dir_path)
                #print(f"d=",d)
                #print(f"root=",root)
                if image_files:
                    images_folder = os.path.join(dir_path, "Images")
                    os.makedirs(images_folder, exist_ok=True)
                    print(f"Created images_folder {images_folder}")
                    for image_file in image_files:
                        src_path = os.path.join(dir_path, image_file)
                        dest_path = os.path.join(images_folder, image_file)
                        shutil.move(src_path, dest_path)
                        print(f"Moved {src_path} to {dest_path}")

if __name__ == "__main__":
    starting_path = input("Enter the starting directory path: ")
    move_images_to_folder(starting_path)
    print("Operation completed.")