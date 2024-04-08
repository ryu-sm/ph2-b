from passlib.context import CryptContext

__pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# def hash_password(plain_password):
#     return __pwd_context.hash(plain_password)


# def verify_password(plain_password, hashed_password):
#     return __pwd_context.verify(plain_password, hashed_password)

import bcrypt


def hash_password(plain_password):
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
