import os
import json
import secrets
import logging

from werkzeug.security import generate_password_hash, check_password_hash

users_file = os.getcwd() + '/local_storage/users.txt'
group_file = os.getcwd() + '/local_storage/groups.txt'


def secure_key(key=str()):
    """
    Encrypts the given security key.
    Returns the encrypted key.
    """
    encrypted_key = generate_password_hash(key)
    return encrypted_key


def check_key(encrypted_key=str(), input_key=str()):
    """
    Checks if the given encrypted_key is equal ot the decrypted input_key.
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
        json_data = set_api_key(json_data)
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
                if key not in line and line != "\n":
                    output_file.write(line)

        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def get_json_from_file(key):
    """
    key -> dict key(string)
    Returns a line from a file the holds the given key,
    otherwise False.
    """

    try:
        with open(users_file, 'r') as input_file:

            for line in input_file:
                if line == "\n":
                    pass
                elif key in line:
                    json_data = json.loads(line)
                    return json_data

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False

    return False


def get_group_info(user_data=dict(), all_groups=False):
    """
    user_data -> dict(string)
    Returns the key value pairs of a group
    or if all_groups is True, all groups.
    otherwise False.
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


def update_group(group, new_values):
    """
    group -> dict key(string)
    new_values -> dict value(dict)
    Updates a group's values.
    If successful, return True,
    otherwise False.
    """
    try:
        with open(group_file, 'r') as text_file:
            line = text_file.readline()
            line = json.loads(line)

        line[group] = new_values

        with open(group_file, 'w') as output_file:
            output_file.write(json.dumps(line))

        return True

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def set_api_key(json_data):
    try:
        nested_dict = list(json_data.values())[0]
        user_key = list(json_data.keys())[0]
        user_data_key = list(nested_dict.keys())[0]
        api_key = secrets.token_urlsafe()

        nested_dict[user_data_key].update({'API_KEY': api_key})
        output_json = {user_key: nested_dict}

        return output_json

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False


def get_api_key(key):
    try:
        json_data = get_json_from_file(key)
        nested_dict = list(json_data.values())[0]
        user_data_key = list(nested_dict.keys())[0]
        api_key = nested_dict[user_data_key]['API_KEY']

        return api_key

    except Exception as message:
        logging.log(logging.ERROR, str(message))
        return False
