import os

SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1"


def generate_secret_key(length=32):
    return os.urandom(length).hex()


# SECRET_KEY = generate_secret_key()
SECRET_KEY = "sdaksd$$%%asd@@jsdljka435345hsdohssasjld"