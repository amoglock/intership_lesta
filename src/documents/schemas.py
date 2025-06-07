from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    detail: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "detail": "Error message...",
                },
            ]    
        }
    }


class UploadFileResponse(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    filename: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "filename": "file.txt",
                },
            ]    
        }
    }


class DocumentInDB(UploadFileResponse):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    id: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {   
                    "id": 1,
                    "filename": "file.txt",
                },
            ]    
        }
    }

class DocumentContent(DocumentInDB):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    content: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {   
                    "id": 1,
                    "filename": "file.txt",
                    "content": "Some content the document..."
                },
            ]    
        }
    }    
