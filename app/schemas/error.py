from pydantic import BaseModel


class ErrorResponse(BaseModel):
    message: str


class BadRequestErrorDetail(BaseModel):
    field: str
    message: str
    type: str


class BadRequestErrorResponse(BaseModel):
    message: str
    details: list[BadRequestErrorDetail]
