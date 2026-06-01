from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator
import re


class AddressSchema(BaseModel):
    line1: str
    line2: str | None = None
    line3: str | None = None
    town: str
    county: str
    postcode: str


class CreateUserRequest(BaseModel):
    name: str
    address: AddressSchema
    phoneNumber: str
    email: EmailStr
    # password is not in the original OpenAPI spec but is required for JWT auth.
    # This is a deliberate extension — documented in README.
    password: str

    @field_validator("phoneNumber")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^\+[1-9]\d{1,14}$", v):
            raise ValueError("phoneNumber must be in E.164 format, e.g. +447911123456")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("password must be at least 8 characters")
        return v


class UpdateUserRequest(BaseModel):
    name: str | None = None
    address: AddressSchema | None = None
    phoneNumber: str | None = None
    email: EmailStr | None = None

    @field_validator("phoneNumber")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^\+[1-9]\d{1,14}$", v):
            raise ValueError("phoneNumber must be in E.164 format, e.g. +447911123456")
        return v


class UserResponse(BaseModel):
    id: str
    name: str
    address: AddressSchema
    phoneNumber: str
    email: str
    createdTimestamp: datetime
    updatedTimestamp: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, user: object) -> "UserResponse":
        return cls(
            id=user.id,  # type: ignore[attr-defined]
            name=user.name,  # type: ignore[attr-defined]
            address=AddressSchema(
                line1=user.address_line1,  # type: ignore[attr-defined]
                line2=user.address_line2,  # type: ignore[attr-defined]
                line3=user.address_line3,  # type: ignore[attr-defined]
                town=user.address_town,  # type: ignore[attr-defined]
                county=user.address_county,  # type: ignore[attr-defined]
                postcode=user.address_postcode,  # type: ignore[attr-defined]
            ),
            phoneNumber=user.phone_number,  # type: ignore[attr-defined]
            email=user.email,  # type: ignore[attr-defined]
            createdTimestamp=user.created_at,  # type: ignore[attr-defined]
            updatedTimestamp=user.updated_at,  # type: ignore[attr-defined]
        )
