from pydantic import BaseModel
from typing import List


class DocumentInCollection(BaseModel):
    """Schema for document in collection response"""
    id: int
    filename: str


class CollectionResponse(BaseModel):
    """Schema for collection response"""
    id: int
    name: str
    documents: List[DocumentInCollection]
