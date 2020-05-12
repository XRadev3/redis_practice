#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.
from os import environ

from auth import require_auth
import flask
import redis_utils

from flask import request

app = flask.Flask(__name__)


@app.route("/index")
def index_page():
    return "Redis practice!"


@app.route("/redis/display/s_set")
@require_auth()
def users():
    request_data = request.args.to_dict()
    return str(redis_utils.display_zsets(request_data))


@app.route("/redis/display/s_set/key")
def user():
    request_data = request.args.to_dict()
    response = flask.Response()
    key = request_data['key']
    sorted_set = request_data['base']

    response_data = redis_utils.get_key_from_ordered_set(sorted_set, key)
    response.data = response_data['data']
    response.status_code = response_data['status']

    return response


@app.route("/redis/zput", methods=["PUT"])
@require_auth()
def put_user():
    request_data = request.args.to_dict()

    if request_data:  # redis_utils.add_ordered_set(request_data):
        value = "key"
        response = flask.redirect("/redis/display/s_set", code=200)
        response.headers.add(value, request.headers['User'])
        import pdb;pdb.set_trace()
        print("asdas")
        return response.response
    else:
        return "You did not set valid data or the sorted set already exists!", 400


@app.route("/redis/zdelete", methods=["DELETE"])
@require_auth()
def delete_user():
    request_data = request.args.to_dict()
    response = flask.Response()

    if redis_utils.remove_ordered_set(request_data):
        response.status_code = 200
        response.headers = request.headers

        return flask.redirect(f"/redis/display/s_set?base={request_data['base']}", code=200, Response=response)

    else:
        return "You did not set valid data or the sorted set already exists!", 400


@app.route("/redis/clear")
@require_auth()
def clear_redis():
    redis_utils.clear_redis()
    return "Memory has been cleared! \n All temporary data is removed!"


if "__name__" == "__main__":
    app.run()
