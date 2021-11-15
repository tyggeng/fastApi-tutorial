from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(user_input):
    return pwd_context.hash(user_input)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
