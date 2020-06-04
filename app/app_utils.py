import os
import json
import secrets

users_file = os.getcwd() + '/local_storage/users.txt'
api_keys = os.getcwd() + '/local_storage/api_keys.txt'


# Writes a given json data to a file. If unsuccessful the function will return false, otherwise true.
def append_json_to_file(json_data):
    try:
        json_data = set_api_key(json_data)
        with open(users_file, 'a') as output_file:
            output_file.write("\n")
            json.dump(json_data, output_file)
            return True

    except Exception as message:
        return False


# Writes a given json data to a file. If unsuccessful the function will return false, otherwise true.
def del_json_from_file(key):
    try:
        with open(users_file, "r") as input_file:
            lines = input_file.readlines()

        with open(users_file, "w") as output_file:
            for line in lines:
                if key not in line and line != "\n":
                    output_file.write(line)

        return True

    except Exception as message:
        return False


# Reads a given json file to a json object.
# If unsuccessful the function will return false, otherwise the requested object.
def get_json_from_file(key):

    try:
        with open(users_file, 'r') as input_file:

            for line in input_file:
                if line == "\n":
                    pass
                elif key in line:
                    json_data = json.loads(line)
                    return json_data

    except Exception as message:
        return False

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
        return False


def get_api_key(key):
    try:
        json_data = get_json_from_file(key)
        nested_dict = list(json_data.values())[0]
        user_data_key = list(nested_dict.keys())[0]
        api_key = nested_dict[user_data_key]['API_KEY']

        return api_key

    except Exception as message:
        return False
