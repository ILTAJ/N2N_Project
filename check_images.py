from PIL import Image
import os

def check_images(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                img = Image.open(file_path)
                img.verify()  # Verify that it is, in fact, an image
            except (IOError, SyntaxError):
                print(f"Corrupted image detected and skipped: {file_path}")
                os.remove(file_path)  # Optional: Remove corrupted files

# Run the check on both training and validation directories
check_images("data\Cat")
check_images("data\Dog")