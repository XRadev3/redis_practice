import flask

from application.ftp_comm import get_json_from_file
from werkzeug.security import generate_password_hash, check_password_hash


def check_password(username, password):
    """
    Asserts if the given password is equal to the actual password.
    Returns True if successful,
    otherwise returns False.
    """
    try:
        user_data = get_json_from_file(username)
        user_pass = user_data[username]['attributes']['password']

        if check_key(user_pass, password):
            return True

    except Exception as message:
        return False


def is_logged():
    try:
        if flask.session['username']:
            return True

    except Exception as message:
        return False


def secure_key(key=str()):
    """
    Encrypts the given security key.
    Returns the encrypted key.
    """
    encrypted_key = generate_password_hash(key)
    return encrypted_key


def check_key(encrypted_key=str(), input_key=str()):
    """
    Checks if the given encrypted_key is equal to the decrypted input_key, if so, returns True.
    Returns False if the keys are different.
    """
    bingo = check_password_hash(encrypted_key, input_key)
    return bingo
