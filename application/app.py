#### IMPORTANT ####
# Yes, yes i know Redis should not be used to store persistent data.
# This program is made for the sole purpose of practicing Redis w/ python.

import flask
import application.auth_utils as auth_utils

from application.forms import *
from application.auth import require_auth, require_apikey, increment_limiter
from application.config import get_app_conf, cache
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
def index():
    title = 'Index'

    if auth_utils.is_logged():
        return render_template('base_logged.html', title=title)

    return render_template('base.html', title=title)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    title = 'Redis Login'
    response = flask.make_response()

    if auth_utils.is_logged():
        return flask.redirect(flask.url_for('user_page'))

    if form.validate_on_submit():
        if auth_utils.check_password(form.username.data, form.password.data):
            session['username'] = form.username.data

            @cache.memorize()
            @cache.evict()
            def call_cache():
                flask.flash("We are glad to see you again.")
                response.data = render_template('user_home.html', name=session['username'])
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
    flask.flash("Bye, it was nice seeing you!")
    return flask.redirect(flask.url_for('index'), 200)


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

        if auth_utils.append_json_to_file({form.username.data: {'attributes': user_data_dict}}):
            flask.flash("You have successfully registered!")

            return flask.redirect(flask.url_for('index', code=302))

    response.data = render_template("register.html", title=title, form=form)
    response.status_code = 200

    return response


@app.route("/user/create", methods=['GET', 'POST'])
@cache.is_hit()
@cache.evict()
def create_user():
    title = "User creation panel."
    username = session['username']
    auth_utils.check_group(session['username'])
    response = flask.make_response()
    form = CreateUserForm()

    if form.validate_on_submit():
        user_data_dict = {
            'nickname': form.name.data,
            'name': form.name.data,
            'email': form.email.data,
            'password': auth_utils.secure_key(form.password.data),
            'group': form.group.data,
            'API_KEY': auth_utils.generate_api_key()
        }

        if auth_utils.append_json_to_file({form.username.data: {'attributes': user_data_dict}}):
            flask.flash("User: {}, was successfully created".format)
            response.data = render_template('user_home.html', name=username)
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
    title = "User customization"
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
        # Change user info.
        if form.submit_info.data:
            user_data_dict = {
                'name': form.name.data,
                'email': form.email.data,
                'password': user_data[hash_field]['password'],
                'group': user_data[hash_field]['group'],
                'API_KEY': user_data[hash_field]['API_KEY']
            }

        # Change password.
        else:
            if not auth_utils.check_password(username, form.old_password.data):
                flask.flash("Incorrect password!")
                response.status_code = 400
                response.data = render_template('update_user.html', title=title, form=form)
                return response

            user_data_dict = {
                'name': user_data[hash_field]['name'],
                'email': user_data[hash_field]['email'],
                'password': auth_utils.secure_key(form.new_password.data),
                'group': user_data[hash_field]['group'],
                'API_KEY': user_data[hash_field]['API_KEY']
            }

        register_data = {username: {'attributes': user_data_dict}}

        if register_data == user_hash:
            flask.flash("Nothing to change...")
            response.status_code = 200
            response.data = render_template("update_user.html", title=title, form=form)
            return response

        if auth_utils.del_json_from_file(username) and auth_utils.append_json_to_file(register_data):

            @cache.update(register_data)
            def call_cache():
                flask.flash("Successfully updated!")
                response.data = render_template('user_home.html', name=form.name.data)
                response.headers['data_size'] = 0
                response.status_code = 201

                return response

            call_cache()

    response.data = render_template("update_user.html", title=title, form=form)
    response.status_code = 200

    return response


@app.route("/group", methods=['GET', 'POST'])
def update_groups():
    form = GroupForm()
    title = "Manage groups"
    auth_utils.check_group(session['username'])
    all_groups = auth_utils.get_group_info(all_groups=True)

    if form.validate_on_submit():
        group_name = flask.request.form.get("group_name")

        if form.submit_cancel.data:
            return render_template('update_groups.html', all_groups=all_groups, title=title, form=form)

        elif form.submit_edit.data:
            return render_template('update_groups.html', all_groups=all_groups, title=title, form=form)

        elif form.submit_new.data:
            return render_template('update_groups.html', all_groups=all_groups, title=title, form=form)

        elif form.submit_update.data:
            return render_template('update_groups.html', all_groups=all_groups, title=title, form=form)

        elif form.submit_delete.data:
            return render_template('update_groups.html', all_groups=all_groups, title=title, form=form)

        elif form.submit_add.data:
            flask.flash("Group created!")
            new_group = {form.new_type.data: {"requests": form.new_request_limit.data, "traffic": form.new_traffic_limit.data}}
            auth_utils.update_group(new_group=new_group)
            all_groups = auth_utils.get_group_info(all_groups=True)

            return render_template('update_groups.html', all_groups=all_groups, title=title, form=form)

    return render_template('update_groups.html', all_groups=all_groups, title=title, form=form)


@app.route("/user/delete", methods=['GET', 'POST'])
@cache.is_hit()
@require_auth
def del_user():
    form = DeleteForm()
    auth_utils.check_group(session['username'])
    all_users = auth_utils.get_json_from_file(all_items=True)
    response = flask.make_response()

    if form.validate_on_submit():
        if auth_utils.del_json_from_file(flask.request.form["dropdown"]):
            all_users = auth_utils.get_json_from_file(all_items=True)
            cache.rem_key(flask.request.form["dropdown"])
            flask.flash("User: {}, was successfully removed!".format(flask.request.form["dropdown"]))
            response.data = render_template('delete_user.html', all_users=all_users, form=form)
            response.headers['data_size'] = 50
            response.status_code = 202

            return response

        flask.flash("Something went wrong... please try again.")
        response.data = render_template('delete_user.html', all_users=all_users, form=form)
        response.headers['data_size'] = 0
        response.status_code = 500

        return response

    return render_template('delete_user.html', all_users=all_users, form=form)


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
    auth_utils.check_group(session['username'])
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
