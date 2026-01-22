from pydantic import BaseModel
from typing import Dict

class ExtractedData(BaseModel):
    name: str = ""
    fatherName: str = ""
    dateOfBirth: str = ""
    address: str = ""
    city: str = ""
    state: str = ""
    pincode: str = ""
    phone: str = ""
    email: str = ""
    idNumber: str = ""
    gender: str = ""

class FillRequest(BaseModel):
    formPath: str
    data: Dict[str, str]

class URLFillRequest(BaseModel):
    url: str
    data: Dict[str, str]