from flask_bcrypt import Bcrypt
encrypter = Bcrypt()

def encode_password(password):
    return encrypter.generate_password_hash(password).decode("utf-8")

def verify_encoded_password(password_econded, common_password):
    return encrypter.check_password_hash(password_econded, common_password)