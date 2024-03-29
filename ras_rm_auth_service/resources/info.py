import json
import os

from flask import Blueprint, current_app, jsonify, make_response

info_view = Blueprint("info_view", __name__)


@info_view.route("/info", methods=["GET"])
def get_info():
    git_info = {}
    if os.path.exists("git_info"):
        with open("git_info") as io:
            git_info = json.loads(io.read())

    app_info = {
        "name": "ras-rm-auth-service",
        "version": current_app.config["VERSION"],
    }
    info = dict(git_info, **app_info)

    return make_response(jsonify(info), 200)
