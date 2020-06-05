#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.

import flask
import app.cron_jobs as cron

from app import config
from app.cache import Cache
from app.forms import *
from app.auth import require_auth, check_password
from redis_utils import redis_utils as redis_utils
from app import auth_utils
from flask import request, render_template, flash, session

app = flask.Flask(__name__)
app.config.from_mapping(config.app_config())
cache = Cache()
#cron.job_clean_cache()


@app.route("/temp")
def temp_route():
    return auth_utils.get_group_info(all_groups=True)


@app.route("/index")
def index_page():
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
        if check_password(form.username.data, form.password.data):
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
@require_auth()
@cache.release()
def logout():
    return flask.redirect('/index')


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
            'group': 'basic'
        }

        if auth_utils.get_json_from_file(form.username.data):
            flask.flash("This username already exits!")
            return render_template("register.html", title=title, form=form)

        status = auth_utils.append_json_to_file({form.username.data: {'attributes': user_data_dict}})

        if status:
            flask.flash("Successfully registered!")
            return flask.redirect('/login', 201)

    return render_template("register.html", title=title, form=form)


@app.route("/user/create", methods=['GET', 'POST'])
@cache.evict()
def create_user():
    form = CreateUserForm()
    title = "User creation panel."

    if form.validate_on_submit():
        user_data_dict = {
            'name': form.name.data,
            'email': form.email.data,
            'password': form.password.data,
            'group': form.group.data
        }

        if auth_utils.append_json_to_file({form.username.data: {'attributes': user_data_dict}}):
            return flask.redirect(f'/user/home_page')

    return render_template("create_user.html", title=title, form=form)


@app.route("/user/update", methods=['GET', 'POST'])
def update_user():
    form = UpdateForm()
    title = "User customization."
    username = session['username']
    hash_field = "attributes"
    user_hash = auth_utils.get_json_from_file(username)
    user_data = user_hash[username]

    if not form.validate_on_submit():

        # Username and group are not available for the user to change.
        form.username.data = username
        form.name.data = user_data[hash_field]['name']
        form.email.data = user_data[hash_field]['email']
        form.password.data = user_data[hash_field]['password']
        form.group.data = user_data[hash_field]['group']

    else:
        user_data_dict = {
            'name': form.name.data,
            'email': form.email.data,
            'password': auth_utils.secure_key(form.password.data),
            'group': user_data[hash_field]['group']
        }
        if auth_utils.del_json_from_file(username) and auth_utils.append_json_to_file({username: {'attributes': user_data_dict}}):
            @cache.update()
            def call_cache():
                flask.flash("Successfully updated!")
                return flask.redirect(f'/user/home_page')
            call_cache()

        else:
            flask.abort(404)

    return render_template("update_base.html", title=title, form=form)


@app.route("/user/groups", methods=['GET', 'POST'])
def update_groups():
    return False


@app.route("/user/home_page")
@cache.is_hit()
@require_auth()
def user_page():
    title = 'User Page'
    data = redis_utils.hget(session['username'], 'attributes')
    data = data['name']

    return render_template("user_home.html", title=title, name=data)


@app.route("/redis/clear")
def clear_redis():
    redis_utils.flushall()
    cron.cron_stop_job()

    return "Memory has been cleared! \n Cron jobs have been stopped!"

