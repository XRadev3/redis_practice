#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.

import flask
import redis_utils

from flask import request

app = flask.Flask(__name__)


@app.route("/index")
def index_page():
    return "Redis practice!"


@app.route("/redis/zdisplay")
def users():
    request_data = request.args.to_dict()
    return str(redis_utils.display_zsets(request_data))


@app.route("/redis/zput", methods=["PUT"])
def put_user():
    request_data = request.args.to_dict()
    if redis_utils.add_ordered_set(request_data):
        return flask.redirect(f"/redis/zdisplay?base={request_data['base']}")
    else:
        return "You did not set valid data or the sorted set already exists!", 400


@app.route("/redis/zdelete", methods=["DELETE"])
def delete_user():
    request_data = request.args.to_dict()
    if redis_utils.remove_ordered_set(request_data):
        return flask.redirect(f"/redis/zdisplay?base={request_data['base']}")
    else:
        return "You did not set valid data or the sorted set already exists!", 400


@app.route("/redis/clear")
def clear_redis():
    redis_utils.clear_redis()
    return "Memory has been cleared! \n All temporary data is removed!"


if "__name__" == "__main__":
    app.run()
