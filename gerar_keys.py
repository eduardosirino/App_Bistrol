import os

def generate_secret_key():
    return os.urandom(24).hex()

print("FLASK_SECRET_KEY:", generate_secret_key())
