import os
import shutil
from src.mapping import folder_map

def main():
    img_path = r"C:\Users\polen\OneDrive\Pictures\Screenshots"
    files = os.listdir(img_path)

    moved = 0
    for file in files:
        name, ext = os.path.splitext(file)
        if ext in folder_map:
            moved += 1
            dest_folder = os.path.join(img_path, folder_map[ext])
            os.makedirs(dest_folder, exist_ok=True)

            shutil.move(
               os.path.join(img_path, file),
               os.path.join(dest_folder, file)
            )

            print(f"Moved {file} -> {folder_map[ext]}")

    print(f"Done! Moved {moved} files.")


if __name__ =="__main__":
    main()