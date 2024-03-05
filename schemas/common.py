import typing
from pydantic import BaseModel, Field


class VerifyEmail(BaseModel):
    email: str = Field(
        max_length=128,
        pattern="^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$",
    )
    s_sales_company_org_id: typing.Optional[str] = None
