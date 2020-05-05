#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.

import flask
import redis

from flask import request

app = flask.Flask(__name__)
r_cli = redis.StrictRedis()


@app.route("/index")
def index_page():
    return "Redis practice!"


@app.route("/redis/display_sset")
def users():
    request_data = request.args.to_dict()
    return str(r_cli.zrange(request_data["base"], 0, -1))


@app.route("/redis/zput", methods=["PUT"])
def put_user():
    request_data = request.args.to_dict()
    if r_cli.zadd(request_data["base"], {request_data["value"]: request_data["score"]}):
        return flask.redirect(f"/redis/display_sset?base={request_data['base']}")
    else:
        return "You did not set valid data or the sorted set already exists!", 400


@app.route("/redis/zdelete", methods=["DELETE"])
def delete_user():
    request_data = request.args.to_dict()
    if r_cli.zrem(request_data["base"], request_data["value"]):
        return flask.redirect(f"/redis/display_sset?base={request_data['base']}")
    else:
        return "You did not set valid data or the sorted set already exists!", 400


@app.route("/redis/zupdate", methods=["PATCH"])
def update_user():
    return "This does not work yet!!!"
    # Find a way to change the score/value, not increment.(update it and don't forget you imbecile)
    # request_data = request.args.to_dict()
    # all_users = r_cli.zrange(request_data["base"], 0, -1)
    #
    # if request_data["value"] in all_users:
    #     r_cli.zadd(request_data["base"], {request_data["value"]: request_data["score"]})
    #     return flask.redirect(f"/redis/display_sset?base={request_data['base']}")
    #
    # else:
    #     return "You did not set valid data or the sorted set already exists!", 404


@app.route("/redis/clear")
def clear_redis():
    r_cli.flushall()
    return "Memory has been cleared! \n All temporary data is removed!"


if "__name__" == "__main__":
    app.run()
