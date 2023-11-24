import os
import sys
from zipfile import ZipFile
import shutil
from src.exception import CustomException

class DataStore:
    """
    Class for managing data extraction, cleanup, and synchronization.

    Attributes:
        root (str): Root directory for data storage.
        zip (str): Path to the zip file containing data.
        images (str): Path to the directory containing images.
        unwanted_classes (list): List of classes to be removed from the dataset.
    """

    def __init__(self):
        self.root = os.path.join(os.getcwd(), "data")
        self.zip = os.path.join(self.root, "archive.zip")
        self.images = os.path.join(self.root, "caltech-101")
        self.unwanted_classes = ["BACKGROUND_Google"]

    def prepare_data(self):
        """
        Extract data from the zip file.
        
        Returns:
            dict: Result of the data extraction process (created, reason).
        """
        try:
            print("Extracting Data")
            with ZipFile(self.zip, 'r') as files:
                files.extractall(path=self.root)
            print("Process Completed")
            return {"Created": True}
        except Exception as e:
            message = CustomException(e, sys)
            return {"Created": False, "Reason": message.error_message}

    def remove_unwanted_classes(self):
        """
        Remove unwanted classes from the dataset.
        
        Returns:
            dict: Result of the removal process (created, reason).
        """
        try:
            print("Removing unwanted classes")
            for label in self.unwanted_classes:
                path = os.path.join(self.images, label)
                shutil.rmtree(path, ignore_errors=True)
            print("Process Completed")
            return {"Created": True}
        except Exception as e:
            message = CustomException(e, sys)
            return {"Created": False, "Reason": message.error_message}

    def sync_data(self):
        """
        Synchronize data with an AWS S3 bucket.
        
        Returns:
            dict: Result of the synchronization process (created, reason).
        """
        try:
            print("\n====================== Starting Data sync ==============================\n")
            os.system(f"aws s3 sync {self.images} s3://image-search-data/images/")
            print("\n====================== Data sync Completed ==========================\n")
            return {"Created": True}
        except Exception as e:
            message = CustomException(e, sys)
            return {"Created": False, "Reason": message.error_message}

    def run_step(self):
        """
        Execute the complete data preparation and synchronization process.
        
        Returns:
            bool: True if the process completes successfully, False otherwise.
        """
        try:
            self.prepare_data()
            self.remove_unwanted_classes()
            self.sync_data()
            return True
        except Exception as e:
            message = CustomException(e, sys)
            return {"Created": False, "Reason": message.error_message}

if __name__ == "__main__":
    data_store = DataStore()
    data_store.run_step()

