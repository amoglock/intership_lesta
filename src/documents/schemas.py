from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    detail: str



class UploadFileResponse(BaseModel):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    filename: str

    class Config:
        from_attributes = True


class DocumentInDB(UploadFileResponse):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    id: int


class DocumentContent(DocumentInDB):
    """_summary_

    Args:
        BaseModel (_type_): _description_
    """
    content: str
    
    class Config:
        from_attributes = True
