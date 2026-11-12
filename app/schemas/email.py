from pydantic import BaseModel, ConfigDict, EmailStr, Field

class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sender: EmailStr
    subject: str = Field(min_length=2, max_length=200)
    body: str = Field(min_length=5, max_length=10000)
