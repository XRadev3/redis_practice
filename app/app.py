#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.

import flask
from app import config
from flask import request, render_template, flash

from redis_utils.redis_minion import RedisMinion
from app.forms import *
from app.auth import require_auth
from redis_utils import redis_utils as redis_utils

app = flask.Flask(__name__)
app.config.from_mapping(config.app_config())


@app.route("/index")
def index_page():
    return render_template('base.html')


@app.route("/login", methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    title = 'Redis Login'

    return render_template('login.html', title=title, form=form)


@app.route("/user/home_page")
# @require_auth()
def user_page():
    request_args = request.args.to_dict()
    title = 'User Page'
    response = redis_utils.hget(request_args['hash_name'], request_args['hash_key'])

    return render_template("user_home.html", title=title, name=response['data'])


@app.route("/user/create", methods=['GET', 'POST'])
def create_user():
    form = CreateUserForm()
    title = "User creation panel."

    if form.validate_on_submit():
        user_data_dict = {
            'email': form.email.data,
            'password': form.password.data,
            'group': form.group.data
        }
        response = redis_utils.hset(form.username.data, form.name.data, user_data_dict)

        if isinstance(response['data'], bool):
            return flask.redirect(f'/user/home_page?hash_name={form.username.data}'
                                  f'&hash_key={form.name.data}',
                                  response['status'])

    return render_template("create_user.html", title=title, form=form)


@app.route("/user/put")
# @require_auth()
def add_user():
    request_args = request.args.to_dict()
    response = redis_utils.hset(request_args['hash_name'], request_args['hash_key'], request_args['hash_map'])

    if isinstance(response['data'], bool):
        return flask.redirect(f'/user/home_page?hash_name={request_args["hash_name"]}'
                              f'&hash_key={request_args["hash_key"]}',
                              response['status'])

    return response['data'], response['status']


@app.route("/user/delete")
def rem_user():
    request_data = request.args.to_dict()
    response = redis_utils.hdel(request_data['hash_name'], request_data['hash_key'])
    if isinstance(response['data'], bool):
        return "User was successfully deleted!", response['status']

    return response['data'], response['status']


@app.route("/user/all")
def hget_all():
    request_data = request.args.to_dict()
    response = redis_utils.hgetall(request_data['hash_name'])
    response_data = ['data', 'status']

    if isinstance(response[response_data[0]], bool):
        return response[response_data[0]], response[response_data[1]]

    return response[response_data[0]], response[response_data[1]]


@app.route("/redis/display/s_set")
@require_auth()
def display_sset():
    request_data = request.args.to_dict()
    return str(redis_utils.zrange(request_data))


@app.route("/redis/display/s_set/key")
def display_sset_key():
    request_data = request.args.to_dict()
    response = flask.Response()
    key = request_data['key']
    sorted_set = request_data['base']

    response_data = redis_utils.zrange_singular(sorted_set, key)
    response.data = response_data['data']
    response.status_code = response_data['status']

    return response


@app.route("/redis/zput", methods=["PUT"])
@require_auth()
def put_sset():
    request_data = request.args.to_dict()

    if request_data:  # redis_utils.add_ordered_set(request_data):
        value = "key"
        response = flask.redirect("/redis/display/s_set?base=users")
        response.headers.add('User', 'Hristo')
        response.status_code = 200
        # response = response.get_wsgi_response(request.environ)
        import pdb;
        pdb.set_trace()
        print("asdas")
        return response
    else:
        return "You did not set valid data or the sorted set already exists!", 400


@app.route("/redis/zdelete", methods=["DELETE"])
@require_auth()
def delete_sset_key():
    request_data = request.args.to_dict()
    response = flask.Response()

    if redis_utils.zrem(request_data):
        response.status_code = 200
        response.headers = request.headers

        return flask.redirect(f"/redis/display/s_set?base={request_data['base']}", code=200, Response=response)

    else:
        return "You did not set valid data or the sorted set already exists!", 400


@app.route("/redis/clear")
@require_auth()
def clear_redis():
    redis_utils.flushall()
    return "Memory has been cleared! \n All temporary data is removed!"


if "__name__" == "__main__":
    app.run()
