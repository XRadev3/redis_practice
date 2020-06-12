#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.

import flask
import app.auth_utils as auth_utils

from app.forms import *
from app.auth import require_auth, require_apikey, increment_limiter
from app.config import get_app_conf, cache
from redis_utils import redis_utils as redis_utils
from flask import render_template, flash, session

app = flask.Flask(__name__)
app.config.update(get_app_conf())


@app.route("/ping")
@require_apikey
@cache.memorize()
def ping():
    response = flask.make_response('Just a test call', 200)
    response.headers['data_size'] = 50
    return response


@app.route("/")
def index_page():
    response = flask.make_response()
    try:
        if session['username']:
            response.headers['data_size'] = 0
            response.data = render_template('base_logged.html')
            return response

    except Exception as message:
        response.data = render_template('base.html')
        return response


@app.route("/login", methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    title = 'Redis Login'
    response = flask.make_response()
    try:
        if session['username']:
            response.data = flask.redirect('/user/home_page')
            response.status_code = 302

            return response

    except Exception as message:
        pass

    if form.validate_on_submit():
        if auth_utils.check_password(form.username.data, form.password.data):
            session['username'] = form.username.data

            @cache.memorize()
            @cache.evict()
            def call_cache():
                response.data = flask.redirect('/user/home_page')
                response.headers['data_size'] = 0
                response.status_code = 302

                return response

            return call_cache()

        else:
            flash('Invalid username or password!')
            response.data = render_template('login.html', title=title, form=form)
            response.headers['data_size'] = 0
            response.status_code = 400

            return response

    response.data = render_template('login.html', title=title, form=form)
    response.status_code = 200

    return response


@app.route("/logout")
@require_auth
@cache.release()
def logout():
    response = flask.make_response()
    response.data = flask.redirect('/')
    response.status_code = 200

    return response


@app.route("/register", methods=['GET', 'POST'])
def register():
    response = flask.make_response()
    form = RegisterForm()
    title = "Register"

    if form.validate_on_submit():
        user_data_dict = {
            'name': form.name.data,
            'email': form.email.data,
            'password': auth_utils.secure_key(form.password.data),
            'group': 'basic',
            'API_KEY': auth_utils.generate_api_key()
        }

        if auth_utils.get_json_from_file(form.username.data):
            flask.flash("This username already exits!")
            response.data = render_template("register.html", title=title, form=form)
            response.headers['data_size'] = 0
            response.status_code = 200
            return response

        status = auth_utils.append_json_to_file({form.username.data: {'attributes': user_data_dict}})

        if status:
            flask.flash("Successfully registered!")
            response.data = flask.redirect('/login', 201)
            response.headers['data_size'] = 0
            response.status_code = 200

            return response

    response.data = render_template("register.html", title=title, form=form)
    response.status_code = 200

    return response


@app.route("/user/create", methods=['GET', 'POST'])
@cache.is_hit()
@cache.evict()
def create_user():
    response = flask.make_response()
    form = CreateUserForm()
    title = "User creation panel."

    if form.validate_on_submit():
        user_data_dict = {
            'name': form.name.data,
            'email': form.email.data,
            'password': auth_utils.secure_key(form.password.data),
            'group': form.group.data,
            'API_KEY': auth_utils.generate_api_key()
        }

        if auth_utils.append_json_to_file({form.username.data: {'attributes': user_data_dict}}):
            response.data = flask.redirect('/user/home_page')
            response.headers['data_size'] = 100
            response.status_code = 201

            return response

    response.data = render_template("create_user.html", title=title, form=form)
    response.status_code = 200

    return response


@app.route("/user/update", methods=['GET', 'POST'])
@cache.is_hit()
@require_auth
def update_user():
    response = flask.make_response()
    form = UpdateForm()
    title = "User customization."
    username = session['username']
    hash_field = cache.item_hash_field
    user_hash = auth_utils.get_json_from_file(username)
    user_data = user_hash[username]

    if not form.validate_on_submit():

        # Username and group are not available for the user to change.
        form.username.data = username
        form.name.data = user_data[hash_field]['name']
        form.email.data = user_data[hash_field]['email']
        form.group.data = user_data[hash_field]['group']

    else:
        if form.submit_info.data:
            user_data_dict = {
                'name': form.name.data,
                'email': form.email.data,
                'password': user_data[hash_field]['password'],
                'group': user_data[hash_field]['group'],
                'API_KEY': user_data[hash_field]['API_KEY']
            }

        else:
            if auth_utils.check_password(username, form.old_password.data):
                user_data_dict = {
                    'name': user_data[hash_field]['name'],
                    'email': user_data[hash_field]['email'],
                    'password': auth_utils.secure_key(form.new_password.data),
                    'group': user_data[hash_field]['group'],
                    'API_KEY': user_data[hash_field]['API_KEY']
                }

            else:
                flask.flash("Wrong password!")
                response.data = render_template("update_base.html", title=title, form=form)
                response.headers['data_size'] = 0
                response.status_code = 200

                return response

        register_data = {username: {'attributes': user_data_dict}}
        if auth_utils.del_json_from_file(username) and auth_utils.append_json_to_file(register_data):

            @cache.update(register_data)
            def call_cache():
                flask.flash("Successfully updated!")
                response.data = flask.redirect('/user/home_page')
                response.headers['data_size'] = 0
                response.status_code = 201

                return response

            call_cache()

        else:
            response.data = flask.redirect('/')
            response.status_code = 401

            return response

    response.data = render_template("update_base.html", title=title, form=form)
    response.status_code = 200

    return response


@app.route("/user/groups", methods=['GET', 'POST'])
def update_groups():
    return False


@app.route("/user/home_page")
@cache.is_hit()
@require_auth
def user_page():
    response = flask.make_response()
    title = 'User Page'
    data = redis_utils.hget(session['username'], 'attributes')
    data = data['name']

    response.data = render_template('user_home.html', title=title, name=data)
    response.headers['data_size'] = 100
    response.status_code = 200

    return response


@app.route("/redis/clear")
def clear_redis():
    redis_utils.flushall()
    response = flask.make_response("Memory has been cleared!", 200)
    response.headers['data_size'] = 1000

    return response


@app.after_request
def after_each_request(response):
    try:
        if response.headers['data_size'] == 0:
            @require_auth
            def call_rate_limiter():
                return response

            call_rate_limiter()

        else:
            increment_limiter(response)

    except Exception as message:
        return response

    return response
