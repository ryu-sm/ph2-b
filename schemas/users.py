from pydantic import BaseModel, Field


class NewUser(BaseModel):
    password: str = Field(min_length=8)
    token: str


class ResetPasswordUser(BaseModel):
    password: str = Field(min_length=8)
    token: str


class UpPasswordUser(BaseModel):
    password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)


class LoginUser(BaseModel):
    email: str = Field(
        max_length=128,
        pattern="^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$",
    )
    password: str = Field(min_length=8)


class UpEmailUser(BaseModel):
    email: str = Field(
        max_length=128,
        pattern="^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$",
    )

    new_email: str = Field(
        max_length=128,
        pattern="^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$",
    )


class UpEmailUserConfirm(BaseModel):
    token: str


class ResetPasswordManager(BaseModel):
    password: str = Field(min_length=8)
    token: str


class LoginManager(BaseModel):
    email: str = Field(
        max_length=128,
        pattern="^[a-zA-Z0-9_+-]+(.[a-zA-Z0-9_+-]+)*@([a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.)+[a-zA-Z]{2,}$",
    )
    password: str = Field(min_length=8)
