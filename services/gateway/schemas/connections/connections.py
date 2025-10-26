from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class ConnectionResponseSchema(BaseModel):
    id: int = Field(..., description="ID подключения", gt=0)
    label: str = Field(..., description="Название подключения", min_length=1, max_length=100)
    type: str = Field(..., description="Тип подключения", min_length=1, max_length=50)
    href: str = Field(..., description="Ссылка", min_length=1, max_length=500)
    value: str = Field(..., description="Значение", min_length=1, max_length=100)
    
    @field_validator('href')
    @classmethod
    def validate_href(cls, v: str) -> str:
        protocol_pattern = re.compile(
            r'^(https?|mailto|tel|skype|tg)://',
            re.IGNORECASE
        )
        
        if protocol_pattern.match(v):
            return v
        
        if re.match(r'^/', v):
            return v
        
        if re.match(r'^mailto:[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v, re.IGNORECASE):
            return v
        
        raise ValueError('Invalid URL format. Supported formats: http://, https://, mailto:, tel:, skype:, tg://')
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed_types = ['social', 'email']

        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {", ".join(allowed_types)}')

        return v
    
    model_config = {"from_attributes": True}


class ConnectionCreateSchema(BaseModel):
    label: str = Field(..., description="Название подключения")
    type: str = Field(..., description="Тип подключения")
    href: str = Field(..., description="Ссылка")
    value: str = Field(..., description="Значение")


class ConnectionUpdateSchema(BaseModel):
    label: Optional[str] = Field(None, description="Название подключения")
    type: Optional[str] = Field(None, description="Тип подключения")
    href: Optional[str] = Field(None, description="Ссылка")
    value: Optional[str] = Field(None, description="Значение")
