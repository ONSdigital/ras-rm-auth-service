from passlib.context import CryptContext

pwd_context = CryptContext(
    schemes=["bcrypt", ],
    default="bcrypt",
    bcrypt__default_rounds=12,
)
