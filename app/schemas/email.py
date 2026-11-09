from pydantic import BaseModel, EmailStr, Field


class EmailRequest(BaseModel):
    sender: EmailStr

    subject: str = Field(
        min_length=2, max_length=200, description="Subject of the customer's email"
    )

    body: str = Field(
        min_length=5, max_length=10000, description="Content of the customer's email"
    )
