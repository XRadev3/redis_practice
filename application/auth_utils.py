import os
import json
import flask
import secrets

import logging

from application.config import cache
from werkzeug.security import generate_password_hash, check_password_hash

users_file = os.getcwd() + '/application/local_storage/users.txt'
group_file = os.getcwd() + '/application/local_storage/groups.txt'


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


def check_group(username):
    """
    Asserts if the user is in the admin group,
    if so returns True, otherwise returns False.
    """
    if not get_item_field(username, 'group') == 'admin':
        flask.abort(flask.redirect(flask.url_for('index'), 401))


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
    Checks if the given encrypted_key is equal ot the decrypted input_key, if so, returns True.
    Returns False if the keys are different.
    """
    bingo = check_password_hash(encrypted_key, input_key)
    return bingo


def append_json_to_file(json_data):
    """
    json_data -> data to write(dict)
    Writes the given data to the file on a new line.
    If successful returns True,
    otherwise returns False.
    """

    try:
        with open(users_file, 'a') as output_file:
            output_file.write("\n")
            json.dump(json_data, output_file)
            return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def del_json_from_file(key):
    """
    key -> dict key(string)
    Deletes a line from a file the holds the given key.
    If successful, return True,
    otherwise False.
    """

    try:
        with open(users_file, "r") as input_file:
            lines = input_file.readlines()

        with open(users_file, "w") as output_file:
            for line in lines:
                if line != "\n" and not in_dict(key, json.loads(line), check_key=True):
                    output_file.write(line)

        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def get_json_from_file(key=str(), all_items=False):
    """
    key -> dict key(string)
    Returns a line from a file the holds the given key,
    otherwise returns False.
    """
    try:
        with open(users_file, 'r') as input_file:
            if all_items:
                item_dict = dict()
                for line in input_file:
                    if line != "\n":
                        item_dict.update(json.loads(line))

                return item_dict

            for line in input_file:
                if line != "\n" and key in line:
                    json_data = json.loads(line)
                    if in_dict(key, json_data) or in_dict(key, json_data, check_key=True):
                        return json_data

    except Exception as message:
        logging.log(logging.CRITICAL, str(message))
        return False

    return False


def get_item_field(key, field_to_find):
    """
    key -> dict key (string)
    field_to_find -> dict key(string)
    Returns the value from the given field if successful,
    otherwise returns False.
    """
    try:
        item_data = get_json_from_file(key)
        field_value = item_data[key][cache.item_hash_field][field_to_find]
        return field_value

    except Exception as message:
        logging.log(40, message)
        return False


def get_group_info(user_data=dict(), all_groups=False):
    """
    user_data -> dict(string)
    Returns the key value pairs of a group
    or if all_groups is True, returns all the groups,
    otherwise returns False.
    """
    try:
        with open(group_file, 'r') as text_file:
            line = text_file.readline()
            read_data = json.loads(line)
            if all_groups:
                return read_data

            group = user_data['group']
            return read_data[group]

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def update_group(group=str(), new_values=dict(), new_group=str()):
    """
    group -> dict key(string)
    new_values -> dict value(dict)
    new_group -> dictionary
    Updates a group's values or if new_group is given, creates a new group.
    If successful, return True,
    otherwise False.
    """
    try:
        with open(group_file, 'r') as text_file:
            line = text_file.readline()
            line = json.loads(line)

        if new_group:
            line.update(new_group)
            with open(group_file, 'w') as output_file:
                output_file.write(json.dumps(line))

            return True

        line[group] = new_values

        with open(group_file, 'w') as output_file:
            output_file.write(json.dumps(line))

        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def refresh_api_key(json_data):
    """
    Refreshes the current API_KEY set to the user data.
    If successful returns dict with the user data and updated API_KEY,
    otherwise returns False.
    """
    try:
        dict_to_check = list(json_data.values())[0]
        user_key = list(json_data.keys())[0]
        user_data_key = list(dict_to_check.keys())[0]
        api_key = secrets.token_urlsafe()

        dict_to_check[user_data_key].update({'API_KEY': api_key})

        output_json = {user_key: dict_to_check}

        return output_json

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def generate_api_key():
    """
    Generates a secure API_KEY.
    Returns the generated string.
    """
    api_key = secrets.token_urlsafe(16)
    return api_key


def get_api_key(json_key):
    """
    Reads the user data from the storage and returns the API_KEY.
    If successful returns string,
    otherwise returns False.
    """
    try:
        json_data = get_json_from_file(json_key)
        dict_to_check = list(json_data.values())[0]
        user_data_key = list(dict_to_check.keys())[0]
        api_key = dict_to_check[user_data_key]['API_KEY']

        return api_key

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def check_api_key_exists(api_key, get_owner=False):
    try:
        with open(users_file, 'r') as input_file:
            for line in input_file:
                if api_key in line:
                    if get_owner:
                        json_data = json.loads(line)
                        user_key = list(json_data.keys())[0]
                        return user_key

                    return True

    except Exception as message:
        logging.log(logging.INFO, str(message))
        return False


def in_dict(item_to_check, dict_to_check, check_key=False):
    """
    Iterates through a dictionary and its nested(two max) and checks if
    item_to_check is present as a value or if check_key is given, a key.
    Returns True if the variable is present, otherwise returns False.
    """

    # Main dictionary
    for key in dict_to_check:
        if check_key:
            if item_to_check == key:
                return True

        elif item_to_check == dict_to_check[key]:
            return True

        # Nested dictionary
        for nested_key in dict_to_check[key]:
            if check_key:
                if item_to_check == nested_key:
                    return True

            elif item_to_check == dict_to_check[key][nested_key]:
                return True

            # Nested in nested dictionary
            for inner_key in dict_to_check[key][nested_key]:
                if check_key:
                    if item_to_check == inner_key:
                        return True

                elif item_to_check == dict_to_check[key][nested_key][inner_key]:
                    return True

    # If nothing is found, return False.
    return False
