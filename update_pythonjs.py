import os
import zipfile
import urllib.request
import shutil
import filecmp
import tempfile

PYTHONJS_URL = "https://m4rcel.lol/pythonjs/pythonjs.zip"
TARGET_DIR = "pythonjs"
ZIP_NAME = "pythonjs_update.zip"


def download_zip():
    print(f"Downloading latest PythonJS from {PYTHONJS_URL} ...")
    urllib.request.urlretrieve(PYTHONJS_URL, ZIP_NAME)
    print("Download complete.")

def extract_zip(temp_dir):
    print(f"Extracting {ZIP_NAME} ...")
    with zipfile.ZipFile(ZIP_NAME, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    print("Extraction complete.")

def compare_and_update(temp_dir, target_dir):
    updated = []
    added = []
    for root, _, files in os.walk(temp_dir):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), temp_dir)
            src_file = os.path.join(root, file)
            dst_file = os.path.join(target_dir, rel_path)
            dst_dir = os.path.dirname(dst_file)
            if not os.path.exists(dst_file):
                if not os.path.exists(dst_dir):
                    os.makedirs(dst_dir)
                shutil.copy2(src_file, dst_file)
                added.append(rel_path)
            else:
                if not filecmp.cmp(src_file, dst_file, shallow=False):
                    shutil.copy2(src_file, dst_file)
                    updated.append(rel_path)
    return added, updated

def main():
    download_zip()
    with tempfile.TemporaryDirectory() as temp_dir:
        extract_zip(temp_dir)
        # Find the extracted pythonjs folder (in case the zip contains a folder)
        extracted_root = temp_dir
        for name in os.listdir(temp_dir):
            if os.path.isdir(os.path.join(temp_dir, name)) and name.lower() == 'pythonjs':
                extracted_root = os.path.join(temp_dir, name)
                break
        added, updated = compare_and_update(extracted_root, TARGET_DIR)
        print("\nUpdate Summary:")
        if added:
            print(f"  Added: {', '.join(added)}")
        if updated:
            print(f"  Updated: {', '.join(updated)}")
        if not added and not updated:
            print("  All files are up to date.")
    os.remove(ZIP_NAME)
    print("Update complete.")

if __name__ == "__main__":
    main() 