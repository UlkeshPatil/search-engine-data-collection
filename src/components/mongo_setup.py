import os
import sys
from src.utils.database_handler import MongodbClient
from src.exception import CustomException

class MetaDataStore:
    """
    Class for managing metadata registration in a MongoDB database.

    Attributes:
        root (str): Root directory for data storage.
        images (str): Path to the directory containing images.
        labels (list): List of labels extracted from the image directory.
        mongo (MongodbClient): Instance of the MongodbClient for database interaction.
    """

    def __init__(self):
        self.root = os.path.join(os.getcwd(), "data")
        self.images = os.path.join(self.root, "caltech-101")
        self.labels = os.listdir(self.images)
        self.mongo = MongodbClient()

    def register_labels(self):
        """
        Register labels in the MongoDB database.

        Returns:
            dict: Result of the label registration process (created, reason).
        """
        try:
            records = {}
            for num, label in enumerate(self.labels):
                records[f"{num}"] = label

            self.mongo.database['labels'].insert_one(records)
            return {"Created": True}
        except Exception as e:
            message = CustomException(e, sys)
            return {"Created": False, "Reason": message.error_message}

    def run_step(self):
        """
        Execute the label registration process.

        Returns:
            dict: Result of the label registration process (created, reason).
        """
        try:
            self.register_labels()
            return {"Created": True}
        except Exception as e:
            message = CustomException(e, sys)
            return {"Created": False, "Reason": message.error_message}

if __name__ == "__main__":
    meta = MetaDataStore()
    meta.run_step()

