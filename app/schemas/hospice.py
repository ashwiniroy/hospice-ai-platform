from pydantic import BaseModel
from typing import Optional


class HospiceResponse(BaseModel):
    enrollment_id: Optional[str] = None
    enrollment_state: Optional[str] = None
    provider_type_code: Optional[str] = None
    provider_type_text: Optional[str] = None
    npi: Optional[int] = None
    multiple_npi_flag: Optional[str] = None
    ccn: Optional[str] = None
    associate_id: Optional[int] = None
    organization_name: Optional[str] = None
    doing_business_as_name: Optional[str] = None
    incorporation_date: Optional[str] = None
    incorporation_state: Optional[str] = None
    organization_type_structure: Optional[str] = None
    organization_other_type_text: Optional[str] = None
    proprietary_nonprofit: Optional[str] = None
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[int] = None

class HospiceListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    data: list[HospiceResponse]