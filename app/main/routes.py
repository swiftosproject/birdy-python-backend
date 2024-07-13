from flask import jsonify, render_template, request, abort, current_app, send_from_directory
from flask_login import login_required, current_user
import json
import os
import re
from . import main
from ..models import User, Package
from .. import db
from .publish import publish

@main.route('/packages/<package_name>/<package_version>/<filename>', methods=['GET'])
def install_route(package_name, package_version, filename):
    if not current_app.config['ALLOW_INSTALLATION']:
        return 'Installation is not currently enabled on this server.', 403

    if not current_user.is_authenticated and current_app.config['REQUIRE_LOGIN_TO_INSTALL']:
        if not current_user.admin and current_app.config['REQUIRE_ADMIN_TO_INSTALL']:
            return current_app.login_manager.unauthorized()
        return current_app.login_manager.unauthorized()

    package_dir = os.path.join(current_app.root_path, 'packages', package_name, package_version)
    return send_from_directory(package_dir, filename)

@main.route('/packages/<package_name>/<package_version>.json', methods=['GET'])
def package_info_route(package_name, package_version):
    package = Package.query.filter_by(name=package_name, version=package_version).first()
    package_data = {
        "id": package.id,
        "name": package_name,
        "description": package.description,
        "version": package_version,
        "dependencies": package.dependencies,
        "files": package.files
    }

    return jsonify(package_data), 200

@main.route('/packages/<package_name>/latest.json', methods=['GET'])
def latest_package_info_route(package_name):
    package = Package.query.filter_by(name=package_name).order_by(Package.version.desc()).first()
    if package is None:
        return jsonify({"error": "Package not found"}), 404
    
    package_data = {
        "id": package.id,
        "name": package_name,
        "description": package.description,
        "version": package.version,
        "dependencies": package.dependencies,
        "files": package.files
    }
    
    return jsonify(package_data), 200

@main.route('/publish', methods=['POST'])
@login_required
def publish_route():
    return publish()

@main.route('/userinfo', methods=['GET'])
@login_required
def getownuserinfo():
    user_data = {
        "id": current_user.id,
        "username": current_user.username,
        "mail": current_user.mail
    }
    return jsonify(user_data), 200

@main.route('/userinfo', methods=['POST'])
def getuserinfo():
    data = request.get_json()
    id = data['id']
    user = User.query.filter_by(id=id).first()

    if not user:
        abort(404)

    user_data = {
        "id": user.id,
        "username": user.username,
        "mail": user.mail
    }

    return jsonify(user_data), 200
