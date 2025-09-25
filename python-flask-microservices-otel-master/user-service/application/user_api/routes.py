# application/user_api/routes.py
import logging
from flask import make_response, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from . import user_api_blueprint
from .. import db, login_manager
from ..models import User
from passlib.hash import sha256_crypt

# Logger setup (OTel auto-instrumentation will inject trace/span IDs automatically)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@login_manager.request_loader
def load_user_from_request(request):
    api_key = request.headers.get("Authorization")
    if api_key:
        api_key = api_key.replace("Basic ", "", 1)
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            logger.info("User loaded from API key", extra={"user_id": user.id})
            return user
    return None


@user_api_blueprint.route("/api/users", methods=["GET"])
def get_users():
    logger.info("Fetching all users")
    data = [row.to_json() for row in User.query.all()]
    return jsonify(data)


@user_api_blueprint.route("/api/user/create", methods=["POST"])
def post_register():
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    email = request.form["email"]
    username = request.form["username"]

    password = sha256_crypt.hash(str(request.form["password"]))

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
        username=username,
        authenticated=True,
    )

    db.session.add(user)
    db.session.commit()

    logger.info("New user registered", extra={"user_id": user.id, "username": user.username})
    return jsonify({"message": "User added", "result": user.to_json()})


@user_api_blueprint.route("/api/user/login", methods=["POST"])
def post_login():
    username = request.form["username"]
    user = User.query.filter_by(username=username).first()

    if user and sha256_crypt.verify(str(request.form["password"]), user.password):
        user.encode_api_key()
        db.session.commit()
        login_user(user)
        logger.info("User logged in", extra={"user_id": user.id, "username": user.username})
        return make_response(jsonify({"message": "Logged in", "api_key": user.api_key}))

    logger.warning("Failed login attempt", extra={"username": username})
    return make_response(jsonify({"message": "Not logged in"}), 401)


@user_api_blueprint.route("/api/user/logout", methods=["POST"])
def post_logout():
    if current_user.is_authenticated:
        logger.info("User logged out", extra={"user_id": current_user.id})
        logout_user()
        return make_response(jsonify({"message": "You are logged out"}))

    logger.warning("Logout attempted without being logged in")
    return make_response(jsonify({"message": "You are not logged in"}))


@user_api_blueprint.route("/api/user/<username>/exists", methods=["GET"])
def get_username(username):
    item = User.query.filter_by(username=username).first()
    if item:
        logger.info("Username exists", extra={"username": username})
        return jsonify({"result": True})
    else:
        logger.warning("Username not found", extra={"username": username})
        return jsonify({"message": "Cannot find username"}), 404


@login_required
@user_api_blueprint.route("/api/user", methods=["GET"])
def get_user():
    if current_user.is_authenticated:
        logger.info("Fetched current user", extra={"user_id": current_user.id})
        return make_response(jsonify({"result": current_user.to_json()}))

    logger.warning("Tried to fetch user while not logged in")
    return make_response(jsonify({"message": "Not logged in"})), 401
