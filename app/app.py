#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.

import flask
import app.auth_utils as auth_utils

from app.forms import *
from app.auth import require_auth
from app.config import get_app_conf, cache
from redis_utils import redis_utils as redis_utils
from flask import render_template, flash, session


app = flask.Flask(__name__)
app.config.update(get_app_conf())


@app.route("/temp")
def temp_route():
    return str(auth_utils.get_api_key('test_user'))


@app.route("/")
def index_page():
    try:
        if session['username']:
            return render_template('base_logged.html')

    except Exception as message:
        return render_template('base.html')


@app.route("/login", methods=['GET', 'POST'])
def login_form():
    form = LoginForm()
    title = 'Redis Login'
    try:
        if session['username']:
            return flask.redirect(f"/user/home_page")

    except Exception as message:
        pass

    if form.validate_on_submit():
        if auth_utils.check_password(form.username.data, form.password.data):
            session['username'] = form.username.data

            @cache.memorize()
            @cache.evict()
            def call_cache():
                return flask.redirect(f'/user/home_page')

            return call_cache()

        else:
            flash('Invalid username or password!')
            return render_template('login.html', title=title, form=form)

    return render_template('login.html', title=title, form=form)


@app.route("/logout")
@require_auth
@cache.release()
def logout():
    return flask.redirect(f'/')


@app.route("/register", methods=['GET', 'POST'])
@cache.evict()
def register():
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
            return render_template("register.html", title=title, form=form)

        status = auth_utils.append_json_to_file({form.username.data: {'attributes': user_data_dict}})

        if status:
            flask.flash("Successfully registered!")
            return flask.redirect(f'/login', 201)

    return render_template("register.html", title=title, form=form)


@app.route("/user/create", methods=['GET', 'POST'])
@cache.is_hit()
@cache.evict()
def create_user():
    form = CreateUserForm()
    title = "User creation panel."

    if form.validate_on_submit():
        user_data_dict = {
            'name': form.name.data,
            'email': form.email.data,
            'password': form.password.data,
            'group': form.group.data,
            'API_KEY': auth_utils.generate_api_key()
        }

        if auth_utils.append_json_to_file({form.username.data: {'attributes': user_data_dict}}):
            return flask.redirect(f'/user/home_page')

    return render_template("create_user.html", title=title, form=form)


@app.route("/user/update", methods=['GET', 'POST'])
@cache.is_hit()
def update_user():
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
                return render_template("update_base.html", title=title, form=form)

        register_data = {username: {'attributes': user_data_dict}}
        if auth_utils.del_json_from_file(username) and auth_utils.append_json_to_file(register_data):

            @cache.update(register_data)
            def call_cache():
                flask.flash("Successfully updated!")
                return flask.redirect(f'/user/home_page')
            call_cache()

        else:
            response = flask.make_response(flask.redirect('/', ), 404, )
            return response

    return render_template("update_base.html", title=title, form=form)


@app.route("/user/groups", methods=['GET', 'POST'])
def update_groups():

    return False


@app.route("/user/home_page")
@cache.is_hit()
@require_auth
def user_page():
    title = 'User Page'
    data = redis_utils.hget(session['username'], 'attributes')
    data = data['name']

    return render_template("user_home.html", title=title, name=data)


@app.route("/redis/clear")
def clear_redis():
    redis_utils.flushall()

    return "Memory has been cleared! \n Cron jobs have been stopped!"
