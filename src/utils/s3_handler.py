import os
import sys
import boto3
from typing import Dict
from src.utils.utils import image_unique_name
from src.exception import CustomException

class S3Connection:
    """Data Class for reverse image search engine."""

    def __init__(self):
        # Initialize the S3 connection using AWS credentials
        session = boto3.Session(
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )
        self.s3 = session.resource("s3")
        self.bucket = self.s3.Bucket(os.environ["AWS_BUCKET_NAME"])

    def add_label(self, label: str) -> Dict:
        """
        This function adds a label in the S3 bucket.
        :param label: Label name
        :return: JSON response with the state message (success or failure)
        """
        try:
            key = f"images/{label}/"
            response = self.bucket.put_object(Body="", Key=key)
            return {"Created": True, "Path": response.key}
        except Exception as e:
            message = CustomException(e, sys)
            return {"Created": False, "Reason": message.error_message}

    def upload_to_s3(self, image_path, label: str):
        """
        This function uploads images to the predefined location in the S3 bucket.
        :param label: Label name
        :param image_path: Path to the image to upload
        :return: JSON response with the state message (success or failure)
        """
        try:
            self.bucket.upload_fileobj(
                image_path,
                f"images/{label}/{image_unique_name()}.jpeg",
                ExtraArgs={"ACL": "public-read"},
            )
            return {"Created": True}
        except Exception as e:
            message = CustomException(e, sys)
            return {"Created": False, "Reason": message.error_message}

