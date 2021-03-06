#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.

import flask

from app import config
import app.cron_jobs as cron
from app.cache import Cache
from app.forms import *
from app.auth import require_auth
from redis_utils import redis_utils as redis_utils
from flask import request, render_template, flash, session

app = flask.Flask(__name__)
app.config.from_mapping(config.app_config())
cache = Cache()
#cron.job_clean_cache()


@app.route("/index")
def index_page():
    return render_template('base.html')


@app.route("/login", methods=['GET', 'POST'])
@cache.evict()
def login_form():
    form = LoginForm()
    title = 'Redis Login'
    try:
        if session['username']:
            return flask.redirect(f"/user/home_page?hash_name={session['username']}")

    except Exception as message:
        pass

    if form.validate_on_submit():
        username = form.username.data
        user = redis_utils.json_file_to_hash(username)

        if user and user[username]['attributes']['password'] == form.password.data:
            session['username'] = username

            @cache.memorize()
            def call_cache():
                return flask.redirect(f'/user/home_page?hash_name={username}')

            return call_cache()

        else:
            flash('Invalid username or password!')
            return flask.redirect('/login')

    return render_template('login.html', title=title, form=form)


@app.route("/logout")
@require_auth()
@cache.release()
def logout():
    return flask.redirect('/index')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    title = "Register"

    if form.validate_on_submit():
        user_data_dict = {
            'name': form.name.data,
            'email': form.email.data,
            'password': form.password.data,
            'group': 'basic'
        }

        if redis_utils.json_file_to_hash(form.username.data):
            flask.flash("This username already exits!")
            return render_template("register.html", title=title, form=form)

        status = redis_utils.json_to_file({form.username.data: {'attributes': user_data_dict}})

        if status:
            flask.flash("Successfully registered!")
            return flask.redirect('/login', 201)

    return render_template("register.html", title=title, form=form)


@app.route("/user/create", methods=['GET', 'POST'])
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
        status = redis_utils.json_to_file({form.username.data: {'attributes': user_data_dict}})

        if status:
            return flask.redirect(f'/user/home_page?hash_name={session["username"]}')

    return render_template("create_user.html", title=title, form=form)


@app.route("/user/update", methods=['GET', 'POST'])
@cache.evict()
@cache.update()
def update_user():
    form = UpdateForm()
    title = "User customization."
    username = session['username']
    hash_field = "attributes"
    user_hash = redis_utils.json_file_to_hash(username)
    user_data = user_hash[username]

    if not form.validate_on_submit():
        form.username.data = username
        form.name.data = user_data[hash_field]['name']
        form.email.data = user_data[hash_field]['email']
        form.password.data = user_data[hash_field]['password']
        form.group.data = user_data[hash_field]['group']

    else:
        user_data_dict = {
            'name': form.name.data,
            'email': form.email.data,
            'password': form.password.data,
            'group': user_data[hash_field]['group']
        }
        if redis_utils.remove_hash_file(username):
            status = redis_utils.json_to_file({username: {'attributes': user_data_dict}})

        else:
            flask.abort(404)

        if status:
            flask.flash("Successfully updated!")
            return flask.redirect(f'/user/home_page?hash_name={username}')

    return render_template("update_base.html", title=title, form=form)


@app.route("/user/home_page")
@require_auth()
@cache.is_hit()
def user_page():
    request_args = request.args.to_dict()
    title = 'User Page'
    response = redis_utils.hget(request_args['hash_name'], 'attributes')

    return render_template("user_home.html", title=title, name=str(response['data']))


@app.route("/redis/clear")
def clear_redis():
    redis_utils.flushall()
    #cron.cron_stop_job()

    return "Memory has been cleared! \n Cron jobs have been stopped!"

