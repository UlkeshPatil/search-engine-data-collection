import os
import base64
from from_root import from_root
from tqdm import tqdm

def upload_bulk_data(root="caltech-101"):
    """
    Upload data using boto3.

    This function reads images from the specified directory and converts them to base64 format.

    Args:
        root (str): The root directory containing subdirectories for each label.

    Returns:
        None
    """
    labels = os.listdir(root)
    for label in tqdm(labels, desc="Processing Labels"):
        data = []
        images = os.listdir(os.path.join(root, label))
        for img in tqdm(images, desc=f"Processing Images for {label}"):
            path = os.path.join(from_root(), root, label, img)
            with open(rf"{path}", "rb") as img_file:
                data.append(base64.b64encode(img_file.read()).decode())

    print("\nCompleted")

if __name__ == "__main__":
    upload_bulk_data(root="caltech-101")

