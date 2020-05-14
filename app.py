#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.
from os import environ

from auth import require_auth, LoginForm

import config
import flask
import redis_utils

from flask import request, render_template, flash

app = flask.Flask(__name__)
app.config.from_mapping(config.app_config())


@app.route("/index")
def index_page():
    return render_template('base.html')


@app.route("/login", methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    title = 'Redis Login'

    if form.validate_on_submit():
        flash('Login requested for {}, remember me {}'.format(form.username.data, form.remember_me.data))

        return flask.redirect('/index')

    return render_template('login.html', title=title, form=form)


@app.route("/index/<user>")
# @require_auth()
def user_page():
    request_args = request.args.to_dict()
    response = redis_utils.hget(request_args['hash_name'], request_args['hash_key'])
    # import pdb;pdb.set_trace()
    return response['data'], response['status']


@app.route("/user/put")
# @require_auth()
def add_user():
    request_args = request.args.to_dict()
    response = redis_utils.hset(request_args['hash_name'], request_args['hash_key'], request_args['hash_value'])

    if response['data'] is bool:
        return flask.redirect(f'/index/<{request_args["hash_value"]}>'
                              f'?hash_name={request_args["hash_name"]}'
                              f'&hash_key={request_args["hash_key"]}',
                              response['status'])

    return response['data'], response['status']


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
