from src.utils.database_handler import MongodbClient
from src.utils.s3_handler import S3Connection
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Union, Any
import uvicorn

app = FastAPI(title="DataCollection-Server")
mongo = MongodbClient()
s3 = S3Connection()
choices = {}


@app.get("/fetch")
def fetch_label():
    """
    Fetch all labels from MongoDB.

    Returns:
        JSONResponse: Response containing the labels.
    """
    try:
        global choices
        result = mongo.database['labels'].find()
        documents = [document for document in result]
        choices = dict(documents[0])
        response = {"Status": "Success", "Response": str(documents[0])}
        return JSONResponse(content=response, status_code=200, media_type="application/json")
    except Exception as e:
        raise e


@app.post("/add_label/{label_name}")
def add_label(label_name: str):
    """
    Add a new label to MongoDB and S3.

    Args:
        label_name (str): The name of the label to add.

    Returns:
        dict: Status of the operation.
    """
    try:
        result = mongo.database['labels'].find()
        documents = [document for document in result]
        last_value = list(map(int, list(documents[0].keys())[1:]))[-1]
        response = mongo.database['labels'].update_one(
            {"_id": documents[0]["_id"]},
            {"$set": {str(last_value + 1): label_name}}
        )
        if response.modified_count == 1:
            response = s3.add_label(label_name)
            return {"Status": "Success", "S3-Response": response}
        else:
            return {"Status": "Fail", "Message": response[1]}
    except Exception as e:
        return {"Status": "Fail", "Message": str(e)}


@app.get("/single_upload/")
def single_upload_info():
    """
    Provide information about the single upload endpoint.

    Returns:
        JSONResponse: Information about the endpoint.
    """
    info = {"Response": "Available", "Post-Request-Body": ["label", "Files"]}
    return JSONResponse(content=info, status_code=200, media_type="application/json")


@app.post("/single_upload/")
async def single_upload(label: str, file: UploadFile = File(...)):
    """
    Upload a single image to S3.

    Args:
        label (str): The label for the image.
        file (UploadFile): The image file to upload.

    Returns:
        dict: Response containing filename, label, and S3-Response.
    """
    try:
        label = choices.get(label, False)
        if file.content_type == "image/jpeg" and label:
            response = s3.upload_to_s3(file.file, label)
            return {"filename": file.filename, "label": label, "S3-Response": response}
        else:
            return {
                "ContentType": f"Content type should be Image/jpeg not {file.content_type}",
                "LabelFound": label,
            }
    except Exception as e:
        return {"Error": str(e)}


@app.get("/bulk_upload")
def bulk_upload_info():
    """
    Provide information about the bulk upload endpoint.

    Returns:
        JSONResponse: Information about the endpoint.
    """
    info = {"Response": "Available", "Post-Request-Body": ["label", "Files"]}
    return JSONResponse(content=info, status_code=200, media_type="application/json")


@app.post("/bulk_upload")
def bulk_upload(label: str, files: List[UploadFile] = File(...)):
    """
    Upload multiple images to S3 in bulk.

    Args:
        label (str): The label for the images.
        files (List[UploadFile]): List of image files to upload.

    Returns:
        dict: Response containing label, skipped files, S3-Response, and LabelFound.
    """
    try:
        skipped = []
        final_response = None
        label = choices.get(label, False)
        if label:
            for file in files:
                if file.content_type == "image/jpeg":
                    response = s3.upload_to_s3(file.file, label)
                    final_response = response
                else:
                    skipped.append(file.filename)
            return {
                "label": label,
                "skipped": skipped,
                "S3-Response": final_response,
                "LabelFound": label,
            }
        else:
            return {
                "label": label,
                "skipped": skipped,
                "S3-Response": final_response,
                "LabelFound": label,
            }
    except Exception as e:
        return {"Error": f"Content type should be Image/jpeg not {e}"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

